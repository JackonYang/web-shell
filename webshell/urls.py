# -*- coding: utf-8 -*-
from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.shell_home, name='shell_home'),
    re_path(r'^run$', views.shell_run, name='shell_run'),
    path(r'cmds/<int:cmd_id>', views.cmd_detail, name='cmd_detail'),
    path(r'load-tmpl/<int:tmpl_id>', views.load_tmpl, name='load_tmpl'),
]
