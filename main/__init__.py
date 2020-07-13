from flask import Blueprint, render_template, send_from_directory,url_for, jsonify
from flask_login import login_required

from os.path import join as os_path_join, basename, exists as os_path_exists
from json import load as json_load
from glob import glob
from codecs import open as codecs_open

from feedparser import parse as f_parse
from email.utils import parsedate_to_datetime

from ainur.utils import validate_groups, get_current_user_groups
from ainur import app

exportmodule = Blueprint('mainmodule', __name__,template_folder='templates',static_folder='static')

BASE_PATH = '/usr/share/lliurex-www/srv/'
LINKS_PATH = os_path_join(BASE_PATH,'links')
OVERRIDE_PATH = '/var/lib/lliurex-www'
FEED_PATH = os_path_join(BASE_PATH,'feed_list')
OVERRIDE_LINKS_PATH = os_path_join(OVERRIDE_PATH,'links')
ICONS_PATH = os_path_join(BASE_PATH,'icons')

def main():
    resources = get_resources()
    with codecs_open('/etc/hostname',encoding='utf-8') as fd:
        servername = fd.readline().strip() 
    list_menu = get_menu_list()
    return render_template('main/main.html', resources=resources, servername=servername, list_menu=list_menu)


def get_menu_list(selected=None):
    user_groups = get_current_user_groups()
    result = []
    for x in app.menu_list['adminmodules']:
        if len(set(x['permissions']) & set(user_groups)) > 0 :
            result.append(x)
    if selected is not None:
        for x in result:
            if 'link' in x :
                if x['link'] == selected:
                    x['selected'] = True
                else:
                    x['selected'] = False
    print(result)
    return result



def get_resource(aux_filename):
    result = {}
    filename = basename(aux_filename)
    link = os_path_join(LINKS_PATH,filename)
    if os_path_exists(link):
        with codecs_open(link,encoding='utf-8') as fd:
            result = json_load(fd)
            result['editable'] = False
            
    link = os_path_join(OVERRIDE_LINKS_PATH,filename)
    if os_path_exists(link):
        with codecs_open(link,encoding='utf-8') as fd:
            metadata = json_load(fd)
            result = {**result, **metadata }
    if len(result.items()) == 0:
        return None
    
    result['filename'] = filename
    if 'editable' not in result:
        result['editable'] = True
    if 'visibility' not in result:
        result['visibility'] = True
    return result

# def get_resources():
#     links = {}
#     for link in glob(os_path_join(LINKS_PATH,'*.json')):
#         with codecs_open(link,encoding='utf-8') as fd:
#             links[basename(link)] = json_load(fd)
#             links[basename(link)]['filename'] = basename(link)
#             links[basename(link)]['editable'] = False
#             if 'visibility' not in links[basename(link)]:
#                 links[basename(link)]['visibility'] = True
#             if not links[basename(link)]['icon'].startswith('http'):
#                 links[basename(link)]['icon'] = url_for('mainmodule.icons',path=links[basename(link)]['icon'])

    
#     for link in glob(os_path_join(OVERRIDE_LINKS_PATH,'*.json')):
#         with codecs_open(link,encoding='utf-8') as fd:
#             basename_link = basename(link)
#             metadata = json_load(fd)
#             if basename_link in links:
#                 links[basename_link] = {**links[basename_link], **metadata}
#             else:
#                 links[basename_link] = metadata
#                 links[basename_link]['editable'] = True
#             links[basename(link)]['filename'] = basename(link)
#     return sorted(links.values(), key=lambda x: x['order'] if 'order' in x else 999)

def get_resources():
    files_to_process = []
    processed_files = []
    for link in glob(os_path_join(LINKS_PATH,'*.json')):
        files_to_process.append(basename(link))

    for link in glob(os_path_join(OVERRIDE_LINKS_PATH,'*.json')):
        files_to_process.append(basename(link))

    for link in list(set(files_to_process)):
        processed_file = get_resource(link)
        if processed_file is not None:
            processed_files.append(processed_file)

    return sorted(processed_files, key=lambda x: x['order'] if 'order' in x else 999)


@exportmodule.route('/rss')
def get_news():
    override_list_feeds = os_path_join(OVERRIDE_PATH,'feed_list')
    list_feeds = []

    if os_path_exists(override_list_feeds):
        with codecs_open(override_list_feeds,encoding='utf-8') as fd:
            list_feeds = [ x.strip() for x in fd.readlines() ]
    elif os_path_join(FEED_PATH):
        with codecs_open(FEED_PATH,encoding='utf-8') as fd:
            list_feeds = [ x.strip() for x in fd.readlines() ]
    list_news = []

    for feed in list_feeds:
        raw_news = f_parse(feed)
        list_news = list_news + raw_news.entries

    sorted_list = sorted(list_news,key=lambda p: parsedate_to_datetime(p['published']),reverse=True )
    return jsonify(sorted_list)


@exportmodule.route('/icons/<path:path>')
def icons(path):
    return send_from_directory(ICONS_PATH, path)