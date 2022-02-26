import os, secrets
from PIL import Image
from datetime import datetime, timedelta
from flask import render_template, url_for, flash, redirect, request
from website import app, db, bcrypt
from website.models import User, Role, Sport, Match
from website.forms import RegistrationForm, LoginForm, UpdateAccountForm, CreateMatchForm, UpdateMatchForm
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


@app.route("/account", methods=['GET', 'POST'])
@login_required
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
@app.route("/match/create", methods=['GET', 'POST'])
@login_required
def create_match():
    form = CreateMatchForm()
    form.sport_id.choices = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]
    if request.method == 'GET':        
        # ***** RETIRAR ESSA LINHA UMA VEZ QUE O DATETIMEPICKER FOR ESCOLHIDO *****
        form.date.data = datetime.today() +  timedelta(days=1)
    elif request.method == 'POST':
        if form.validate_on_submit():
            match = Match(title=form.title.data,
                description=form.description.data,
                date=form.date.data, location=form.location.data,
                sport_id=form.sport_id.data,
                owner=current_user)

            db.session.add(match)
            db.session.commit()

            flash('Your match has been created!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Your match has not been created! Check your inputs', 'danger')
    return render_template('create_match.html', title='Create Match', form=form, legend='Create')


# Find an existing match
@app.route("/match/find")
@login_required
def find_match():
    matches = Match.query.all()
    return render_template('find_match.html', title='Find Match', matches=matches)

# Show details of a single match
@app.route("/match/<int:match_id>/details")
@login_required
def details_match(match_id):
    match = Match.query.get_or_404(match_id)
    return render_template('details_match.html', title='Match Details', match=match)


# Update a single match that you own
@app.route("/match/<int:match_id>/update", methods=['GET', 'POST'])
@login_required
def update_match(match_id):
    match = Match.query.get_or_404(match_id)

    if current_user != match.owner:
        flash('You are not the owner of that match!', 'danger')
        # from flask import abort
        # abort(403) # 403 = forbidden access
        return redirect(url_for('find_match'))
    
    form = UpdateMatchForm()
    # workaround for listing the current sport first
    sport_list = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]
    sport_list.remove((match.sport.id, match.sport.name))
    sport_list.insert(0, (match.sport.id, match.sport.name))
    form.sport_id.choices = sport_list

    # Update match in database (method = POST)
    if form.validate_on_submit():
        match.title = form.title.data
        match.description = form.description.data
        match.date = form.date.data
        match.location = form.location.data
        match.sport_id = form.sport_id.data
        db.session.commit()

        flash('Your match has been updated!', 'success')
        return redirect(url_for('details_match', match_id=match.id))

    # Populate form (method = GET)
    elif request.method == 'GET':
        form.title.data = match.title
        form.description.data = match.description
        form.date.data = match.date
        form.location.data = match.location

    return render_template('update_match.html', title='Update Match', form=form, legend='Update', match=match)


# Delete a single match that you own
@app.route("/match/<int:match_id>/delete", methods=['POST'])
@login_required
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)

    if current_user != match.owner:
        flash('You are not the owner of that match!', 'danger')
        # from flask import abort
        # abort(403) # 403 = forbidden access
        return redirect(url_for('find_match'))

    db.session.delete(match)
    db.session.commit()
    flash('Your match has been deleted!', 'success')
    return redirect(url_for('find_match'))











































# Shortcut to insert data in the database
@app.route("/insertdata")
def insertdata():
    '''
    gender_1 = Gender(name='Male')
    gender_2 = Gender(name='Female')
    gender_3 = Gender(name='Neutral')
    gender_4 = Gender(name='Not applicable')
    db.session.add(gender_1)
    db.session.add(gender_2)
    db.session.add(gender_3)
    db.session.add(gender_4)
    db.session.commit()
    '''
    
    # Create three standard roles
    role_1 = Role(name='Common')
    role_2 = Role(name='Coach')
    role_3 = Role(name='Company')
    db.session.add(role_1)
    db.session.add(role_2)
    db.session.add(role_3)
    db.session.commit()
    
    
    # Create three standard sports
    sport_1 = Sport(name='Basketball')
    sport_2 = Sport(name='Tennis')
    sport_3 = Sport(name='Chess')
    db.session.add(sport_1)
    db.session.add(sport_2)
    db.session.add(sport_3)
    db.session.commit()
    
    '''
    # Create one standard match
    match_1 = Match(title='title', sport_id=1, user_id=1)
    db.session.add(match_1)
    db.session.commit()
    '''
    return redirect(url_for('index'))