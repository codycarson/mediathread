import simplejson
from random import choice
from string import letters

from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from djangohelpers.lib import allow_http

from discussions.views import threaded_comment_json
from courseaffils.lib import in_course_or_404, in_course, get_public_name
from projects.forms import ProjectForm
from projects.lib import composition_project_json

Project = get_model('projects','project')
ProjectVersion = get_model('projects','projectversion')

@allow_http("POST")
def project_create(request):
    if request.method != "POST":
        return HttpResponseForbidden("forbidden")

    user = request.user
    course = request.course 
    in_course_or_404(user, course)
    is_faculty = course.is_faculty(user),
    
    project = Project(author=user, course=course, title="Untitled")
    project.save()

    project.collaboration(request, sync_group=True)

    parent = request.POST.get("parent")
    if parent is not None:
        try:
            parent = Project.objects.get(pk=parent)
            
            parent_collab = parent.collaboration(request)
            if parent_collab.permission_to("add_child", request):
                parent_collab.append_child(project)

        except Project.DoesNotExist:
            parent = None
            # @todo -- an error has occurred
            
    if not request.is_ajax():
        return HttpResponseRedirect(project.get_absolute_url())
    else: 
        project_context = composition_project_json(request, project, project.can_edit(request))    
        project_context['editing'] = True
        
        data = { 'panel_state': 'open', 
                 'template': 'project',
                 'context': project_context 
        }
                
        return HttpResponse(simplejson.dumps(data, indent=2), mimetype='application/json')

@allow_http("POST")
def project_save(request, project_id):
    project = get_object_or_404(Project, pk=project_id, course=request.course)

    if not project.can_edit(request) or not request.method == "POST":
        return HttpResponseRedirect(project.get_absolute_url())

    space_owner = in_course_or_404(project.author.username, request.course)

    if request.method == "POST":
        projectform = ProjectForm(request, instance=project, data=request.POST)
        if projectform.is_valid():

            #legacy and for optimizing queries
            projectform.instance.submitted = (request.POST.get('publish',None) != 'PrivateEditorsAreOwners')
            
            #this changes for version-tracking purposes
            projectform.instance.author = request.user
            projectform.save()

            projectform.instance.collaboration(request, sync_group=True)

            if request.META.get('HTTP_ACCEPT','').find('json') >=0:
                v_num = projectform.instance.get_latest_version()
                return HttpResponse(simplejson.dumps(
                    { 'status':'success',
                      'is_assignment': projectform.instance.is_assignment(request),
                      'revision': {
                          'id': v_num,
                          'public_url': projectform.instance.public_url(),
                          'visibility': project.visibility_short()
                       }
                    }, indent=2),
                    mimetype='application/json')

        redirect_to = '.'
        return HttpResponseRedirect(redirect_to)
    

@allow_http("POST")
def project_delete(request, project_id):
    """
    Delete the requested project. Regular access conventions apply. 
    If the logged-in user is not allowed to delete the project, an HttpResponseForbidden
    will be returned
    """
    project = get_object_or_404(Project, pk=project_id, course=request.course)
    
    if not project.can_edit(request) or not request.method == "POST":
        return HttpResponseForbidden("forbidden")

    project.delete()
    return HttpResponseRedirect('/')

@allow_http("GET")
def project_view_readonly(request, project_id, version_number=None):
    """
    A single panel read-only view of the specified project/version combination.
    No assignment, response or feedback access/links.
    Regular access conventions apply. For example, if the project is "private"
    an HTTPResponseForbidden will be returned.
    
    Used for reviewing old project versions and public project access.
    
    Keyword arguments:
    project_id -- the model id
    version_number -- a specific project version or None for the current version 
    
    """
    
    project = get_object_or_404(Project, pk = project_id)
    
    if not project.can_read(request):
        return HttpResponseForbidden("forbidden")
    
    data = { 'space_owner' : request.user.username }
    
    course = request.course
    if not course:
        # public view
        course = request.collaboration_context.content_object
        public_url = project.public_url()
    else:
        # versioned view
        public_url = reverse('project-view-readonly', kwargs = { 'project_id': project.id, 'version_number': version_number})
        
    if not request.is_ajax():
        data['project'] = project
        data['version'] = version_number
        data['public_url'] = public_url
        return render_to_response('projects/project.html', data, context_instance=RequestContext(request))
    else:
        
        if version_number:
            version = get_object_or_404(ProjectVersion,
                                        versioned_id = project_id,
                                        version_number=version_number)
            
            project = version.instance()
        
        panels = []
            
        # Requested project, either assignment or composition
        project_context = composition_project_json(request, project, False, version_number)
        panel = { 'panel_state': 'open', 'panel_state_label': "Version View", 'context': project_context, 'template': 'project' }
        panels.append(panel)
        
        data['panels'] = panels
        
        return HttpResponse(simplejson.dumps(data, indent=2), mimetype='application/json')
      
