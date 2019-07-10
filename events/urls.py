from django.conf.urls import url, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r's3Images', views.ImagesViewset)

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'create/$', views.create, name='create'),
    url(r'(?P<pk>\d+)/delete', views.delete, name='delete'),
    # url(r'(?P<pk>\d+)/scan_event',views.scan_event,name='scan_event'),
    url(r'(?P<pk>\d+)/rescan_event', views.rescan, name='rescan_event'),
    url(r'(?P<pk>\d+)/dropbox_to_s3', views.dropbox_to_s3, name='dropbox_to_s3'),
    url(r'(?P<pk>\d+)/event_gallary', views.event_gallary, name='event_gallary'),
    url(r'(?P<pk>\d+)/gallery', views.gallary, name='gallery'),
    url(r'(?P<pk>\d+)/stats', views.stats, name='stats'),
    url(r'(?P<pk>\d+)/attach_dropbox', views.attach_dropbox, name='attach_dropbox'),
    url(r'get_csv', views.getcsv, name='get_csv'),
    url(r'(?P<pk>\d+)/Tags', views.Tags, name='Tags'),
    url(r'(?P<event>\d+)/remove_unmach/(?P<pk>\d+)', views.delete_unmach, name='remove_unmach'),
    url('^api/(?P<pk>\d+)/', include(router.urls)),
    url(r'datatable/(?P<pk>\d+)', views.dataTable, name='dataTable'),
    url(r'getathletes/(?P<pk>\d+)', views.getAthletes, name='getAthletes')
]
