from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.home),
    url('^params/', views.getparm),
    url('^run_time/', views.run_time),
]