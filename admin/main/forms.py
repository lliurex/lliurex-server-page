from wtforms import FieldList, Form, StringField, SubmitField, FormField, IntegerField, HiddenField, BooleanField
from wtforms.fields.html5 import URLField
from wtforms.validators import InputRequired, Regexp
from flask_wtf import FlaskForm

class LinkForm(FlaskForm):
    filename = HiddenField()
    link = URLField(validators=[InputRequired()],label='Link')
    icon = URLField(label='Icon url',validators=[Regexp('^http.*')])
    name = StringField(label='Name')
    description = StringField(label='Description')
    order = IntegerField(default=999)
    editable = BooleanField(default=True)
    visibility = BooleanField(default=True)

class ReducedLink(FlaskForm):
    filename = HiddenField()
    name = StringField()
    icon = StringField(label='Icon url')
    order = IntegerField(default=999)
    editable = BooleanField(default=True)
    visibility = BooleanField(default=True)

class AdminServerPageForm(FlaskForm):
    listlink = FieldList(FormField(ReducedLink))
    listrss = FieldList(StringField())