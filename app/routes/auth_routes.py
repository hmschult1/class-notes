from flask import Blueprint, render_template, redirect, request, flash, url_for, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app.authForms import LoginForm
from app.authModels import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard.dashboard_home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out. Thank you for using the Geneva Web Portal!', 'info')
    return redirect(url_for('auth.login'))