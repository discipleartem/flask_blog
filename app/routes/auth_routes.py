from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.forms.auth_forms import LoginForm, RegistrationForm
from app import login_manager

# Add url_prefix='/auth' to match test paths
bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

"""
session['_user_id'] is set by Flask-Login's login_user()
before_app_request handler loads the user into g.user
The test can access g.user after making a request
"""

@bp.before_app_request
def load_logged_in_user():
    """Load user object into g.user"""
    user_id = session.get('_user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.get_by_id(user_id)



@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('articles.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Successfully logged in', 'success')
            return redirect(url_for('articles.index'))
        flash('Invalid username or password', 'danger')

    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('articles.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if User.create_user(form.username.data, form.password.data):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        flash('Username already taken', 'danger')

    elif request.method == 'POST':
        # Add explicit validation error messages
        if not form.username.data:
            flash('Username is required.', 'danger')

        if not form.password.data:
            flash('Password is required.', 'danger')

        # Display any other validation errors from the form
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'danger')

    return render_template('auth/register.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out', 'success')
    return redirect(url_for('articles.index'))