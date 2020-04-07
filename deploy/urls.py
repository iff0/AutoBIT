from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.home),
    url('^set_platform/', views.set_platform),
    url('^get_target_file/', views.get_target_file),
    url('^get_basic_info/', views.get_basic_info),
    url('^test/', views.CreateTask),
]