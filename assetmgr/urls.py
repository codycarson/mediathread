from django.conf.urls.defaults import *
from django.conf import settings
import os.path

media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns(
    'assetmgr.views',

    url(r'^$', 
        'asset_workspace',
        name='asset-collection-view'),
                       
    url(r'^(?P<asset_id>\d+)/$', 
        'asset_workspace', 
        name="asset-view"),
                       
    url(r'^(?P<asset_id>\d+)/annotations/(?P<annot_id>\d+)/$',
        'asset_workspace',
        name='annotation-view'),
    
    url(r'^json/(?P<asset_id>\d+)/$', 
        'asset_json', 
        name="asset-json"),
    
    url(r'^create/(?P<asset_id>\d+)/annotations/$',
        'annotation_create'),

    url(r'^save/(?P<asset_id>\d+)/annotations/(?P<annot_id>\d+)/$',
        'annotation_save',
        name="annotation-save"),
                       
    url(r'^delete/(?P<asset_id>\d+)/annotations/(?P<annot_id>\d+)/$',
        'annotation_delete',
        name="annotation-delete"),
    
    url(r'^xmeml/(?P<asset_id>\w+)/$', 'final_cut_pro_xml', name="final_cut_pro_xml"),


    # Candidates for deprecation
    url(r'^old/(?P<asset_id>\d+)/$', 
        'old_asset_workspace', 
        name="old-asset-view"),
                       
    url(r'^old/(?P<asset_id>\d+)/annotations/(?P<annot_id>\d+)/$',
        'annotationview',
        name="annotation-form"),
)

