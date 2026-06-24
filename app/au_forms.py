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
from app.utils.countries import country_list

class Step1Form(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    maiden_name = StringField('Maiden Name (if applicable)', validators=[Optional()])
    geneva_degrees = SelectMultipleField(
        "Geneva Degree(s)",
        choices=[
            ("TUG", "Undergraduate Degree"),
            ("Grad", "Graduate Degree"),
            ("ODP", "Online Degree"),
        ],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=True),
        validators=[DataRequired()]
    )
    undergrad_year = StringField("Undergraduate Graduation Year", validators=[Optional()])
    graduate_year = StringField("Graduate Graduation Year", validators=[Optional()])
    online_year = StringField("Online Program Graduation Year", validators=[Optional()])
    update_types = SelectMultipleField(
        "What information would you like to share with the College?",
        choices=[
            ('Contact Information', "Contact Information"),
            ('Birth Announcement(s)', "Birth Announcement(s)"),
            ('Family Update', "Family Update"),
            ('Employment Update', "Employment Update"),
            ('Additional Education', "Additional Education"),
            ('Life Achievements', "Life Achievement(s)"),
        ],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=True),
        validators=[DataRequired()]
    )
    wants_class_note = RadioField(
        "Would you like to submit a Class Note in addition to updating your alumni record?",
        choices=[('Yes', 'Yes, I would like to submit a Class Note for publication'), ('No', 'No, I would rather not submit a Class Note at this time')],
        validators=[DataRequired()]
    )

class ContactForm(FlaskForm):
    pref_salutation = StringField('Preferred Salutation', validators=[Optional()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone_type = RadioField(
        "Phone Type",
        choices=[('mobile', 'Mobile'), ('home', 'Home')],
        validators=[DataRequired()]
    )
    phone = TelField('Phone Number', validators=[DataRequired()])
    address_line1 = StringField('Street Address (Line 1)', validators=[DataRequired()])
    address_line2 = StringField('Street Address (Line 2)', validators=[Optional()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State / Region', validators=[DataRequired()])
    postal_code = StringField('Postal / ZIP Code', validators=[DataRequired()])
    country = SelectField('Country', choices=[], validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.country.choices = [('', 'Select a country')] + country_list

class FamilyForm(FlaskForm):
    marital_status = SelectField(
        'Marital Status',
        choices=[
            ('', 'Select your status'),
            ('Single', 'Single'),
            ('Married', 'Married'),
            ('Divorced', 'Divorced'),
            ('Widowed', 'Widowed'),
            ('Separated', 'Separated')
        ],
        validators=[Optional()]
    )
    spouse_name = StringField("Spouse's Name", validators=[Optional()])
    spouse_geneva_grad = RadioField(
        "Is your spouse also a graduate of Geneva College?",
        choices=[('Yes', 'Yes'), ('No', 'No')],
        validators=[Optional()]
    )
    spouse_geneva_degrees = SelectMultipleField(
        "Spouse's Geneva Degree(s)",
        choices=[
            ("TUG", "Undergraduate"),
            ("Grad", "Graduate"),
            ("ODP", "Online"),
        ],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=True),
        validators=[Optional()]
    )
    spouse_undergrad_year = StringField("Undergraduate Graduation Year", validators=[Optional()])
    spouse_graduate_year = StringField("Graduate Graduation Year", validators=[Optional()])
    spouse_online_year = StringField("Online Program Graduation Year", validators=[Optional()])
    marry_date = DateField("Date of Marriage", format='%Y-%m-%d', validators=[Optional()])
    
class ChildForm(FlaskForm):
    first_name = StringField("Child's First Name", validators=[Optional()])
    last_name = StringField("Child's Last Name", validators=[Optional()])
    gender = RadioField(
        "Child's Gender",
        choices=[('Son', 'Son'), ('Daughter', 'Daughter')],
        validators=[Optional()]
    )
    birthday = DateField("Child's Birthdate", format='%Y-%m-%d', validators=[Optional()])
    
class ChildrenForm(FlaskForm):
    children = FieldList(FormField(ChildForm), min_entries=1)    
            
class EmploymentForm(FlaskForm):
    employer = StringField("Employer", validators=[Optional()])
    position = StringField("Position", validators=[Optional()])
    start_date = DateField("Start Date", format='%Y-%m-%d', validators=[Optional()])
        
class EducationForm(FlaskForm):
    institution = StringField("Institution", validators=[Optional()])
    degree = StringField("Degree Earned", validators=[Optional()])
    graduation_year = StringField("Graduation Year", validators=[Optional()])

class LifeAchieveForm(FlaskForm):
    additional_updates = TextAreaField("Anything else you'd like to share with the College?", validators=[Optional()])

class VolunteerForm(FlaskForm):
    volunteer_radio = RadioField(
        "Are you interested in volunteering as a Geneva alumni?",
        choices=[('Yes', 'Yes, show me volunteer opportunities!'), ('No', 'No, I am not interested at this time.')],
        validators=[Optional()]
    )
    volunteer_choices = SelectMultipleField(
        "Select Volunteer Opportunities:",
        choices=[
            ('Help with admissions in my area', "Help with admissions in my area"),
            ('Speak to current students', "Speak to current students"),
            ('Serve on my class reunion committee', "Serve on my class reunion committee"),
            ('Host an alumni event', "Host an alumni event"),
            ('Other', "Other"),
        ],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=True),
        validators=[Optional()]
    )
    other_volunteer = TextAreaField("Other Volunteer Ideas", validators=[Optional()])

class ClassNoteForm(FlaskForm):
    class_note_text = TextAreaField(
        'Class Note',
        validators=[
            Optional(),
            Length(max=300, message='Your note is too long to be posted on the website (max 300 characters).')
        ]
    )
    
    image = FileField(
        'Image',
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
        ]
    )
    
    existing_image = HiddenField()
    
class FinalSubmitForm(FlaskForm):
    submit = SubmitField("Submit Final")
    
    