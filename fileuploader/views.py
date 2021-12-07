# -*- coding: utf-8 -*-
import logging
import os

# from rest_framework.decorators import api_view
# from rest_framework.response import Response

from django.template.response import TemplateResponse
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

global_vars = {
    'upload_to': '',
}


def home(request,
         template_name='fileuploader-home.html'):

    context = {
        'upload_to': global_vars['upload_to'],
    }

    return TemplateResponse(request, template_name, context)


def handle_uploaded_file(f, upload_to):
    filepath = os.path.join(upload_to, f.name)
    print(filepath)

    with open(filepath, 'wb') as fw:
        for chunk in f.chunks():
            fw.write(chunk)


def run(request):
    if request.method != 'POST':
        pass

    qd = request.POST

    upload_to = qd['upload_to']
    global_vars['upload_to'] = upload_to

    handle_uploaded_file(request.FILES['myfile'], upload_to)

    return redirect('fileuploader_home')
