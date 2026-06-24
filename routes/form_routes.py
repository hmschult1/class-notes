from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, AlumniClassNote, AlumniChild
from app.utils.sendgrid import send_email
from datetime import datetime, date
from app.auForms import step1Form, ContactForm, AlumniChildrenForm, FamilyForm, EmploymentForm, EducationForm, LifeAchieveForm, VolunteerForm, AlumniClassNoteForm, FinalSubmitForm
from flask import current_app
from flask import session, request
import base64
import uuid
import os
from flask import (
    Blueprint, render_template, request, session, redirect, url_for, flash
)
import re
from werkzeug.utils import secure_filename

# IMAGE FILENAME HELPER FUNCTION
def build_image_filename(note, original_filename=None):
    """
    Build a filename like: first_last_IMG_<id>.ext
    using safe characters only. Defaults to .jpg if no filename is provided.
    """
    # Default extension to .jpg
    ext = '.jpg'
    
    if original_filename:
        _, given_ext = os.path.splitext(original_filename)
        if given_ext:
            ext = given_ext.lower()

    # Use data from the note
    first = (note.first_name or "").strip()
    last = (note.last_name or "").strip()

    parts = [first, last, "IMG", str(note.id)]
    base = "_".join(p for p in parts if p)

    # Normalize: lowercase and only a–z, 0–9, underscore
    base = base.lower()
    base = re.sub(r'[^a-z0-9_]+', '_', base).strip('_')

    if not base:
        base = f"img_{note.id}"

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

