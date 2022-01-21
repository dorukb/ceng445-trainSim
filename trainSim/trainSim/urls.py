"""trainSim URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path,include,re_path
from trainSim import views





urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index),
    re_path('createGrid/', views.createGrid),
    re_path('create/', views.create),
    # re_path('attach/(?P<gridname>[aA-zZ]+)?', views.attach),
    re_path('attach/(?P<gridname>[a-zA-Z0-9_]+)?', views.attach),
    re_path('detach/(?P<gridname>[a-zA-Z0-9_]+)?', views.detach),
    re_path('delete/(?P<gridname>[a-zA-Z0-9_]+)?', views.delete),

    re_path('share/(?P<gridname>[a-zA-Z0-9_]+)?', views.share),
    re_path('hatice/(?P<gridname>[a-zA-Z0-9_]+)?', views.hatice),

    re_path('edit/(?P<gridname>[a-zA-Z0-9_]+)?', views.edit),
    re_path('commands/', views.commands),
    re_path('sim/(?P<gridname>[a-zA-Z0-9_]+)?', views.gosim),


]
