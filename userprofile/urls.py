from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    # url(r'login/$', auth_views.login, {'template_name': 'userprofile/login.html'}, name='login'),
    url(r'login/$', views.login_auth, name='login'),
    url(r'signup/$', views.signup, name='signup'),
    url(r'logout/$', auth_views.logout, {'next_page': views.login_auth}, name='logout'),
    url(r'^password/$', views.change_password, name='change_password'),
    url(r'^reset-password/$', views.forgot_password, name='reset-password')

]