# CONDITIONAL LOGIC HELPER FUNCTIONS 
UPDATE_ROUTES = {
    "Contact Information": "form.form_contact",
    "Family Update": "form.form_family",
    "Birth Announcement": "form.form_AlumniChildren",
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
    if session.get("class_note_option") == "Yes":
        return redirect(url_for("form.form_AlumniClassNote"))

    return redirect(url_for("form.form_volunteer"))

def last_selected_update_url():
    selected_updates = session.get("update_types", [])
    if selected_updates:
        return url_for(UPDATE_ROUTES[selected_updates[-1]])

    return url_for("form.form_step1")    

@form_bp.route('/step1', methods=['GET', 'POST'])
def form_step1():
    form = step1Form()

    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit():
            # Save form data to session
            session['first_name'] = form.firstName.data
            session['last_name'] = form.lastName.data
            session['maiden_name'] = form.maidenName.data
            
            session['geneva_degree'] = form.genevaDegree.data
            session['undergrad_year'] = form.undergradYear.data
            session['graduate_year'] = form.graduateYear.data
            session['online_year'] = form.onlineYear.data
            
            session['update_types'] = form.updateSelector.data
            
            selected_updates = form.updateSelector.data
            session['update_types'] = selected_updates
            session['update_index'] = 0
            
            session['class_note_option'] = form.AlumniClassNote.data

            first_update = selected_updates[0]
            return redirect(url_for(UPDATE_ROUTES[first_update]))
            

    # Prepopulate form from session if available
    if request.method == 'GET':
        form.firstName.data = session.get('first_name')
        form.lastName.data = session.get('last_name')
        form.maidenName.data = session.get('maiden_name')
        form.genevaDegree.data = session.get('geneva_degree')
        form.undergradYear.data = session.get('undergrad_year')
        form.graduateYear.data = session.get('graduate_year')
        form.onlineYear.data = session.get('online_year')
        form.updateSelector.data = session.get('update_types', [])
        form.AlumniClassNote.data = session.get('class_note_option')

    return render_template('forms/step1.html', form=form)

@form_bp.route('/contact', methods=['GET', 'POST'])
def form_contact():
    form = ContactForm()
    
    
    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit():
            # Save form data to session
            session['pref_salutation'] = form.prefSalutation.data
            session['email'] = form.email.data
            session['phone_type'] = form.phoneType.data
            session['phone'] = form.phone.data
            session['address_line1'] = form.addressLine1.data
            session['address_line2'] = form.addressLine2.data
            session['city'] = form.city.data
            session['state'] = form.state.data
            session['postal_code'] = form.postalCode.data
            session['country'] = form.country.data
            
            return navigate_update("Contact Information", "next")
        
        elif nav == 'prev':
            return navigate_update("Contact Information", "prev")

    # Prepopulate form from session if available
    if request.method == 'GET':
        form.prefSalutation.data = session.get('pref_salutation')
        form.email.data = session.get('email')
        form.phoneType.data = session.get('phone_type')
        form.phone.data = session.get('phone')
        form.addressLine1.data = session.get('address_line1')
        form.addressLine2.data = session.get('address_line2')
        form.city.data = session.get('city')
        form.state.data = session.get('state')
        form.postalCode.data = session.get('postal_code')
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

@form_bp.route('/family', methods=['GET', 'POST'])
def form_family():
    form = FamilyForm()
    
    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit():
            # Save form data to session
            session['marital_status'] = form.maritalStatus.data
            session['spouse_name'] = form.spouseName.data
            session['is_spouse_G_grad'] = form.spouseGenevaGrad.data
            session['spouse_geneva_degree'] = form.spouseGenevaDegree.data
            session['spouse_undergrad_year'] = form.spouseUndergradYear.data
            session['spouse_graduate_year'] = form.spouseGraduateYear.data
            session['spouse_online_year'] = form.spouseOnlineYear.data
            session['marry_date'] = form.marryDate.data
            
            return navigate_update("Family Update", "next")
            
        elif nav == 'prev':
            return navigate_update("Family Update", "prev")
        
    # Prepopulate form from session if available
    if request.method == 'GET':
        form.maritalStatus.data = session.get('marital_status')
        form.spouseName.data = session.get('spouse_name')
        form.spouseGenevaGrad.data = session.get('is_spouse_G_grad')
        form.spouseGenevaDegree.data = session.get('spouse_geneva_degree')
        form.spouseUndergradYear.data = session.get('spouse_undergrad_year')
        form.spouseGraduateYear.data = session.get('spouse_graduate_year')
        form.spouseOnlineYear.data = session.get('spouse_online_year')
        marry_date = session.get('marry_date')
        form.marryDate.data = parse_session_date(marry_date)
        
    return render_template('forms/family.html', form=form)    
            
@form_bp.route('/AlumniChildren', methods=['GET', 'POST'])
def form_AlumniChildren():
    form = AlumniChildrenForm()
    
    if request.method == 'POST':
        if 'add_AlumniChild' in request.form:
            form.AlumniChildren.append_entry()
            return render_template('forms/AlumniChildren.html', form=form)

        if 'remove_AlumniChild' in request.form:
            index_to_remove = int(request.form['remove_AlumniChild'])
            if len(form.AlumniChildren.entries) > 1:
                form.AlumniChildren.entries.pop(index_to_remove)
            return render_template('forms/AlumniChildren.html', form=form)
        
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav =='next' and form.validate_on_submit():
            session['AlumniChildren'] = []
            for AlumniChild_form in form.AlumniChildren:
                session['AlumniChildren'].append({
                    'first_name': AlumniChild_form.AlumniChildsFirstName.data,
                    'last_name': AlumniChild_form.AlumniChildsLastName.data,
                    'gender': AlumniChild_form.AlumniChildGender.data,
                    'birthday': AlumniChild_form.AlumniChildsBirthday.data,
                })
                
            return navigate_update("Birth Announcement", "next")
            
        elif nav == 'prev':
            return navigate_update("Birth Announcement", "prev")
        
    # Prepopulate form from session if available            
    if request.method == 'GET':
        # AlumniChildren: clear existing, then repopulate
        form.AlumniChildren.entries = []
        AlumniChildren_data = session.get('AlumniChildren', [])
        for AlumniChild in AlumniChildren_data:
            birthday = AlumniChild.get('birthday')
            if birthday:
                birthday = parse_session_date(AlumniChild.get("birthday"))
            else:
                birthday = None
            form.AlumniChildren.append_entry({
                'AlumniChildsFirstName': AlumniChild.get('first_name'),
                'AlumniChildsLastName': AlumniChild.get('last_name'),
                'AlumniChildGender': AlumniChild.get('gender'),
                'AlumniChildsBirthday': birthday,
            })

        # Always ensure at least one entry
        if not form.AlumniChildren.entries:
            form.AlumniChildren.append_entry()            
        
    return render_template('forms/AlumniChildren.html', form=form) 

            
@form_bp.route('/employment', methods=['GET', 'POST'])
def form_employment():
    form = EmploymentForm()
    
    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit():
            session['employer'] = form.employer.data
            session['position'] = form.position.data
            session['start_date'] = form.startDate.data
            
            return navigate_update("Employment Update", "next")
            
        elif nav == 'prev':
            return navigate_update("Employment Update", "prev")
        
    # Prepopulate form from session if available            
    if request.method == 'GET':  
        form.employer.data = session.get('employer')
        form.position.data = session.get('position')
        form.startDate.data = session.get('start_date')  
        start_date = session.get('start_date')
        form.startDate.data = parse_session_date(start_date)                      
        
    return render_template('forms/employment.html', form=form)
            
@form_bp.route('/education', methods=['GET', 'POST'])
def form_education():
    form = EducationForm()
    
    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit():
            session['non_g_education'] = form.nonGEducation.data
            session['non_g_degree'] = form.nonGEducationDegree.data
            session['non_g_grad_year'] = form.nonGEducationGradYear.data
            
            return navigate_update("Additional Education", "next")   
        
        elif nav == 'prev':
            return navigate_update("Additional Education", "prev")  
        
    # Prepopulate form from session if available            
    if request.method == 'GET':  
        form.nonGEducation.data = session.get('non_g_education')
        form.nonGEducationDegree.data = session.get('non_g_degree')
        form.nonGEducationGradYear.data = session.get('non_g_grad_year')  
        non_g_grad_year = session.get('non_g_grad_year')
        if non_g_grad_year:
            form.nonGEducationGradYear.data = datetime.strptime(non_g_grad_year, '%Y').date()                       
        
        return render_template('forms/education.html', form=form)       
            
@form_bp.route('/achievements', methods=['GET', 'POST'])
def form_achievement():
    form = LifeAchieveForm()
    
    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit(): 
            session['additional_updates'] = form.additionalUpdates.data
            
            return navigate_update("Life Achievements", "next")   
        
        elif nav == 'prev':
            return navigate_update("Life Achievements", "prev")
        
    # Prepopulate form from session if available            
    if request.method == 'GET':  
        form.additionalUpdates.data = session.get('additional_updates')
        
        return render_template('forms/achievements.html', form=form)
            
@form_bp.route('/volunteer', methods=['GET', 'POST'])
def form_volunteer():
    form = VolunteerForm()
    
    if request.method == 'POST':
        nav = request.form.get('nav')

        if nav == 'next' and form.validate_on_submit():
            session['volunteer_radio'] = form.volunteerRadio.data
            session['volunteer_choices'] = form.volunteerChoices.data or []
            session['other_volunteer_text'] = form.otherVolunteer.data or ""
            return redirect(url_for("form.form_final_review"))

        elif nav == 'prev':
            if session.get("class_note_option") == "Yes":
                return redirect(url_for("form.form_AlumniClassNote"))
            return redirect(last_selected_update_url())
        
    if request.method == 'GET':
        form.volunteerRadio.data = session.get('volunteer_radio')
        form.volunteerChoices.data = session.get('volunteer_choices', [])
        form.otherVolunteer.data = session.get('other_volunteer_text', "")    
        
    return render_template('forms/volunteer.html', form=form) 
            
@form_bp.route('/class-note', methods=['GET', 'POST'])
def form_AlumniClassNote():
    form = AlumniClassNoteForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        # Always save class note to session before navigation
        session['class_note'] = form.AlumniClassNote.data

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
        form.AlumniClassNote.data = session.get('class_note')
        
        uploaded_filename = session.get('uploaded_image_filename')
        if uploaded_filename:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
            image_url = url_for('static', filename=f'uploads/{uploaded_filename}')
        else:
            image_url = None
            
        return render_template('forms/class-note.html', form=form, image_url=image_url)

    # === Validation error (length, etc.) ===
    if form.AlumniClassNote.errors:
        for error in form.AlumniClassNote.errors:
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
        "TUG": "Undergraduate",
        "Grad": "Graduate",
        "ODP": "Online",
    }
    
    degree_year_map = {
        "TUG": session_data.get("undergrad_year"),
        "Grad": session_data.get("graduate_year"),
        "ODP": session_data.get("online_year"),
    }

    selected_degrees = session_data.get("geneva_degree") or []

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
        "TUG": session_data.get("spouse_undergrad_year"),
        "Grad": session_data.get("spouse_graduate_year"),
        "ODP": session_data.get("spouse_online_year"),
    }

    spouse_selected_degrees = session_data.get("spouse_geneva_degree") or []

    for degree in spouse_selected_degrees:
        year = spouse_degree_year_map.get(degree)
        if year:
            spouse_degree_rows.append({
                "degree": degree_label_map.get(degree, degree),
                "year": degree_year_map.get(degree, "")
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
                ("Birth Announcements", session_data.get("AlumniChildren")),
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
                ("Institution", session_data.get("non_g_education")),
                ("Degree", session_data.get("non_g_degree")),
                ("Graduation Year", session_data.get("non_g_grad_year")),
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
                ("Class Note", session_data.get("class_note")),
                ("Uploaded Image", session_data.get("uploaded_image_filename")),
            ],
        },
        {
            "title": "Volunteer Opportunities",
            "fields": [
                ("Interest", session_data.get("volunteer_radio")),
                ("Volunteer Opportunities", session_data.get("volunteer_choices")),
                ("Other Volunteer Idea", session_data.get("other_volunteer_text")),
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
    AlumniChildren = session.get("AlumniChildren") or []
    noteFlag = session.get("class_note_option") # 'Yes' or 'No'

    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'
        if nav == 'next' and form.validate_on_submit():
            return redirect(url_for("form.submit_final"))
    
        elif nav == 'prev':
            return redirect(url_for("form.form_step1"))
        
    return render_template('forms/review.html', review_sections=review_sections, noteFlag=noteFlag, AlumniChildren=AlumniChildren, form=form) 

@form_bp.route('/submit-final', methods=['GET', 'POST'])
def submit_final():
    if request.form.get('nav') == 'prev':
        return redirect(url_for("form.form_final_review"))

    try:
        note = AlumniClassNote(
            first_name=session.get("first_name"),
            last_name=session.get("last_name"),
            maiden_name=session.get("maiden_name"),

            geneva_degree=session.get("geneva_degree"),
            undergrad_year=session.get("undergrad_year"),
            graduate_year=session.get("graduate_year"),
            online_year=session.get("online_year"),

            update_types=", ".join(session.get("update_types", [])),
            class_note_option=session.get("class_note_option") == "Yes",

            pref_salutation=session.get("pref_salutation"),
            email=session.get("email"),
            phone=session.get("phone"),
            Phone_type=session.get("phone_type"),

            address_line1=session.get("address_line1"),
            address_line2=session.get("address_line2"),
            city=session.get("city"),
            state=session.get("state"),
            postal_code=session.get("postal_code"),
            country=session.get("country"),

            marital_status=session.get("marital_status"),
            spouse_name=session.get("spouse_name"),
            is_spouse_G_grad=session.get("is_spouse_G_grad") == "Yes",
            spouse_geneva_degree=session.get("spouse_geneva_degree"),
            spouse_undergrad_year=session.get("spouse_undergrad_year"),
            spouse_graduate_year=session.get("spouse_graduate_year"),
            spouse_online_year=session.get("spouse_online_year"),
            marry_date=parse_session_date(session.get("marry_date")),

            employer=session.get("employer"),
            position=session.get("position"),
            start_date=parse_session_date(session.get("start_date")),

            non_g_education=session.get("non_g_education"),
            non_g_degree=session.get("non_g_degree"),
            non_g_grad_year=session.get("non_g_grad_year"),

            additional_updates=session.get("additional_updates"),

            volunteer_radio=session.get("volunteer_radio") == "Yes",
            volunteer_choices=", ".join(session.get("volunteer_choices", [])),
            other_volunteer=session.get("other_volunteer_text"),

            class_note_text=session.get("class_note"),
        )

        db.session.add(note)
        db.session.flush()

        for AlumniChild_data in session.get("AlumniChildren", []):
            AlumniChild = AlumniChild(
                first_name=AlumniChild_data.get("first_name"),
                last_name=AlumniChild_data.get("last_name"),
                gender=AlumniChild_data.get("gender"),
                birthday=parse_session_date(AlumniChild_data.get("birthday"))
            )
            note.AlumniChildren.append(AlumniChild)

        temp_filename = session.get("uploaded_image_filename")
        if temp_filename:
            upload_folder = current_app.config.get("UPLOAD_FOLDER", "static/uploads")
            abs_upload_folder = os.path.join(current_app.root_path, upload_folder)
            os.makedirs(abs_upload_folder, exist_ok=True)

            old_path = os.path.join(abs_upload_folder, temp_filename)

            if os.path.exists(old_path):
                new_filename = build_image_filename(note, original_filename=temp_filename)
                new_path = os.path.join(abs_upload_folder, new_filename)
                os.rename(old_path, new_path)
                note.image_filename = new_filename

        db.session.commit()

        email_body = render_template(
            "forms/email/thank-you-email.html",
            full_data=session,
            AlumniChildren=session.get("AlumniChildren", [])
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
    return render_template('forms/thank-you.html')   
    
    
                                      