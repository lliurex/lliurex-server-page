from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound
from ainur.utils import validate_groups
from flask_login import login_required

exportmodule = Blueprint('mainmodule', __name__,template_folder='templates')

@validate_groups(['admins'])
@login_required
def main():
    print(request)
    return render_template('main/main.html')

