from flask import Blueprint, render_template
from flask_login import login_required
from app.models import AlumniClassNote
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.authForms import ChangePasswordForm
# from app.auForms import EditFullEntryForm
from app import db

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# DASHBOARD ROUTES
@dashboard_bp.route('/')
@login_required
def dashboard_home():
    notes = AlumniClassNote.query.order_by(AlumniClassNote.submitted_at.desc()).all()
    return render_template('admin_panel/landing.html', notes=notes)

@dashboard_bp.route('/accounts', methods=['GET', 'POST'])
@login_required
def dashboard_accounts():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.current_password.data):
            flash('Incorrect current password.', 'danger')
        else:
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated successfully.', 'success')
            return redirect(url_for('dashboard.dashboard_accounts'))

    return render_template('admin_panel/accounts.html', form=form)

@dashboard_bp.route('/class-notes')
@login_required
def dashboard_AlumniClassNotes():
    entries = AlumniClassNote.query.order_by(AlumniClassNote.submitted_at.desc()).all()
    form = EditFullEntryForm()
    return render_template('admin_panel/class-notes.html', entries=entries, form=form)

@dashboard_bp.route('/class-notes/<int:note_id>/edit', methods=['POST'])
@login_required
def edit_class_note(note_id):
    form = EditFullEntryForm()

    if form.validate_on_submit():
        note = AlumniClassNote.query.get_or_404(note_id)

        # Populate fields from form
        note.viewed = True
        note.first_name = form.firstName.data
        note.last_name = form.lastName.data
        note.maiden_name = form.maidenName.data
        note.email = form.email.data
        note.phone = form.phone.data
        note.grad_year = form.gradYear.data
        note.address_line1 = form.addressLine1.data
        note.address_line2 = form.addressLine2.data
        note.city = form.city.data
        note.state = form.state.data
        note.postal_code = form.postalCode.data
        note.country = form.country.data
        note.marital_status = form.maritalStatus.data
        note.spouse_name = form.spouseName.data
        note.spouse_grad_year = form.spouseGradYear.data
        note.marry_date = form.marryDate.data
        note.employer = form.employer.data
        note.position = form.position.data
        note.non_g_education = form.nonGEducation.data
        note.additional_updates = form.additionalUpdates.data
        note.volunteer_opportunities = ', '.join(form.volunteerChoices.data)
        note.other_volunteer = form.otherVolunteer.data
        note.class_note = form.AlumniClassNote.data

        existing = form.existing_image.data
        if existing:
            note.image_filename = existing
            print(f"[DEBUG] Preserving existing image: {existing}")
        else:
            note.image_filename = None
            print("[DEBUG] No existing image found or image removed.")
        
        db.session.commit()
        flash('Entry updated successfully.', 'success')
    else:
        flash('There was an error submitting the form. Please check the fields.', 'danger')

    return redirect(url_for('dashboard.dashboard_AlumniClassNotes'))


@dashboard_bp.route('/memoriam')
@login_required
def dashboard_memoriam():
    return render_template('admin_panel/memoriam.html')