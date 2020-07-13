from flask import Blueprint, render_template, url_for, request, redirect, abort
from ainur.utils import validate_groups
from flask_login import login_required
from werkzeug.utils import secure_filename

from os.path import join as os_path_join, exists as os_path_exists
from os import remove as os_remove
from shutil import copyfile
from json import load as json_load, dump as json_dump
from codecs import open as codecs_open

from ainur.adminmodules.main.forms import AdminServerPageForm, LinkForm, ReducedLink
from ainur.modules.main import get_resources, get_resource, get_menu_list


exportmodule = Blueprint('admin_mainmodule', __name__,template_folder='templates',static_folder='static/admin/main')

BASE_PATH = '/usr/share/lliurex-www/srv/'
OVERRIDE_PATH = '/var/lib/lliurex-www'
LINKS_PATH = os_path_join(BASE_PATH,'links')
FEED_PATH = os_path_join(BASE_PATH,'feed_list')
ICONS_PATH = os_path_join(BASE_PATH,'icons')
OVERRIDE_LINKS_PATH = os_path_join(OVERRIDE_PATH,'links')
OVERRIDE_FEED_PATH = os_path_join(OVERRIDE_PATH,'feed_list')
ROUTES_PERMISSIONS = {'main': ['teachers','admins'] ,'editlink':['teachers','admins'],'deletelink':['teachers','admins'],'hidelink':['teachers','admins']}
MENU = {'link':'admin_mainmodule.main','permissions':ROUTES_PERMISSIONS['main'],'name':{'default':'Main Page'}}

@exportmodule.route('/', methods=['GET', 'POST'])
@validate_groups(ROUTES_PERMISSIONS['main'])
@login_required
def main():
    form = AdminServerPageForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            saverss(form.data['listrss'])
            #saverorderlinks(form.data['listlink'])
            return redirect(url_for('admin_mainmodule.main'))
    else:
        list_feeds = []
        if not os_path_exists(OVERRIDE_FEED_PATH):
            copyfile(FEED_PATH, OVERRIDE_FEED_PATH)
        with codecs_open(OVERRIDE_FEED_PATH,encoding='utf-8') as fd:
            list_feeds = [ x.strip() for x in fd.readlines() ]
        listlink=get_resources()
        for x in listlink:
            x['name'] = x['name']['default']
            x['description'] = x['description']['default']

        
        form = AdminServerPageForm(listrss=list_feeds, listlink=listlink)

    return render_template('admin/main/main.html', title='admin server page', list_menu=get_menu_list('admin_mainmodule.main') ,form=form)


@exportmodule.route('/editlink', methods=['GET', 'POST'], defaults={'linkpath':'None'})
@exportmodule.route('/editlink/<linkpath>', methods=['GET', 'POST'])
@validate_groups(ROUTES_PERMISSIONS['editlink'])
@login_required
def editlink(linkpath):
    form = LinkForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if linkpath == 'None':
                linkpath = get_unique_name(OVERRIDE_LINKS_PATH, form.name.data)
                resource = {'editable':True,'visibility':True}
            else:
                resource = get_resource(linkpath)
                if resource is None or ( resource is not None and not resource['editable']):
                    return redirect(url_for('admin_mainmodule.main'))

            link_path = os_path_join(OVERRIDE_LINKS_PATH, linkpath)
            with codecs_open(link_path, 'w', encoding='utf-8') as fd:
                config = {}
                config['name'] = {'default': form.name.data}
                config['description'] = {'default': form.description.data}
                config['icon'] = form.icon.data
                config['link'] = form.link.data
                config = {**resource, **config}
                json_dump(config, fd, indent=4)
            return redirect(url_for('admin_mainmodule.main'))
        else:
            print('adios')
    else:
        if linkpath != 'None':
            resource = get_resource(linkpath)
            if resource is None or (resource is not None and not resource['editable']):
                return redirect(url_for('admin_mainmodule.main'))
            resource['name'] = resource['name']['default']
            resource['description'] = resource['description']['default']
            form = LinkForm(**resource)

    return render_template('admin/main/edit_link.html', list_menu=get_menu_list('admin_mainmodule.main') , form=form)


@exportmodule.route('/deletelink/<linkpath>', methods=['GET', 'POST'])
@validate_groups(ROUTES_PERMISSIONS['deletelink'])
@login_required
def deletelink(linkpath):
    form = ReducedLink()
    if request.method == 'POST':
        if form.validate_on_submit():
            resource = get_resource(linkpath)
            if resource is not None and resource['editable']:
                if os_path_exists(os_path_join(OVERRIDE_LINKS_PATH,linkpath)):
                    os_remove(os_path_join(OVERRIDE_LINKS_PATH,linkpath))
            return redirect(url_for('admin_mainmodule.main'))
    else:
        if linkpath != 'None':
            resource = get_resource(linkpath)
            if resource is None:
                return redirect(url_for('admin_mainmodule.main'))
            resource['name'] = resource['name']['default']
            resource['description'] = resource['description']['default']
            form = ReducedLink(**resource)

    return render_template('admin/main/delete_link.html', list_menu=get_menu_list('admin_mainmodule.main') , form=form)



@exportmodule.route('/hidelink/<linkpath>', methods=['GET', 'POST'])
@validate_groups(ROUTES_PERMISSIONS['hidelink'])
@login_required
def hidelink(linkpath):
    if linkpath != 'None':
        resource = get_resource(linkpath)
    else:
        abort(404)
    if resource is None:
        abort(404)
    else:
        resource['visibility'] = not resource['visibility']

    link_path = os_path_join(OVERRIDE_LINKS_PATH, linkpath)
    with codecs_open(link_path, 'w', encoding='utf-8') as fd:
        json_dump(resource,fd,indent=4)
        
    return 'Ok'



def saverss(listrss):
    with codecs_open(OVERRIDE_FEED_PATH,'w',encoding='utf-8') as fd:
        fd.writelines([x + '\n' for x in listrss if len(x) > 0])

def saverorderlinks(listlinks):
    pass

def get_unique_name(folder, filename):
    if not os_path_exists(os_path_join(folder,secure_filename(filename)+".json")):
        return secure_filename(filename)+".json"
    else:
        counter = 1
        while counter < 100:
            proposed_name = secure_filename(filename + str(counter)) +".json"
            if not os_path_exists(os_path_join(folder,prosposed_name)):
                return proposed_name
            counter += 1
