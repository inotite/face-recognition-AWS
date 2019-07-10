from django.conf.urls import url
from . import views
from client.views import sync_again

urlpatterns = [
    url(r'^$', views.index, name="athlete-index"),
    # url(r'create/',views.create,name='create'),
    url(r'(?P<pk>\d+)/update/', views.update, name='update-athlete'),
    url(r'(?P<pk>\d+)/delete', views.delete, name='delete-athlete'),
    url(r'(?P<pk>\d+)/user_gallery', views.athlete_gallery, name='user_gallery'),
    url(r'(?P<pk>\d+)/stats', views.stats, name='stats'),
    url(r'(?P<pk>\d+)/event', views.get_participentes, name='participants'),
    url(r'(?P<pk>\d+)/get-task', views.get_task_status, name='get-task'),
    url(r'(?P<pk>\d+)/reprocess', sync_again, name='reprocess'),
    url(r'export', views.export_data, name='export'),
    url(r'import', views.import_data, name='import'),
    url(r'profile', views.profile_update, name='profile'),
    url(r'participated-projects', views.participated, name='participated'),
]