@allow_http("GET")
def project_workspace(request, project_id, feedback=None):
    """
    A multi-panel editable view for the specified project
    Legacy note: Ideally, this function would be named project_view but
    StructuredCollaboration requires the view name to be  <class>-view to do a reverse        
    
    Panel 1: Parent Assignment (if applicable)
    Panel 2: Project
    Panel 3: Instructor Feedback (if applicable & exists) 
    
    Keyword arguments:
    project_id -- the model id
    
    """    
    project = get_object_or_404(Project, pk=project_id)
    
    if not project.can_read(request):
        return HttpResponseForbidden("forbidden")
    
    show_feedback = feedback == "feedback"
    course = request.course
    is_faculty = course.is_faculty(request.user)
    data = { 'space_owner' : request.user.username, 'show_feedback': show_feedback }
    
    if not request.is_ajax():
        data['project'] = project
        return render_to_response('projects/project.html', data, context_instance=RequestContext(request))
    else:
        panels = []
        
        is_assignment = project.is_assignment(request)
        can_edit = project.can_edit(request)
        feedback_discussion = project.feedback_discussion() if is_faculty or can_edit else None
    
        # Project Parent (assignment) if exists
        parent_assignment = project.assignment()
        if parent_assignment:
            assignment_context = composition_project_json(request, parent_assignment, parent_assignment.can_edit(request))
            assignment_context['create_selection'] = True
            panel = { 'is_faculty': is_faculty, 'panel_state': 'closed' if show_feedback else 'open', 'subpanel_state': 'closed', 'context': assignment_context, 'template': 'project' }
            panels.append(panel)
                    
        # Requested project, can be either an assignment or composition
        project_context = composition_project_json(request, project, can_edit)
        project_context['editing'] =  True if can_edit and len(project.body) < 1 else False # only editing if it's new
        project_context['create_instructor_feedback'] = is_faculty and parent_assignment and not feedback_discussion
        panel = { 'is_faculty': is_faculty, 'panel_state': 'closed' if show_feedback else 'open', 'context': project_context, 'template': 'project' }
        panels.append(panel)
        
        # Project Response -- if the requested project is an assignment
        # This is primarily a student view. The student's response should 
        # pop up automatically when the parent assignment is viewed.
        if is_assignment:
            responses = project.responses_by(request, request.user)
            if len(responses) > 0:
                response = responses[0]
                response_can_edit = response.can_edit(request)
                response_context = composition_project_json(request, response, response_can_edit)
                
                panel = { 'is_faculty': is_faculty, 'panel_state': 'closed', 'context': response_context, 'template': 'project' }
                panels.append(panel)
                
                if not feedback_discussion and response_can_edit:
                    feedback_discussion = response.feedback_discussion()
            
        data['panels'] = panels
        
        # If feedback exists for the requested project
        if feedback_discussion:
            # 3rd pane is the instructor feedback, if it exists
            panel = { 'panel_state': 'open' if show_feedback else 'closed',
                      'panel_state_label': "Instructor Feedback",
                      'template': 'discussion',
                      'context': threaded_comment_json(feedback_discussion, request.user)
                    }
            panels.append(panel)
            
        # Create a place for asset editing
        panel = { 'panel_state': 'closed',
                  'panel_state_label': "Item Details",
                  'template': 'asset_quick_edit',
                  'update_history': False,
                  'show_colleciton': False,
                  'context': { 'type': 'asset' }
                }
        panels.append(panel)    
            
        return HttpResponse(simplejson.dumps(data, indent=2), mimetype='application/json')
    

