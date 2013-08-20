from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth import admin as group_admin

from mediathread.main.models import UserSetting


class GroupTypeException(Exception):
    pass


class UserSettingAdmin(admin.ModelAdmin):
    class Meta:
        model = UserSetting

    list_display = ("user", "name", "value")

admin.site.register(UserSetting, UserSettingAdmin)


class CustomizedGroupAdminModel(group_admin.GroupAdmin):
    list_display = ('group_descriptive_name',)
    search_fields = ['course__title', 'name']

    def group_descriptive_name(self, obj):
        course_type = obj.name.split('_')[0]

        # get the course obj
        if course_type == 'faculty':
            """
            Faculty Group handle
            """
            course = obj.faculty_of.get()
        elif course_type == 'member' or course_type == 'student':
            """
            Member Group handle
            """
            # fixed the title if it's not 'member' but 'student'
            if course_type == 'student':
                obj.name = obj.name.replace('student', 'member')
                obj.save()
            course = obj.course
        else:
            raise GroupTypeException("Group type must be either 'faculty' or 'member'.")

        return "%s: %s Group" % (course.title, course_type.capitalize())
    group_descriptive_name.short_description = 'Group Name'

admin.site.unregister(Group)
admin.site.register(Group, admin_class=CustomizedGroupAdminModel)
