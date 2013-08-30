from django.contrib.auth.models import Group
from django.conf import settings
from courseaffils.models import Course
from mediathread.user_accounts.models import RegistrationModel


class CallToActionMiddleware(object):
    def process_request(self, request):
        if not request.is_ajax() and request.user.is_authenticated():
            # check if professor is only in faculty group of sample course or in no course at all
            registration_model_exists = RegistrationModel.objects.filter(user=request.user).exists()
            sample_course_faculty_group_id = Course.objects.get(id=settings.SAMPLE_COURSE_ID).faculty_group_id
            created_courses = Group.objects.exclude(
                id=sample_course_faculty_group_id).filter(user=request.user, name__startswith="faculty_").exists()

            if registration_model_exists and not created_courses:
                request.no_courses_created = True
            else:
                # check how many students are in the currently active course (created by them)
                if request.course and request.course.id != settings.SAMPLE_COURSE_ID and\
                        request.course.is_faculty(request.user):
                    student_count = len(request.course.students)
                    if student_count == 0:
                        request.no_students = True

        return None
