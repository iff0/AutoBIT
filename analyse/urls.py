from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.home),
    url('^params/', views.getparm),
    url('^s_layers_num/', views.s_layers_num),
    url('^s_layers_size/', views.s_layers_size),
    url('^run_time/', views.run_time),
]