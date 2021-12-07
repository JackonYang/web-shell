# -*- coding: utf-8 -*-
import logging
import copy
import json
import os

# from rest_framework.decorators import api_view
# from rest_framework.response import Response

from django.template.response import TemplateResponse
from django.shortcuts import redirect

from utils.shell_runner import get_cmd_stdout

from proj_configs import DATA_DUMP_DIR


logger = logging.getLogger(__name__)

cmd_history = []
cmd_details = {}
global_vars = {
    'cmd_id': 0,
    'cmd_tmpl_id': 0,
    'tmpl_name2id': {},
    'tmpls_meta': {
        'version': 0,
    }
}
cmd_tmpls = {}

shell_args_data = {
    'cmd_dir': {
        'name': 'cmd_dir',
        'value': '/mnt/data/jkyang',
        'help': '',
    },
    'cmd': {
        'name': 'cmd',
        'value': '',
        'help': '',
    },
    'template_name': {
        'name': 'cmd_tmpl_name',
        'value': '',
        'help': '',
    },
    'output': {
        'name': 'output',
        'value': '',
        'help': 'hide',
    },
}

shell_args_order = [
    'cmd_dir',
    'cmd',
    'template_name',
]


def load_dumps():
    global global_vars, cmd_tmpls

    if not os.path.exists(DATA_DUMP_DIR):
        return

    versions = sorted(os.listdir(DATA_DUMP_DIR))
    if len(versions) < 1:
        return

    version_dir = os.path.join(DATA_DUMP_DIR, versions[-1])

    with open(os.path.join(version_dir, 'global_vars.json'), 'r') as fr:
        global_vars = json.load(fr)

    with open(os.path.join(version_dir, 'cmd_tmpls.json'), 'r') as fr:
        cmd_tmpls = json.load(fr)


load_dumps()
# print(json.dumps(global_vars, indent=4))
# print(json.dumps(cmd_tmpls, indent=4))


def shell_home(request,
               template_name='shell-home.html'):

    context = {
        'shell_args': [copy.copy(shell_args_data[i]) for i in shell_args_order],
        'shell_output': shell_args_data['output']['value'],
        'cmds': [copy.copy(cmd_details[i]) for i in cmd_history],
        'cmd_tmpls': list(cmd_tmpls.values()),
    }

    return TemplateResponse(request, template_name, context)


def load_tmpl(request, tmpl_id):
    tmpl_id = str(tmpl_id)
    if tmpl_id in cmd_tmpls:
        tmpl = cmd_tmpls[tmpl_id]
        shell_args_data['cmd_dir']['value'] = tmpl['cmd_dir']
        shell_args_data['cmd']['value'] = tmpl['cmd']
        shell_args_data['output']['value'] = ''

    return redirect('shell_home')


def on_tmpls_updated():
    global_vars['tmpls_meta']['version'] += 1

    verion_id = global_vars['tmpls_meta']['version']

    version_dir = os.path.join(DATA_DUMP_DIR, 'version-%06d' % verion_id)
    os.makedirs(version_dir)

    with open(os.path.join(version_dir, 'global_vars.json'), 'w') as fw:
        json.dump(global_vars, fw, indent=4)

    with open(os.path.join(version_dir, 'cmd_tmpls.json'), 'w') as fw:
        json.dump(cmd_tmpls, fw, indent=4)


def gen_cmd_id():
    global_vars['cmd_id'] += 1
    return global_vars['cmd_id']


def gen_cmd_tmpl_id(cmd_tmpl_name):
    if cmd_tmpl_name in global_vars['tmpl_name2id']:
        return global_vars['tmpl_name2id'][cmd_tmpl_name]

    global_vars['cmd_tmpl_id'] += 1

    tid = str(global_vars['cmd_tmpl_id'])
    global_vars['tmpl_name2id'][cmd_tmpl_name] = tid
    return tid


def brief_output(cmd_id, output):
    lines = output.split('\n')
    brief = '<br/>'.join(lines[:3])
    if len(lines) > 3:
        brief += '... <a href="/webshell/cmds/%s"> read more </a>' % cmd_id

    return brief


def shell_run(request):
    if request.method != 'POST':
        pass

    qd = request.POST
    cmd = qd['cmd']
    cmd_dir = qd['cmd_dir']

    is_save_template = qd.get('is_save_template')
    if is_save_template and is_save_template == 'true':
        cmd_tmpl_name = qd['cmd_tmpl_name']
        key = gen_cmd_tmpl_id(cmd_tmpl_name)
        cmd_tmpls[key] = {
            'key': key,
            'name': cmd_tmpl_name,
            'cmd': cmd,
            'cmd_dir': cmd_dir,
        }
        on_tmpls_updated()

    shell_args_data['cmd_dir']['value'] = cmd_dir
    shell_args_data['cmd']['value'] = cmd

    cmd_id = gen_cmd_id()
    output = get_cmd_stdout(cmd, check=False, cmd_dir=cmd_dir)

    shell_args_data['output']['value'] = output

    cmd_details[cmd_id] = {
        'cmd': cmd,
        'cmd_args': copy.deepcopy(qd),
        'output_brief': brief_output(cmd_id, output),
        'output_raw': output,
        'output': output.replace('\n', '<br/>'),
        'notes': '',
        'mark': '',
    }

    cmd_history.append(cmd_id)

    return redirect('shell_home')


def cmd_detail(request, cmd_id,
               template_name='cmd-detail.html'):
    context = {
        'cmd': cmd_details[cmd_id],
    }

    return TemplateResponse(request, template_name, context)
