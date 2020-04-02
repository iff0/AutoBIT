from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^upload/', views.upload_model),
    url(r'^structure_view/', views.structure_view),
]