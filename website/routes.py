import os, secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from website import app, db, bcrypt
from website.models import User, Role, Sport, Match
from website.forms import RegistrationForm, LoginForm, UpdateAccountForm, CreateMatchForm
from flask_login import login_user, logout_user, current_user, login_required

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html', title='Home')

@app.route("/contact")
def contact():
    return render_template('contact.html', title='Contact')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    # Registration form is valid
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
                                form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data,
                password=hashed_password)

        # Add user to database
        db.session.add(user)
        db.session.commit()

        flash('Your account has been successfully created!', 'success')
        return redirect(url_for('login'))
    else:
        flash('Your account was not created. Check your inputs!', 'danger')

    return render_template('register.html',
                        title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
                            user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Check your email and password!', 'danger')
    return render_template('login.html',
                        title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

# Save user uploaded picture in /static/img file
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,
                'static/img/profile_pictures', picture_fn)
    
    # Resize picture with Pillow
    output_size = (125, 125)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_fn


@login_required
@app.route("/account", methods=['GET', 'POST'])
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email

    # Get current user profile picture
    image_file = url_for('static', filename='img/profile_pictures/' +
                        current_user.image_file)
    return render_template('account.html', title='Account',
                        image_file=image_file, form=form)

# Create a new match
@login_required
@app.route("/match/create", methods=['GET', 'POST'])
def create_match():
    form = CreateMatchForm()
    if form.validate_on_submit():
        flash('Your match has been created!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Your match has been created!', 'danger')
    return render_template('create_match.html', title='New Match', form=form)




# Shortcut to insert data in the database
@app.route("/insertdata")
def insertdata():
    '''
    # Create three standard roles
    role_1 = Role(name='Common')
    role_2 = Role(name='Coach')
    role_3 = Role(name='Company')
    db.session.add(role_1)
    db.session.add(role_2)
    db.session.add(role_3)
    db.session.commit()
    '''
    '''
    # Create three standard sports
    sport_1 = Sport(name='Basketball')
    sport_2 = Sport(name='Tennis')
    sport_3 = Sport(name='Chess')
    db.session.add(sport_1)
    db.session.add(sport_2)
    db.session.add(sport_3)
    db.session.commit()
    '''
    '''
    # Create one standard match
    match_1 = Match(title='title', sport_id=1, user_id=1)
    db.session.add(match_1)
    db.session.commit()
    '''
    return redirect(url_for('index'))