"""newdj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url
from guide.views import test, home

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', home),
    url(r'^guide/', include('guide.urls')),
    url(r'^deploy/', include('deploy.urls')),
    url(r'^analyse/', include('analyse.urls')),
    url(r'^test/', test),
]
urlpatterns += staticfiles_urlpatterns()
