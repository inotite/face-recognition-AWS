from .views import *
from django.conf.urls import url, include

urlpatterns = [
    url(r'index/', index, name='client-index'),
    url(r'privacy-policy/', privacy, name='privacy-policy'),
    url(r'terms-and-conditions/', terms, name='terms-and-conditions'),
    url(r'projects/(?P<pk>\d+)', projects, name='projects'),
    url(r'All/', client_projects, name='all'),
    url(r'create-project/', create_project, name='client-project-create'),
]
