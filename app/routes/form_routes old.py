from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, AlumniClassNote, AlumniChild
from app.utils.sendgrid import send_email
from datetime import datetime
from app.auforms import IDForm, UpdateSelectorForm, ContactForm, UpdateForm, AlumniClassNoteForm, FinalSubmitForm
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
    

@form_bp.route('/step1', methods=['GET', 'POST'])
def form_step1():
    form = IDForm()
    form2 = UpdateSelectorForm()

    if request.method == 'POST':
        nav = request.form.get('nav')  # 'next' or 'prev'

        if nav == 'next' and form.validate_on_submit():
            # Save form data to session
            session['pref_salutaion'] = form.prefSalutation.data
            session['first_name'] = form.firstName.data
            session['last_name'] = form.lastName.data
            session['maiden_name'] = form.maidenName.data
            session['grad_year'] = form.gradYear.data
            session['update_types'] =form2.updateSelector.data
            
            return redirect(url_for('form.form_step2'))

    # Prepopulate form from session if available
    if request.method == 'GET':
        form.prefSalutation.data = session.get('pref_salutation')
        form.firstName.data = session.get('first_name')
        form.lastName.data = session.get('last_name')
        form.maidenName.data = session.get('maiden_name')
        form.gradYear.data = session.get('grad_year')
        form2.updateSelector.data = session.get('update_types')

    return render_template('forms/step1-bio-conditional.html', form=form)

@form_bp.route('/step2', methods=['GET', 'POST'])
def form_step2():
    form = UpdateForm()

    # === GET REQUEST ===
    if request.method == 'GET':
        # Pre-fill individual fields from session
        form.maritalStatus.data = session.get('marital_status')
        form.spouseName.data = session.get('spouse_name')
        form.spouseGradYear.data = session.get('spouse_grad_year')
        marry_date = session.get('date_of_marriage')
        if marry_date:
            form.marryDate.data = datetime.strptime(marry_date, '%Y-%m-%d').date()
        form.employer.data = session.get('employer')
        form.position.data = session.get('position')
        form.nonGEducation.data = session.get('non_geneva_education')
        form.additionalUpdates.data = session.get('additional_updates')
        form.volunteerChoices.data = session.get('volunteer_choices')
        form.otherVolunteer.data = session.get('other_volunteer_text')

        # AlumniChildren: clear existing, then repopulate
        form.AlumniChildren.entries = []
        AlumniChildren_data = session.get('AlumniChildren', [])
        for AlumniChild in AlumniChildren_data:
            birthday = AlumniChild.get('birthday')
            if birthday:
                birthday = datetime.strptime(birthday, "%Y-%m-%d").date()
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

        return render_template('forms/step2-update.html', form=form)

    # === POST REQUEST ===
    if request.method == 'POST':
        if 'add_AlumniChild' in request.form:
            form.AlumniChildren.append_entry()
            return render_template('forms/step2-update.html', form=form)

        if 'remove_AlumniChild' in request.form:
            index_to_remove = int(request.form['remove_AlumniChild'])
            if len(form.AlumniChildren.entries) > 1:
                form.AlumniChildren.entries.pop(index_to_remove)
            return render_template('forms/step2-update.html', form=form)

        # Handle navigation (next or prev), but first:
        if form.validate_on_submit():
            # ✅ Save data to session BEFORE redirect
            session['marital_status'] = form.maritalStatus.data
            session['spouse_name'] = form.spouseName.data
            session['spouse_grad_year'] = form.spouseGradYear.data
            session['date_of_marriage'] = str(form.marryDate.data) if form.marryDate.data else None
            session['employer'] = form.employer.data
            session['position'] = form.position.data
            session['non_geneva_education'] = form.nonGEducation.data
            session['additional_updates'] = form.additionalUpdates.data
            session['volunteer_choices'] = form.volunteerChoices.data
            session['other_volunteer_text'] = form.otherVolunteer.data

            # Save AlumniChildren manually
            session['AlumniChildren'] = []
            for AlumniChild_form in form.AlumniChildren:
                session['AlumniChildren'].append({
                    'first_name': AlumniChild_form.AlumniChildsFirstName.data,
                    'last_name': AlumniChild_form.AlumniChildsLastName.data,
                    'gender': AlumniChild_form.AlumniChildGender.data,
                    'birthday': str(AlumniChild_form.AlumniChildsBirthday.data) if AlumniChild_form.AlumniChildsBirthday.data else None
                })

            # 🔁 Navigate based on user click
            nav = request.form.get("nav")
            if nav == "prev":
                return redirect(url_for("form.form_step1"))
            else:
                return redirect(url_for("form.form_step3"))

    # If form not valid or other issue, redisplay with errors
    return render_template('forms/step2-update.html', form=form)

