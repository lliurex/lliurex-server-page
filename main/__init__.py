from flask import Blueprint, render_template, abort, request, send_from_directory,url_for
from jinja2 import TemplateNotFound
from ainur.utils import validate_groups
from flask_login import login_required

from os.path import join as os_path_join, basename
from json import load as json_load
from glob import glob
from codecs import open as codecs_open

exportmodule = Blueprint('mainmodule', __name__,template_folder='templates',static_folder='static')

BASE_PATH = '/usr/share/lliurex-www/srv/'
LINKS_PATH = os_path_join(BASE_PATH,'links')
OVERRIDE_PATH = '/var/lib/lliurex-www'
OVERRIDE_LINKS_PATH = os_path_join(OVERRIDE_PATH,'links')
ICONS_PATH = os_path_join(BASE_PATH,'icons')

def main():
    resources = get_resources()
    return render_template('main/main.html', resources=resources)

def get_resources():
    links = {}
    for link in glob(os_path_join(LINKS_PATH,'*.json')):
        with codecs_open(link,encoding='utf-8') as fd:
            links[basename(link)] = json_load(fd)
    
    for link in glob(os_path_join(OVERRIDE_LINKS_PATH,'*.json')):
        with codecs_open(link,encoding='utf-8') as fd:
            basename_link = basename(link)
            metadata = json_load(fd)
            if basename_link in links:
                links[basename_link] = {**links[basename_link], **metadata}
            else:
                links[basename_link] = metadata

    return sorted(links.values(), key=lambda x: x['order'] if 'order' in x else 999)

@exportmodule.route('/icons/<path:path>')
def icons(path):
    return send_from_directory(ICONS_PATH, path)