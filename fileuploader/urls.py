# -*- coding: utf-8 -*-
from django.urls import re_path
# from django.urls import path

from . import views

urlpatterns = [
    re_path(r'^$', views.home, name='fileuploader_home'),
    re_path(r'^run$', views.run, name='fileuploader_run'),
]
