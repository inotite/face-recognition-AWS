from django.contrib import admin
# from django.urls import path
from django.conf.urls import url, include
from . import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from client.views import *

urlpatterns = [
    # path('admin/', admin.site.urls),
    url(r'admin/', include(admin.site.urls)),
    url(r'^', include('userprofile.urls')),
    url(r'events/', include('events.urls')),
    url(r'users/', include('athletes.urls')),
    url(r'client/', include('client.urls')),
    url(r'projects/(?P<pk>\d+)/join', join_project, name='join-project'),

]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
