"""Routes and helpers for the alumni update multi-step form.

This module implements the form wizard endpoints and helper functions
that persist session data into normalized SQLAlchemy models on final
submission. Key helpers include image filename building, date parsing,
and review section generation. Keep route handlers thin — business
logic that is reused lives in the small helper functions below.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app import db
from app.models import (
    Alumni, AlumniUpdate, AlumniAddress, AlumniGenevaEducation,
    AlumniFamilyUpdate, AlumniChild, AlumniEmploymentUpdate,
    AlumniEducationUpdate, AlumniClassNote, PhoneType
)
from app.utils.sendgrid import send_email
from datetime import datetime, date
from app.au_forms import (
    Step1Form, ContactForm, ChildrenForm, FamilyForm, EmploymentForm,
    EducationForm, LifeAchieveForm, VolunteerForm, ClassNoteForm, FinalSubmitForm
)
import base64
import uuid
import os
import re
from werkzeug.utils import secure_filename


# IMAGE FILENAME HELPER FUNCTION
def build_image_filename(class_note: AlumniClassNote, original_filename=None):
    """Create a filesystem-safe filename for a class-note image.

    Uses the associated alumnus' first/last name and the class_note id to
    construct a readable filename, normalized to lowercase and limited
    to alphanumerics and underscores. If no original filename is given,
    defaults to .jpg.
    """
    # Default extension to .jpg
    ext = '.jpg'
    
    if original_filename:
        _, given_ext = os.path.splitext(original_filename)
        if given_ext:
            ext = given_ext.lower()

    # Use data from the related alumnus via alumni_update
    first = ""
    last = ""
    try:
        first = (class_note.alumni_update.alumnus.first_name or "").strip()
        last = (class_note.alumni_update.alumnus.last_name or "").strip()
    except Exception:
        pass

    parts = [first, last, "IMG", str(class_note.id)]
    base = "_".join(p for p in parts if p)

    # Normalize: lowercase and only a–z, 0–9, underscore
    base = base.lower()
    base = re.sub(r'[^a-z0-9_]+', '_', base).strip('_')

    if not base:
        base = f"img_{class_note.id}"

    filename = f"{base}{ext}"
    return secure_filename(filename)

form_bp = Blueprint('form', __name__, url_prefix='/alumni-update')

def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


# NAVIGATION HELPERS
def navigate_update(current_update, direction="next"):
    """Navigate between the selected update pages.

    The wizard records the list of selected update types in session
    (`update_types`). Given the current update label and a direction
    ("next" or "prev"), return a redirect to the next route in the
    sequence. If the update isn't found we return the first step.
    """

# CONDITIONAL LOGIC HELPER FUNCTIONS 
UPDATE_ROUTES = {
    "Contact Information": "form.form_contact",
    "Family Update": "form.form_family",
    "Birth Announcement(s)": "form.form_children",
    "Employment Update": "form.form_employment",
    "Additional Education": "form.form_education",
    "Life Achievements": "form.form_achievement",
}

def navigate_update(current_update, direction="next"):
    selected_updates = session.get("update_types", [])

    try:
        current_index = selected_updates.index(current_update)
    except ValueError:
        return redirect(url_for("form.form_step1"))

    if direction == "next":
        target_index = current_index + 1

        if target_index >= len(selected_updates):
            return next_after_updates()

    else:  # prev
        target_index = current_index - 1

        if target_index < 0:
            return redirect(url_for("form.form_step1"))

    next_update = selected_updates[target_index]
    return redirect(url_for(UPDATE_ROUTES[next_update])) 

def next_after_updates():
    """Return the next route after completing update pages.

    If the user requested a class note, the next page is the class-note
    form; otherwise we move to the volunteer page or final review.
    """
    if session.get("wants_class_note") == "Yes":
        return redirect(url_for("form.form_class_note"))

    return redirect(url_for("form.form_volunteer"))

def last_selected_update_url():
    selected_updates = session.get("update_types", [])
    if selected_updates:
        return url_for(UPDATE_ROUTES[selected_updates[-1]])

    return url_for("form.form_step1")    

@form_bp.route('/step1', methods=['GET', 'POST'])
def form_step1():
    form = Step1Form()

    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit():
            # Save form data to session
            session['first_name'] = form.first_name.data
            session['last_name'] = form.last_name.data
            session['maiden_name'] = form.maiden_name.data

            session['geneva_degrees'] = form.geneva_degrees.data
            session['undergrad_year'] = form.undergrad_year.data
            session['graduate_year'] = form.graduate_year.data
            session['online_year'] = form.online_year.data

            selected_updates = form.update_types.data
            session['update_types'] = selected_updates
            session['update_index'] = 0

            session['wants_class_note'] = form.wants_class_note.data

            if selected_updates:
                first_update = selected_updates[0]
                return redirect(url_for(UPDATE_ROUTES[first_update]))
            
        else:
            return render_template('forms/step1.html', form=form)
                

    # Prepopulate form from session if available
    if request.method == 'GET':
        form.first_name.data = session.get('first_name')
        form.last_name.data = session.get('last_name')
        form.maiden_name.data = session.get('maiden_name')
        form.geneva_degrees.data = session.get('geneva_degrees')
        form.undergrad_year.data = session.get('undergrad_year')
        form.graduate_year.data = session.get('graduate_year')
        form.online_year.data = session.get('online_year')
        form.update_types.data = session.get('update_types', [])
        form.wants_class_note.data = session.get('wants_class_note')

    return render_template('forms/step1.html', form=form)

@form_bp.route('/contact', methods=['GET', 'POST'])
def form_contact():
    form = ContactForm()
    
    
    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit():
            # Save form data to session
            session['pref_salutation'] = form.pref_salutation.data
            session['email'] = form.email.data
            session['phone_type'] = form.phone_type.data
            session['phone'] = form.phone.data
            session['address_line1'] = form.address_line1.data
            session['address_line2'] = form.address_line2.data
            session['city'] = form.city.data
            session['state'] = form.state.data
            session['postal_code'] = form.postal_code.data
            session['country'] = form.country.data
            
            return navigate_update("Contact Information", "next")
        
        elif nav == 'prev':
            return navigate_update("Contact Information", "prev")

    # Prepopulate form from session if available
    if request.method == 'GET':
        form.pref_salutation.data = session.get('pref_salutation')
        form.email.data = session.get('email')
        form.phone_type.data = session.get('phone_type')
        form.phone.data = session.get('phone')
        form.address_line1.data = session.get('address_line1')
        form.address_line2.data = session.get('address_line2')
        form.city.data = session.get('city')
        form.state.data = session.get('state')
        form.postal_code.data = session.get('postal_code')
        form.country.data = session.get('country')
        
    return render_template('forms/contact.html', form=form)

# date parser helper function
def parse_session_date(value):
    if not value:
        return None

    if isinstance(value, date):
        return value

    for fmt in ("%Y-%m-%d", "%a, %d %b %Y %H:%M:%S GMT"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass

    return None


# REVIEW / RENDER HELPERS
def build_review_sections(session_data):
    """Build the list of sections/fields shown on the review page.

    This converts the raw session keys into a structure consumed by
    `forms/review.html` (title + list of label/value pairs), filtering
    out empty values.
    """

@form_bp.route('/family', methods=['GET', 'POST'])
def form_family():
    form = FamilyForm()
    
    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit():
            # Save form data to session
            session['marital_status'] = form.marital_status.data
            session['spouse_name'] = form.spouse_name.data
            session['spouse_geneva_grad'] = form.spouse_geneva_grad.data
            session['spouse_geneva_degrees'] = form.spouse_geneva_degrees.data
            session['spouse_undergrad_year'] = form.spouse_undergrad_year.data
            session['spouse_graduate_year'] = form.spouse_graduate_year.data
            session['spouse_online_year'] = form.spouse_online_year.data
            session['marry_date'] = form.marry_date.data

            return navigate_update("Family Update", "next")
            
        elif nav == 'prev':
            return navigate_update("Family Update", "prev")
        
    # Prepopulate form from session if available
    if request.method == 'GET':
        form.marital_status.data = session.get('marital_status')
        form.spouse_name.data = session.get('spouse_name')
        form.spouse_geneva_grad.data = session.get('spouse_geneva_grad')
        form.spouse_geneva_degrees.data = session.get('spouse_geneva_degrees')
        form.spouse_undergrad_year.data = session.get('spouse_undergrad_year')
        form.spouse_graduate_year.data = session.get('spouse_graduate_year')
        form.spouse_online_year.data = session.get('spouse_online_year')
        marry_date = session.get('marry_date')
        form.marry_date.data = parse_session_date(marry_date)
        
    return render_template('forms/family.html', form=form)    
            
@form_bp.route('/children', methods=['GET', 'POST'])
def form_children():
    form = ChildrenForm()

    if request.method == 'POST':
        if 'add_child' in request.form:
            form.children.append_entry()
            return render_template('forms/children.html', form=form)

        if 'remove_child' in request.form:
            index_to_remove = int(request.form['remove_child'])
            if len(form.children.entries) > 1:
                form.children.entries.pop(index_to_remove)
            return render_template('forms/children.html', form=form)

        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit():
            session['children'] = []
            for child_form in form.children:
                session['children'].append({
                    'first_name': child_form.first_name.data,
                    'last_name': child_form.last_name.data,
                    'gender': child_form.gender.data,
                    'birthday': child_form.birthday.data,
                })

            return navigate_update("Birth Announcement(s)", "next")

        elif nav == 'prev':
            return navigate_update("Birth Announcement(s)", "prev")

    # Prepopulate form from session if available
    if request.method == 'GET':
        form.children.entries = []
        children_data = session.get('children', [])
        for child in children_data:
            birthday = child.get('birthday')
            if birthday:
                birthday = parse_session_date(birthday)
            form.children.append_entry({
                'first_name': child.get('first_name'),
                'last_name': child.get('last_name'),
                'gender': child.get('gender'),
                'birthday': birthday,
            })

        if not form.children.entries:
            form.children.append_entry()

    return render_template('forms/children.html', children=form.children.data, form=form)

            
@form_bp.route('/employment', methods=['GET', 'POST'])
def form_employment():
    form = EmploymentForm()
    
    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit():
            session['employer'] = form.employer.data
            session['position'] = form.position.data
            session['start_date'] = form.start_date.data

            return navigate_update("Employment Update", "next")
            
        elif nav == 'prev':
            return navigate_update("Employment Update", "prev")
        
    # Prepopulate form from session if available            
    if request.method == 'GET':  
        form.employer.data = session.get('employer')
        form.position.data = session.get('position')
        start_date = session.get('start_date')
        form.start_date.data = parse_session_date(start_date)                      
        
    return render_template('forms/employment.html', form=form)
            
@form_bp.route('/education', methods=['GET', 'POST'])
def form_education():
    form = EducationForm()
    
    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit():
            session['education_institution'] = form.institution.data
            session['education_degree'] = form.degree.data
            session['education_graduation_year'] = form.graduation_year.data

            return navigate_update("Additional Education", "next")   
        
        elif nav == 'prev':
            return navigate_update("Additional Education", "prev")  
        
    # Prepopulate form from session if available            
    if request.method == 'GET':  
        form.institution.data = session.get('education_institution')
        form.degree.data = session.get('education_degree')
        form.graduation_year.data = session.get('education_graduation_year')
        non_g_grad_year = session.get('education_graduation_year')
        if non_g_grad_year:
            try:
                form.graduation_year.data = non_g_grad_year
            except Exception:
                pass

        return render_template('forms/education.html', form=form)       
            
@form_bp.route('/achievements', methods=['GET', 'POST'])
def form_achievement():
    form = LifeAchieveForm()
    
    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit(): 
            session['additional_updates'] = form.additional_updates.data
            
            return navigate_update("Life Achievements", "next")   
        
        elif nav == 'prev':
            return navigate_update("Life Achievements", "prev")
        
    # Prepopulate form from session if available            
    if request.method == 'GET':  
        form.additional_updates.data = session.get('additional_updates')
        
        return render_template('forms/achievements.html', form=form)
            
@form_bp.route('/volunteer', methods=['GET', 'POST'])
def form_volunteer():
    form = VolunteerForm()
    
    if request.method == 'POST':
        nav = request.form.get('nav')

        if nav == 'next' and form.validate_on_submit():
            session['volunteer_choices'] = form.volunteer_choices.data or []
            session['other_volunteer'] = form.other_volunteer.data or ""
            return redirect(url_for("form.form_final_review"))

        elif nav == 'prev':
            if session.get("wants_class_note") == "Yes":
                return redirect(url_for("form.form_class_note"))
            return redirect(last_selected_update_url())
        
    if request.method == 'GET':
        form.volunteer_choices.data = session.get('volunteer_choices', [])
        form.other_volunteer.data = session.get('other_volunteer', "")    
        
    return render_template('forms/volunteer.html', form=form) 
            
@form_bp.route('/class-note', methods=['GET', 'POST'])
def form_class_note():
    form = ClassNoteForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Always save class note to session before navigation
        session['class_note_text'] = form.class_note_text.data

        # Save base64-encoded image (if provided)
        resized_image = request.form.get('resized_image')
        if resized_image:
            try:
                header, encoded = resized_image.split(',', 1)
                image_bytes = base64.b64decode(encoded)

                # Define upload directory
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
                abs_upload_folder = os.path.join(current_app.root_path, upload_folder)
                os.makedirs(abs_upload_folder, exist_ok=True)

                # Generate a temporary filename
                filename = f"{uuid.uuid4().hex}.jpg"
                filepath = os.path.join(abs_upload_folder, filename)

                # Save file to disk
                with open(filepath, "wb") as f:
                    f.write(image_bytes)

                # Store filename in session (not full path)
                session['uploaded_image_filename'] = filename
                print(f"[DEBUG] Image saved to: {filepath}")

            except Exception as e:
                flash("There was a problem processing your uploaded image.", "danger")
                print(f"[ERROR] Failed to save image: {e}")

        # Handle navigation after saving
        nav = request.form.get('nav')
        if nav == 'prev':
            return redirect(last_selected_update_url())

        return redirect(url_for("form.form_volunteer"))

    # === GET Request ===
    elif request.method == 'GET':
        # Pre-fill class note from session
        form.class_note_text.data = session.get('class_note_text')

        uploaded_filename = session.get('uploaded_image_filename')
        if uploaded_filename:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
            image_url = url_for('static', filename=f'uploads/{uploaded_filename}')
        else:
            image_url = None

        return render_template('forms/class_note.html', form=form, image_url=image_url)

    # === Validation error (length, etc.) ===
    if form.class_note_text.errors:
        for error in form.class_note_text.errors:
            if "too long" in error.lower():
                flash(error, "warning")

    return render_template('forms/class-note.html', form=form)      

def has_value(value):
    if value is None:
        return False
    if value == "":
        return False
    if value == []:
        return False
    return True

def build_review_sections(session_data):
    # User's degree
    degree_rows = []

    degree_label_map = {
        "Undergraduate": "Undergraduate",
        "Graduate": "Graduate",
        "Online": "Online Degree",
    }
    
    degree_year_map = {
        "Undergraduate": session_data.get("undergrad_year"),
        "Graduate": session_data.get("graduate_year"),
        "Online": session_data.get("online_year"),
    }

    selected_degrees = session_data.get("geneva_degrees") or []

    for degree in selected_degrees:
        year = degree_year_map.get(degree)
        if year:
            degree_rows.append({
                "degree": degree_label_map.get(degree, degree),
                "year": degree_year_map.get(degree, "")
            })
        else:
            degree_rows.append({
                "degree": degree,
                "year": ""
            })
    # Spouse's degree        
    spouse_degree_rows = []

    spouse_degree_year_map = {
        "Undergraduate": session_data.get("spouse_undergrad_year"),
        "Graduate": session_data.get("spouse_graduate_year"),
        "Online Degree": session_data.get("spouse_online_year"),
    }

    spouse_selected_degrees = session_data.get("spouse_geneva_degrees") or []

    for degree in spouse_selected_degrees:
        year = spouse_degree_year_map.get(degree)
        if year:
            spouse_degree_rows.append({
                "degree": degree_label_map.get(degree, degree),
                "year": spouse_degree_year_map.get(degree, "")
            })
        else:
            spouse_degree_rows.append({
                "degree": degree,
                "year": ""
            })   
                 
    sections = [
        {
            "title": "Alumni Information",
            "fields": [
                ("First Name", session_data.get("first_name")),
                ("Last Name", session_data.get("last_name")),
                ("Maiden Name", session_data.get("maiden_name")),
                ("Geneva Degree(s)", degree_rows),
                ("Selected Update(s)", session_data.get("update_types")),
            ],
        },
        {
            "title": "Contact Information",
            "fields": [
                ("Preferred Salutation", session_data.get("pref_salutation")),
                ("Email", session_data.get("email")),
                ("Phone", session_data.get("phone")),
                ("Address", " ".join(filter(None, [
                    session_data.get("address_line1"),
                    session_data.get("address_line2")
                ]))),
                ("City, Region, Postal Code", " ".join(filter(None, [
                    session_data.get("city"),
                    session_data.get("state"),
                    session_data.get("postal_code")
                ]))),
                ("Country", session_data.get("country")),
            ],
        },
        {
            "title": "Birth Announcement(s)",
            "fields": [
                ("Birth Announcements", session_data.get("children")),
            ],
        },
        {
            "title": "Family Update",
            "fields": [
                ("Marital Status", session_data.get("marital_status")),
                ("Spouse Name", session_data.get("spouse_name")),
                ("Spouse's Geneva Degree(s)", spouse_degree_rows),
                ("Date of Marriage", session_data.get("marry_date")),
            ],
        },
        {
            "title": "Employment Update",
            "fields": [
                ("Employer", session_data.get("employer")),
                ("Position", session_data.get("position")),
                ("Start Date", session_data.get("start_date")),
            ],
        },
        {
            "title": "Additional Education",
            "fields": [
                ("Institution", session_data.get("education_institution")),
                ("Degree", session_data.get("education_degree")),
                ("Graduation Year", session_data.get("education_graduation_year")),
            ],
        },
        {
            "title": "Life Achievement(s)",
            "fields": [
                ("Additional Updates", session_data.get("additional_updates")),
            ],
        },
        {
            "title": "Class Note",
            "fields": [
                ("Class Note", session_data.get("class_note_text")),
                ("Uploaded Image", session_data.get("uploaded_image_filename")),
            ],
        },
        {
            "title": "Volunteer Opportunities",
            "fields": [
                ("Volunteer Interest", session_data.get("volunteer_choices")),
                ("Other Volunteer Idea(s)", session_data.get("other_volunteer")),
            ],
        },
    ]

    cleaned_sections = []

    for section in sections:
        filled_fields = []

        for label, value in section["fields"]:
            if has_value(value):
                filled_fields.append({
                    "label": label,
                    "value": value
                })

        if filled_fields:
            cleaned_sections.append({
                "title": section["title"],
                "fields": filled_fields
            })

    return cleaned_sections
            
@form_bp.route('/review', methods=['GET', 'POST'])
def form_final_review():
    form = FinalSubmitForm()
    
    review_sections = build_review_sections(session)
    children = session.get("children") or []
    noteFlag = session.get("wants_class_note") # 'Yes' or 'No'

    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit():
            return redirect(url_for("form.submit_final"))
    
        elif nav == 'prev':
            return redirect(url_for("form.form_step1"))
        
    return render_template('forms/review.html', review_sections=review_sections, noteFlag=noteFlag, children=children, form=form) 

@form_bp.route('/submit-final', methods=['GET', 'POST'])
def submit_final():
    if request.form.get('nav') == 'prev':
        return redirect(url_for("form.form_final_review"))

    review_sections = build_review_sections(session)

    try:
        # Create normalized objects
        alumnus = Alumni(
            first_name=session.get("first_name"),
            last_name=session.get("last_name"),
            maiden_name=session.get("maiden_name"),
            pref_salutation=session.get("pref_salutation"),
            email=session.get("email"),
            phone=session.get("phone"),
            phone_type=PhoneType(session.get("phone_type")) if session.get("phone_type") else None,
        )

        db.session.add(alumnus)
        db.session.flush()

        # Address
        address = AlumniAddress(
            alumnus_id=alumnus.id,
            address_line1=session.get("address_line1"),
            address_line2=session.get("address_line2"),
            city=session.get("city"),
            state=session.get("state"),
            postal_code=session.get("postal_code"),
            country=session.get("country"),
        )
        db.session.add(address)

        # Update
        alumni_update = AlumniUpdate(
            alumnus_id=alumnus.id,
            update_types=session.get("update_types", []),
            wants_class_note=(session.get("wants_class_note") == "Yes"),
            additional_updates=session.get("additional_updates"),
            volunteer_choices=session.get("volunteer_choices", []),
            other_volunteer=session.get("other_volunteer"),
        )
        db.session.add(alumni_update)
        db.session.flush()

        # Geneva educations
        for deg in session.get("geneva_degrees", []):
            year = None
            if deg == "TUG":
                year = session.get("undergrad_year")
            elif deg == "Grad":
                year = session.get("graduate_year")
            elif deg == "ODP":
                year = session.get("online_year")

            g = AlumniGenevaEducation(
                alumnus_id=alumnus.id,
                degree_level=deg,
                degree=deg,
                graduation_year=year,
            )
            db.session.add(g)

        # Family update
        if any([session.get("marital_status"), session.get("spouse_name"), session.get("spouse_geneva_degrees")]):
            fam = AlumniFamilyUpdate(
                alumni_update_id=alumni_update.id,
                marital_status=session.get("marital_status"),
                spouse_name=session.get("spouse_name"),
                is_spouse_geneva_grad=(session.get("spouse_geneva_grad") == "Yes"),
                spouse_geneva_degrees=session.get("spouse_geneva_degrees"),
                spouse_undergrad_year=session.get("spouse_undergrad_year"),
                spouse_graduate_year=session.get("spouse_graduate_year"),
                spouse_online_year=session.get("spouse_online_year"),
                marry_date=parse_session_date(session.get("marry_date")),
            )
            db.session.add(fam)

        # Children
        for child_data in session.get("children", []):
            child = AlumniChild(
                alumni_update_id=alumni_update.id,
                first_name=child_data.get("first_name"),
                last_name=child_data.get("last_name"),
                gender=child_data.get("gender"),
                birthday=parse_session_date(child_data.get("birthday")),
            )
            db.session.add(child)

        # Employment
        if session.get("employer"):
            emp = AlumniEmploymentUpdate(
                alumni_update_id=alumni_update.id,
                employer=session.get("employer"),
                position=session.get("position"),
                start_date=parse_session_date(session.get("start_date")),
            )
            db.session.add(emp)

        # Education
        if session.get("education_institution"):
            edu = AlumniEducationUpdate(
                alumni_update_id=alumni_update.id,
                institution=session.get("education_institution"),
                degree=session.get("education_degree"),
                graduation_year=session.get("education_graduation_year"),
            )
            db.session.add(edu)

        # Class note
        class_note_obj = None
        if session.get("wants_class_note") == "Yes":
            class_note_obj = AlumniClassNote(
                alumni_update_id=alumni_update.id,
                class_note_text=session.get("class_note_text"),
            )
            db.session.add(class_note_obj)
            db.session.flush()

        # Handle uploaded image renaming for class note
        temp_filename = session.get("uploaded_image_filename")
        if temp_filename and class_note_obj:
            upload_folder = current_app.config.get("UPLOAD_FOLDER", "static/uploads")
            abs_upload_folder = os.path.join(current_app.root_path, upload_folder)
            os.makedirs(abs_upload_folder, exist_ok=True)

            old_path = os.path.join(abs_upload_folder, temp_filename)

            if os.path.exists(old_path):
                new_filename = build_image_filename(class_note_obj, original_filename=temp_filename)
                new_path = os.path.join(abs_upload_folder, new_filename)
                os.rename(old_path, new_path)
                class_note_obj.image_filename = new_filename

        db.session.commit()

        email_body = render_template(
            'email/thank-you-email.html',
            full_data=session,
            review_sections=review_sections,
            children=session.get("children", [])
        )

        send_email(
            subject="New Alumni Update Form Submission",
            to_emails="hmschult1@geneva.edu",
            html_content=email_body
        )

        session.clear()
        flash("Thank you! Your alumni update has been submitted successfully.", "success")
        return redirect(url_for("form.thank_you"))

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(e)
        flash("An error occurred while submitting your update. Please try again.", "danger")
        return redirect(url_for("form.form_final_review"))

@form_bp.route('/thank-you')
def thank_you():
    return render_template('forms/thanks.html')   
    
    
                                      