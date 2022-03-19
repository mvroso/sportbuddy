from flask import Blueprint, render_template, url_for, flash, redirect, request
from website import db, bcrypt
from website.models import User, Coach
from website.users.forms import (RegistrationForm, LoginForm,
        UpdateAccountForm, RequestResetForm, ResetPasswordForm)
from website.users.utils import send_reset_email
from website.main.utils import save_picture
from flask_login import login_user, logout_user, current_user, login_required

# Declares blueprint
users = Blueprint('users', __name__)


# Register a new user
@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:

        flash('You are already logged in!', 'danger')
        return redirect(url_for('main.index'))

    # initializes the form
    form = RegistrationForm()

    if request.method == 'POST': 
        if form.validate_on_submit():
            # hashes user password
            hashed_password = bcrypt.generate_password_hash(
                                    form.password.data).decode('utf-8')

            # Common = "1" or Company = "3"
            if form.role.data == "1" or form.role.data == "3":

                user = User(name=form.name.data,
                        email=form.email.data,
                        gender_id=form.gender.data,
                        role_id=form.role.data,
                        password=hashed_password)

                db.session.add(user)

            # Coach = "2"
            elif form.role.data == "2":

                coach = Coach(name=form.name.data,
                        email=form.email.data,
                        gender_id=form.gender.data,
                        role_id=form.role.data,
                        password=hashed_password)

                db.session.add(coach)

            db.session.commit()

            flash('Your account has been successfully created!', 'success')
            return redirect(url_for('users.login'))

        else:

            flash('Your account was not created. Check your inputs!', 'danger')

    return render_template('register.html',
                        title='Register', form=form)


# Login user
@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:

        flash('You are already logged in!', 'danger')
        return redirect(url_for('main.index'))

    # initializes the form
    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(
                            user.password, form.password.data):

            login_user(user, remember=True)
            return redirect(url_for('main.index'))

        else:

            flash('Login unsuccessful. Check your email and password!', 'danger')
    
    return render_template('login.html', title='Login', form=form)


# Logout user
@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('users.login'))


# Reset password request user
@users.route("/reset_password_request", methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:

        flash('You are already logged in!', 'danger')
        return redirect(url_for('main.index'))

    # initalizes the form
    form = RequestResetForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)

        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))

    return render_template('reset_password_request.html', title='Reset Password Request', form=form)


# Reset password user
@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:

        flash('You are already logged in!', 'danger')
        return redirect(url_for('main.index'))

    user = User.verify_reset_token(token)

    if user is None:

        flash('The token is invalid or expired', 'warning')
        return redirect(url_for('users.reset_password_request'))

    # initializes the form
    form = ResetPasswordForm()

    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password

        db.session.commit()

        flash('Your password has been updated!', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_password.html', title='Reset Password', form=form)


# Show current user account
@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    # initializes the form
    form = UpdateAccountForm()

    if form.validate_on_submit():
        # saves picture image and hash
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 200, 200)
            current_user.image_file = picture_file

        current_user.name = form.name.data
        current_user.email = form.email.data

        db.session.commit()

        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))

    elif request.method == 'GET':

        form.name.data = current_user.name
        form.email.data = current_user.email

    # Get current user profile picture
    image_file = url_for('static', filename='img/profile_pictures/' +
                        current_user.image_file)

    return render_template('account.html', title='Account',
                        image_file=image_file, form=form)