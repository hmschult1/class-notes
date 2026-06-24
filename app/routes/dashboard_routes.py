from flask import Blueprint, render_template, render_template_string, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import AlumniClassNote, AlumniUpdate, Alumni
from werkzeug.security import check_password_hash, generate_password_hash
from app.auth_forms import ChangePasswordForm
from app.dashboard_forms import EditFullEntryForm
from app import db

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# DASHBOARD ROUTES
@dashboard_bp.route('/')
@login_required
def dashboard_home():
    updates = AlumniUpdate.query.order_by(AlumniUpdate.submitted_at.desc()).all()
    return render_template('admin_panel/landing.html', updates=updates)

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
    entries = (
        AlumniClassNote.query.join(AlumniUpdate)
        .order_by(AlumniUpdate.submitted_at.desc())
        .all()
    )
    form = EditFullEntryForm()
    return render_template('admin_panel/class-notes.html', entries=entries, form=form)

@dashboard_bp.route('/class-notes/<int:note_id>/edit', methods=['POST'])
@login_required
def edit_class_note(note_id):
    form = EditFullEntryForm()

    if form.validate_on_submit():
        note = AlumniClassNote.query.get_or_404(note_id)
        update = note.alumni_update
        alumnus = update.alumnus

        # Populate fields from form into related objects
        note.viewed = True

        alumnus.first_name = form.first_name.data
        alumnus.last_name = form.last_name.data
        alumnus.maiden_name = form.maiden_name.data
        alumnus.email = form.email.data
        alumnus.phone = form.phone.data

        # Address: update first address if present, else create
        if alumnus.addresses:
            addr = alumnus.addresses[0]
            addr.address_line1 = form.address_line1.data
            addr.address_line2 = form.address_line2.data
            addr.city = form.city.data
            addr.state = form.state.data
            addr.postal_code = form.postal_code.data
            addr.country = form.country.data
        else:
            from app.models import AlumniAddress
            addr = AlumniAddress(
                alumnus_id=alumnus.id,
                address_line1=form.address_line1.data,
                address_line2=form.address_line2.data,
                city=form.city.data,
                state=form.state.data,
                postal_code=form.postal_code.data,
                country=form.country.data,
            )
            db.session.add(addr)

        update.additional_updates = form.additional_updates.data
        update.volunteer_choices = form.volunteer_choices.data or []
        update.other_volunteer = form.other_volunteer.data

        note.class_note_text = form.class_note_text.data

        existing = form.existing_image.data
        if existing:
            note.image_filename = existing
        else:
            note.image_filename = None

        db.session.commit()
        flash('Entry updated successfully.', 'success')
    else:
        flash('There was an error submitting the form. Please check the fields.', 'danger')

    return redirect(url_for('dashboard.dashboard_AlumniClassNotes'))


@dashboard_bp.route('/memoriam')
@login_required
def dashboard_memoriam():
    return render_template('admin_panel/memoriam.html')