from django.conf.urls import include, patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'create/$', course_create, name='course_create'),
    url(r'member-list/$', member_list, name='member_list'),
)