MAX_NOTE_LENGTH = 300

@form_bp.route('/step3', methods=['GET', 'POST'])
def form_step3():
    form = AlumniClassNoteForm()

    # === POST Request ===
    if request.method == 'POST' and form.validate_on_submit():
        # ✅ Always save class note to session before navigation
        session['class_note'] = form.AlumniClassNote.data

        # ✅ Save base64-encoded image (if provided)
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

        # ✅ Handle navigation after saving
        nav = request.form.get('nav')
        if nav == 'prev':
            return redirect(url_for('form.form_step2'))
        else:
            return redirect(url_for('form.review_submission'))

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
            
            return render_template('forms/step3-note.html', form=form, image_url=image_url)

    # === Validation error (length, etc.) ===
    if form.AlumniClassNote.errors:
        for error in form.AlumniClassNote.errors:
            if "too long" in error.lower():
                flash(error, "warning")

    return render_template('forms/step3-note.html', form=form)

@form_bp.route('/review', methods=['GET', 'POST'])
def review_submission():
    form = FinalSubmitForm()
    return render_template('forms/review.html', session_data=session, form=form)

@form_bp.route('/submit-final', methods=['GET', 'POST'])
def submit_final():
    # Detect navigation intent
    nav = request.form.get('nav')

    # ✅ If user clicked "Previous", go back to step 3 (do not submit)
    if nav == 'prev':
        return redirect(url_for('form.form_step3'))

    # ✅ If user clicked "Submit", continue as normal
    try:
        # STEP 1: Build AlumniClassNote from session
        note = AlumniClassNote(
            
        )

        # STEP 2: Add AlumniChildren
        for AlumniChild_data in session.get('AlumniChildren', []):
            AlumniChild = AlumniChild(
                first_name=AlumniChild_data.get('first_name'),
                last_name=AlumniChild_data.get('last_name'),
                gender=AlumniChild_data.get('gender'),
                birthday=parse_date(AlumniChild_data.get('birthday'))
            )
            note.AlumniChildren.append(AlumniChild)

        # STEP 3: Save note and get ID
        db.session.add(note)
        db.session.flush()

        # STEP 4: Rename image if present
        temp_filename = session.get('uploaded_image_filename')
        if temp_filename:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
            abs_upload_folder = os.path.join(current_app.root_path, upload_folder)
            os.makedirs(abs_upload_folder, exist_ok=True)

            old_path = os.path.join(abs_upload_folder, temp_filename)
            if os.path.exists(old_path):
                new_filename = build_image_filename(note, original_filename=temp_filename)
                new_path = os.path.join(abs_upload_folder, new_filename)
                os.rename(old_path, new_path)
                note.image_filename = new_filename
            else:
                print(f"[WARNING] Uploaded image not found: {old_path}")

        # STEP 5: Commit
        db.session.commit()

        # STEP 6: Send confirmation email
        email_body = render_template(
            'forms/email/thank-you-email.html',
            full_data=session,
            AlumniChildren=session.get('AlumniChildren', [])
        )

        send_email(
            subject='New Alumni Update Form Submission',
            to_emails='hmschult1@geneva.edu',
            html_content=email_body
        )

        # STEP 7: Clear session and redirect
        session.clear()
        flash("Thank you! Your update has been submitted successfully.", "success")
        return redirect(url_for('form.thank_you'))

    except Exception as e:
        db.session.rollback()
        print("Submission error:", str(e))
        flash("An error occurred while submitting your update.", "danger")
        return redirect(url_for('form.review_submission'))

@form_bp.route('/thank-you')
def thank_you():
    return render_template('forms/thank-you.html')
