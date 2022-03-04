import os, secrets
from PIL import Image
from datetime import datetime, timedelta
from flask import render_template, url_for, flash, redirect, request
from website import app, db, bcrypt, mail
from website.models import User, Role, Sport, Match, Timeperiod
from website.forms import (RegistrationForm, LoginForm, UpdateAccountForm, CreateMatchForm, 
                        UpdateMatchForm, FilterMatchForm, RequestResetForm, ResetPasswordForm)
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from sqlalchemy import or_, and_, func

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

    if request.method == 'POST': 
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
            login_user(user, remember=True)
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Check your email and password!', 'danger')
    return render_template('login.html',
                        title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
            sender='noreply@sportbuddy.com', recipients=[user.email])

    msg.body = f'''To reset your password, visit the following link:
{ url_for('reset_password', token=token, _external=True) }

If you did not make this request then simply ignore this email.
'''
    mail.send(msg)

@app.route("/reset_password_request", methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('login'))

    return render_template('reset_password_request.html', title='Reset Password Request', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('The token is invalid or expired', 'warning')
        return redirect(url_for('reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(
                                    form.password.data).decode('utf-8')

            user.password = hashed_password
            db.session.commit()

            flash('Your password has been updated!', 'success')
            return redirect(url_for('login'))

    return render_template('reset_password.html', title='Reset Password', form=form)



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
        #form.date.data = datetime.today() +  timedelta(days=1)
        pass
    elif request.method == 'POST':
        if form.validate_on_submit():
            match = Match(title=form.title.data,
                description=form.description.data,
                date=form.date.data, location=form.location.data,
                sport_id=form.sport_id.data,
                time_period_id=form.time_period.data,
                owner=current_user)

            db.session.add(match)
            db.session.commit()

            flash('Your match has been created!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Your match has not been created! Check your inputs', 'danger')
    return render_template('create_update_match.html', title='Create Match', form=form, legend='Create')


# Show a list of existing matches
@app.route("/match/find") #sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss
@app.route("/match/find/<int:sport_id>/<int:time_period_id>/<date>/<title>/<location>/<description>")
@login_required
def find_match(sport_id=0, time_period_id=0, date=None, title=None, location=None, description=None):
    page = request.args.get('page', 1, type=int)

    # Builds the search query
    # FIND MATCH IS STILL NOT WORKING PROPERLY GRR!!!!!!!!!!!!!!!!!!!!!!!!!!
    #subquery = 
    #query = and_(Match.date >= datetime.now(),
    #    func.count(Match.players) < Match.players_maxnumber)
    query = or_(Match.date >= datetime.now(), 0)

    if sport_id != 0:
        query = and_(query, Match.sport_id == sport_id)
    
    if time_period_id != 0:
        query = and_(query, Match.time_period_id == time_period_id)

    if date != None:
        query = and_(query, Match.date == date)

    if title != None:
        query = and_(query, Match.title.like("%" + title + "%"))
        '''
    if location != None or location == "":
        query = and_(query, Match.location.like('%' + str(location) + '%'))

    if description != None or description != "":
        query = and_(query, Match.description.like('%' + str(description) + '%'))
    '''
    '''
    if sport_id == None:
        matches = Match.query.filter(Match.date >= datetime.now()) \
            .order_by(Match.date.asc()).paginate(page=page, per_page=2)
    else:
        matches = Match.query.filter(Match.date >= datetime.now(), \
            Match.sport_id == sport_id) \
            .order_by(Match.date.asc()).paginate(page=page, per_page=2)
    '''
    matches = Match.query.filter(query) \
            .order_by(Match.date.asc()) \
            .paginate(page=page, per_page=2)

    print("teste " + str(title))

    return render_template('find_match.html', title='Find Match', matches=matches)

# Filter a list of existing matches
@app.route("/match/filter", methods=['GET', 'POST'])
@login_required
def filter_match():
    form = FilterMatchForm()

    sport_list = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]
    sport_list.insert(0, (0, "All Sports"))
    form.sport_id.choices = sport_list
    time_period_list = [(0, "All Periods"), (1, "Morning"),
                        (2, "Afternoon"), (3, "Evening"),
                        (4, "Night")]
    form.time_period.choices = time_period_list

    if request.method == 'POST':
        if form.validate_on_submit():
            return redirect(url_for('find_match', sport_id=form.sport_id.data, time_period_id=form.time_period.data,
                    date=form.date.data, title=form.title.data))#, location=form.location.data, description=form.description.data))

    return render_template('create_update_match.html', title='Filter Match', form=form)


# Show details of a single match
@app.route("/match/<int:match_id>/details")
@login_required
def details_match(match_id):
    match = Match.query.get_or_404(match_id)

    # Join Button
    join_flag = True
    player_number = len(match.players) + 1 # +1 is the owner
    if current_user in match.players or player_number >= match.players_maxnumber:
        join_flag = False

    return render_template('details_match.html', title='Match Details', match=match, flag=join_flag, player_number=player_number)

# Join a match as a player
@app.route("/match/<int:match_id>/join", methods=['POST'])
@login_required
def join_match(match_id):
    match = Match.query.get_or_404(match_id)

    if current_user == match.owner:
        flash('You have already joined!', 'danger')
        # from flask import abort
        # abort(403) # 403 = forbidden access
        return redirect(url_for('details_match', match_id=match.id))

    if len(match.players) >= match.players_maxnumber:
        flash('This match is full!', 'danger')
        # from flask import abort
        # abort(403) # 403 = forbidden access
        return redirect(url_for('details_match', match_id=match.id))

    match.players.append(current_user)
    db.session.commit()

    flash('You have joined!', 'success')
    return redirect(url_for('details_match', match_id=match.id))

# Quit a match as a player
@app.route("/match/<int:match_id>/quit", methods=['POST'])
@login_required
def quit_match(match_id):
    match = Match.query.get_or_404(match_id)

    if current_user == match.owner:
        flash('You cannot quit a match that you have created!', 'danger')
        # from flask import abort
        # abort(403) # 403 = forbidden access
        return redirect(url_for('details_match', match_id=match.id))

    if current_user not in match.players:
        flash('You are not in this match!', 'danger')
        # from flask import abort
        # abort(403) # 403 = forbidden access
        return redirect(url_for('details_match', match_id=match.id))

    match.players.remove(current_user)
    db.session.commit()

    flash('You have quit the match!', 'success')
    return redirect(url_for('details_match', match_id=match.id))

# Remove a player from a match
@app.route("/match/<int:match_id>/remove/<int:player_id>", methods=['POST'])
@login_required
def remove_player_match(match_id, player_id):
    match = Match.query.get_or_404(match_id)
    player = User.query.get_or_404(player_id)

    if current_user != match.owner:
        flash('You are not allowed to remove other players!', 'danger')
        # from flask import abort
        # abort(403) # 403 = forbidden access
        return redirect(url_for('details_match', match_id=match.id))

    if player not in match.players:
        flash('This player is not in this match!', 'danger')
        # from flask import abort
        # abort(403) # 403 = forbidden access
        return redirect(url_for('details_match', match_id=match.id))

    match.players.remove(player)
    db.session.commit()

    flash('You have removed the player ' + player.name + ' from the match!', 'success')
    return redirect(url_for('details_match', match_id=match.id))

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
    # same for time period
    time_period_list = [(1, "Morning"), (2, "Afternoon"),
                        (3, "Evening"), (4, "Night")]
    time_period_list.remove((match.timeperiod.id, match.timeperiod.name))
    time_period_list.insert(0, (match.timeperiod.id, match.timeperiod.name))
    form.time_period.choices = time_period_list

    # Update match in database (method = POST)
    if form.validate_on_submit():
        match.title = form.title.data
        match.description = form.description.data
        match.date = form.date.data
        match.location = form.location.data
        match.sport_id = form.sport_id.data
        match.time_period_id = form.time_period.data
        db.session.commit()

        flash('Your match has been updated!', 'success')
        return redirect(url_for('details_match', match_id=match.id))

    # Populate form (method = GET)
    elif request.method == 'GET':
        form.title.data = match.title
        form.description.data = match.description
        form.date.data = match.date
        form.location.data = match.location

    return render_template('create_update_match.html', title='Update Match', form=form, legend='Update', match=match)


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





































@app.route("/teste")
def teste():
    print (os.getenv('MAIL_PASS'))
    print (os.environ.get("SECRET_KEY"))
    return redirect(url_for('index'))






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
    
    # Create three timeperiods
    timeperiod_1 = Timeperiod(name='Morning')
    timeperiod_2 = Timeperiod(name='Afternoon')
    timeperiod_3 = Timeperiod(name='Evening')
    timeperiod_4 = Timeperiod(name='Night')
    db.session.add(timeperiod_1)
    db.session.add(timeperiod_2)
    db.session.add(timeperiod_3)
    db.session.add(timeperiod_4)
    db.session.commit()

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
    sport_3 = Sport(name='Fencing')
    sport_4 = Sport(name='Judo')
    sport_5 = Sport(name='Volleyball')
    sport_6 = Sport(name='Boxing')

    db.session.add(sport_1)
    db.session.add(sport_2)
    db.session.add(sport_3)
    db.session.add(sport_4)
    db.session.add(sport_5)
    db.session.add(sport_6)

    db.session.commit()
    
    '''
    # Create one standard match
    match_1 = Match(title='title', sport_id=1, user_id=1)
    db.session.add(match_1)
    db.session.commit()
    '''
    return redirect(url_for('index'))