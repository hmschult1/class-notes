from wtforms import FieldList, FormField
from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, DateField, TextAreaField,
    RadioField, SelectMultipleField, SubmitField, TelField, HiddenField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Optional, Length
)
from wtforms.widgets import ListWidget, CheckboxInput
from flask_wtf.file import FileField, FileAllowed

class EditFullEntryForm(FlaskForm):
    # --- From ContactForm ---
    firstName = StringField('First Name', validators=[DataRequired()])