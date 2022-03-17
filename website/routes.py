import os, secrets
from PIL import Image
from datetime import datetime, timedelta
from flask import render_template, url_for, flash, redirect, request
from website import app, db, bcrypt, mail
from website.models import User, Role, Sport, Match, Timeperiod, Coach, Event
from website.forms import (RegistrationForm, LoginForm, UpdateAccountForm, CreateMatchForm, 
                        UpdateMatchForm, FilterMatchForm, RequestResetForm, ResetPasswordForm,
                        UpdateCoachAccountForm, FilterCoachForm, CreateEventForm, UpdateEventForm,
                        FilterEventForm)
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

@app.route("/about")
def about():
    return render_template('about.html', title='About')

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
            # Common = "1" or Company = "3"
            if form.role.data == "1" or form.role.data == "3":
                user = User(name=form.name.data,
                        email=form.email.data,
                        gender_id=form.gender.data,
                        role_id=form.role.data,
                        password=hashed_password)
                # Add user to database
                db.session.add(user)

            # Coach = "2"
            elif form.role.data == "2":
                coach = Coach(name=form.name.data,
                        email=form.email.data,
                        gender_id=form.gender.data,
                        role_id=form.role.data,
                        password=hashed_password)
                db.session.add(coach)


            # Commit changes to database
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

    msg.body = f"To reset your password, visit the following link:\n\n" \
            f"{url_for('reset_password', token=token, _external=True)}\n\n" \
            f"If you did not make this request then simply ignore this email."

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
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user.password = hashed_password
        db.session.commit()

        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', title='Reset Password', form=form)



# Save user uploaded picture in /static/img/profile_pictures
def save_picture(form_picture, width, height):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,
                'static/img/profile_pictures', picture_fn)
    
    # Resize picture with Pillow
    output_size = (width, height)
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
            picture_file = save_picture(form.picture.data, 200, 200)
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

@app.route("/coach/account", methods=['GET', 'POST'])
@login_required
def coach_account():
    if current_user.role.name != "Coach":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

    coach = Coach.query.filter_by(id=current_user.id).first()
    
    form = UpdateCoachAccountForm()
    form.sports.choices = [(row.id, row.name) for row 
                                    in Sport.query.order_by('name')]

    if form.validate_on_submit():
        if form.card.data:
            card_file = save_picture(form.card.data, 400, 400)
            coach.card_file = card_file

        coach.hourly_rate = round(form.hourly_rate.data, 2)
        coach.phone_number = form.phone_number.data
        coach.description = form.description.data

        coach.sports = []
        if form.sports.data != [] and type(form.sports.data) is list:
            for sport_id in form.sports.data:
                sport = Sport.query.get(sport_id)
                coach.sports.append(sport)
        elif type(form.sports.data) is int:
            sport = Sport.query.get(form.sports.data)
            coach.sports.append(sport)

        db.session.commit()

        flash('Your coach account has been updated!', 'success')
        return redirect(url_for('coach_account'))

    elif request.method == 'GET':
        form.hourly_rate.data = coach.hourly_rate
        form.phone_number.data = coach.phone_number
        form.description.data = coach.description
        # sports
        sport_id_list = []
        for sport in coach.sports:
            sport_id_list.append(sport.id)
        form.sports.data = sport_id_list

        if coach.plan_id == 2:
            plan = "Premium"
        else:
            plan = "Free"

    # Get current user profile picture
    image_file = url_for('static', filename='img/profile_pictures/' +
                        current_user.image_file)
    return render_template('coach_account.html', title='Coach Account',
                        image_file=image_file, form=form, plan=plan)

# Create a new match
@app.route("/match/create", methods=['GET', 'POST'])
@login_required
def create_match():
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

    form = CreateMatchForm()
    form.sport_id.choices = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]
    if request.method == 'GET':        
        form.date.data = datetime.today() +  timedelta(days=1)
    elif request.method == 'POST':
        if form.validate_on_submit():
            match = Match(title=form.title.data,
                description=form.description.data,
                date=form.date.data,
                players_maxnumber=form.players_maxnumber.data,
                location=form.location.data,
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
@app.route("/match/find")
@app.route("/match/find/<int:sport_id>/<int:time_period_id>/<date>/<match_title>/<location>/<description>/<int:players_maxnumber>/<int:page>")
@login_required
def find_match(page=1, sport_id=0, time_period_id=0, date="-", match_title="-", location="-", description="-", players_maxnumber=0):
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

    # Builds the search query
    query = or_(Match.date >= datetime.now())

    if sport_id != 0:
        query = and_(query, Match.sport_id == sport_id)
    
    if time_period_id != 0:
        query = and_(query, Match.time_period_id == time_period_id)

    if date != "-":
        query = and_(query, Match.date == date)

    if match_title != "-":
        query = and_(query, Match.title.like("%" + match_title + "%"))
        
    if location != "-":
        query = and_(query, Match.location.like('%' + location + '%'))

    if description != "-":
        query = and_(query, Match.description.like('%' + description + '%'))

    if players_maxnumber != 0:
        query = and_(query, Match.players_maxnumber >= players_maxnumber)
    
    
    matches = Match.query.filter(query) \
            .order_by(Match.date.asc()) \
            .paginate(page=page, per_page=6)

    return render_template('find_match.html', title='Find Match', 
        matches=matches,
        sport_id=sport_id, time_period_id=time_period_id, date=date,
        match_title=match_title, location=location, description=description,
        players_maxnumber=players_maxnumber)

# Filter a list of existing matches
@app.route("/match/filter", methods=['GET', 'POST'])
@login_required
def filter_match():
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

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

            sport_id = form.sport_id.data
            time_period_id = form.time_period.data
            date = form.date.data
            match_title = form.title.data
            location = form.location.data
            description = form.description.data
            players_maxnumber = form.players_maxnumber.data

            if date == None:
                date = "-"
            if not match_title:
                match_title = "-"
            if not location:
                location = "-"
            if not description:
                description = "-"
            if players_maxnumber == None:
                players_maxnumber = 0


            return redirect(url_for('find_match', sport_id=sport_id, time_period_id=time_period_id,
                    date=date, match_title=match_title, location=location, description=description,
                    players_maxnumber=players_maxnumber, page=1))

    return render_template('create_update_match.html', title='Filter Match', form=form)


# Summarizes the matches that the user is involved
@app.route("/match/summary")
@app.route("/match/summary/<int:sport_id>/<int:time_period_id>/<date>/<match_title>/<location>/<description>/<int:players_maxnumber>/<int:page>")
@login_required
def summary_match(page=1, sport_id=0, time_period_id=0, date="-", match_title="-", location="-", description="-", players_maxnumber=0):
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

    #page = request.args.get('page', 1, type=int)

    # Builds the search query
    query = or_(Match.owner == current_user, Match.players.any(id=current_user.id))

    matches = Match.query.filter(query) \
            .order_by(Match.date.asc()) \
            .paginate(page=page, per_page=6)

    return render_template('find_match.html', title='Summary Match', 
        matches=matches,
        sport_id=sport_id, time_period_id=time_period_id, date=date,
        match_title=match_title, location=location, description=description,
        players_maxnumber=players_maxnumber)

# Show details of a single match
@app.route("/match/<int:match_id>/details")
@login_required
def details_match(match_id):
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

    match = Match.query.get_or_404(match_id)

    # Join Button
    able_to_join = True
    player_number = len(match.players) + 1 # +1 is the owner
    if current_user in match.players or player_number >= match.players_maxnumber:
        able_to_join = False

    return render_template('details_match.html', title='Match Details', match=match, able_to_join=able_to_join, player_number=player_number)

# Join a match as a player
@app.route("/match/<int:match_id>/join", methods=['POST'])
@login_required
def join_match(match_id):
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

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
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

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
        if form.players_maxnumber.data < len(match.players) + 1:
            flash('There are players in this match!', 'danger')
        else:
            match.title = form.title.data
            match.description = form.description.data
            match.date = form.date.data
            match.players_maxnumber = form.players_maxnumber.data
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
        form.players_maxnumber.data = match.players_maxnumber
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

# Show a list of existing coaches
@app.route("/coach/find")
@app.route("/coach/find/<int:sport_id>/<int:gender_id>/<hourly_rate>/<name>/<int:page>")
@login_required
def find_coach(page=1, gender_id=0, sport_id=0, hourly_rate=0, name="-"):
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

    # Builds the search query
    query = or_(Coach.hourly_rate >= 0)

    if sport_id != 0:
        query = and_(query, Coach.sports.any(id=sport_id))

    if gender_id != 0:
        query = and_(query, Coach.gender_id == gender_id)

    if float(hourly_rate) != 0:
        query = and_(query, Coach.hourly_rate <= hourly_rate)

    if name != "-":
        query = and_(query, Coach.name.like("%" + name + "%"))

    coaches = Coach.query.filter(query, Coach.plan_id == 1) \
            .order_by(Coach.name.asc()) \
            .paginate(page=page, per_page=4)

    premium_coaches = Coach.query.filter(query, Coach.plan_id == 2) \
            .order_by(Coach.name.asc()) \
            .limit(4)

    return render_template('find_coach.html', title='Find Coach', 
        coaches=coaches, premium_coaches=premium_coaches, 
        sport_id=sport_id, gender_id=gender_id, hourly_rate=hourly_rate,
        name=name)


# Filter a list of existing coaches
@app.route("/coach/filter", methods=['GET', 'POST'])
@login_required
def filter_coach():
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

    form = FilterCoachForm()

    sport_list = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]
    sport_list.insert(0, (0, "All Sports"))
    form.sport_id.choices = sport_list

    if request.method == 'POST':
        if form.validate_on_submit():

            name = form.name.data
            sport_id = form.sport_id.data
            gender = form.gender.data
            hourly_rate = form.hourly_rate.data

            if not name:
                name = "-"
            if hourly_rate == None:
                hourly_rate = 0

            return redirect(url_for('find_coach', sport_id=sport_id, name=name,
                    gender_id=gender, hourly_rate=hourly_rate, page=1))

    return render_template('filter_coach.html', title='Filter Coach', form=form)


# Show details of a single coach
@app.route("/coach/<int:coach_id>/details")
@login_required
def details_coach(coach_id):
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

    coach = Coach.query.get_or_404(coach_id)

    if coach.gender_id == 1:
        gender = "Male"
    else:
        gender = "Female"

    return render_template('details_coach.html', title='Coach Details', coach=coach, gender=gender)


# Shows the plans available for the coaches
@app.route("/coach/plans", methods=['GET', 'POST'])
@login_required
def plans():
    if current_user.role.name != "Coach":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

    if request.method == "POST":
        coach = Coach.query.filter_by(id=current_user.id).first()

        plan = ""
        if request.form.get("selectfree") != None:
            coach.plan_id = 1
            plan = "Free"
        elif request.form.get("selectpremium") != None:
            coach.plan_id = 2
            plan = "Premium"

        db.session.commit()
        flash("You have switched to the " + plan + " plan!", "success")

    return render_template('plans.html', title='Plans')



# Create a new event
@app.route("/event/create", methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role.name != "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

    form = CreateEventForm()
    form.sport_id.choices = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]
    if request.method == 'GET':        
        form.date.data = datetime.today() +  timedelta(days=1)
    elif request.method == 'POST':
        if form.validate_on_submit():
            event = Event(title=form.title.data,
                description=form.description.data,
                date=form.date.data,
                price=round(form.price.data, 2),
                attendees_maxnumber=form.attendees_maxnumber.data,
                location=form.location.data,
                sport_id=form.sport_id.data,
                owner=current_user)

            if form.background.data:
                background_file = save_picture(form.background.data, 1320, 440)
                event.background_file = background_file

            db.session.add(event)
            db.session.commit()

            flash('Your event has been created!', 'success')
            return redirect(url_for('find_event'))
        else:
            flash('Your event has not been created! Check your inputs', 'danger')
    return render_template('create_update_event.html', title='Create Event', form=form, legend='Create')

# Show a list of existing events
@app.route("/event/find")
@app.route("/event/find/<int:sport_id>/<event_title>/<date>/<price>/<location>/<int:page>")
@login_required
def find_event(page=1, sport_id=0, event_title="-", date="-", price=0, location="-"):
    
    # Builds the search query
    query = or_(Event.date >= datetime.now())
    
    if sport_id != 0:
        query = and_(query, Event.sport_id == sport_id)

    if event_title != "-":
        query = and_(query, Event.title.like("%" + event_title + "%"))

    if date != "-":
        query = and_(query, Event.date == date)

    if float(price) != 0:
        query = and_(query, Event.price <= price)
        
    if location != "-":
        query = and_(query, Event.location.like('%' + location + '%'))

    events = Event.query.filter(query) \
            .order_by(Event.date.asc()) \
            .paginate(page=page, per_page=6)

    return render_template('find_event.html', title='Find Event', 
            events=events,
            sport_id=sport_id, event_title=event_title, date=date,
            price=price, location=location)


# Filter a list of existing events
@app.route("/event/filter", methods=['GET', 'POST'])
@login_required
def filter_event():
        
    form = FilterEventForm()

    sport_list = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]
    sport_list.insert(0, (0, "All Sports"))
    form.sport_id.choices = sport_list

    if request.method == 'POST':
        if form.validate_on_submit():

            sport_id = form.sport_id.data
            event_title = form.title.data
            date = form.date.data
            price = form.price.data
            location = form.location.data

            if not event_title:
                event_title = "-"
            if not date:
                date = "-"
            if not price:
                price = 0
            if not location:
                location = "-"

            return redirect(url_for('find_event', sport_id=sport_id, 
                    event_title=event_title, date=date, 
                    price=price, location=location, page=1))

    return render_template('filter_event.html', title='Filter Event', form=form)



# Show details of a single event
@app.route("/event/<int:event_id>/details")
@login_required
def details_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Buy Ticket Button
    buy_ticket = True
    attendees_number = len(event.attendees)
    if current_user.role.name == "Company" or attendees_number >= event.attendees_maxnumber or current_user in event.attendees:
        buy_ticket = False

    return render_template('details_event.html', title='Event Details', event=event, buy_ticket=buy_ticket, attendees_number=attendees_number)

# Update a single event that you own
@app.route("/event/<int:event_id>/update", methods=['GET', 'POST'])
@login_required
def update_event(event_id):
    event = Event.query.get_or_404(event_id)

    if current_user != event.owner:
        flash('You are not the owner of that event!', 'danger')
        # from flask import abort
        # abort(403) # 403 = forbidden access
        return redirect(url_for('find_event'))
    
    form = UpdateEventForm()
    # workaround for listing the current sport first
    sport_list = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]
    sport_list.remove((event.sport.id, event.sport.name))
    sport_list.insert(0, (event.sport.id, event.sport.name))
    form.sport_id.choices = sport_list

    # Update event in database (method = POST)
    if form.validate_on_submit():
        if form.attendees_maxnumber.data < len(event.attendees) + 1:
            flash('There are attendees in this event!', 'danger')
        else:
            event.title = form.title.data
            event.description = form.description.data
            event.date = form.date.data
            event.price = round(form.price.data, 2)
            event.attendees_maxnumber = form.attendees_maxnumber.data
            event.location = form.location.data
            event.sport_id = form.sport_id.data

            if form.background.data:
                background_file = save_picture(form.background.data, 1320, 440)
                event.background_file = background_file

            db.session.commit()
            flash('Your event has been updated!', 'success')
        return redirect(url_for('details_event', event_id=event.id))

    # Populate form (method = GET)
    elif request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.date.data = event.date
        form.price.data = event.price
        form.attendees_maxnumber.data = event.attendees_maxnumber
        form.location.data = event.location

    return render_template('create_update_event.html', title='Update Event', form=form, legend='Update', event=event)

# Delete a single event that you own
@app.route("/event/<int:event_id>/delete", methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    if current_user != event.owner:
        flash('You are not the owner of that event!', 'danger')
        # from flask import abort
        # abort(403) # 403 = forbidden access
        return redirect(url_for('find_event'))

    db.session.delete(event)
    db.session.commit()
    flash('Your event has been deleted!', 'success')
    return redirect(url_for('find_event'))

# Buy a ticket for an event
@app.route("/event/<int:event_id>/buy_ticket", methods=['POST'])
@login_required
def buy_ticket_event(event_id):
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('index'))

    event = Event.query.get_or_404(event_id)

    if current_user == event.owner:
        flash('You cannot buy a ticket!', 'danger')
        # from flask import abort
        # abort(403) # 403 = forbidden access
        return redirect(url_for('details_event', event_id=event.id))

    if len(event.attendees) >= event.attendees_maxnumber:
        flash('This event is full!', 'danger')
        # from flask import abort
        # abort(403) # 403 = forbidden access
        return redirect(url_for('details_event', event_id=event.id))

    event.attendees.append(current_user)
    db.session.commit()

    flash('You have bought a ticket!', 'success')
    return redirect(url_for('details_event', event_id=event.id))


# Summarizes the events that the user is involved
@app.route("/event/summary")
@app.route("/event/summary/<int:sport_id>/<event_title>/<date>/<price>/<location>/<int:page>")
@login_required
def summary_event(page=1, sport_id=0, event_title="-", date="-", price=0, location="-"):

    # Builds the search query
    query = or_(Event.owner == current_user, Event.attendees.any(id=current_user.id))

    events = Event.query.filter(query) \
            .order_by(Event.date.asc()) \
            .paginate(page=page, per_page=6)

    return render_template('find_event.html', title='Summary Event', 
            events=events,
            sport_id=sport_id, event_title=event_title, date=date,
            price=price, location=location)


















@app.route("/teste")
def teste():

    hashed_password = bcrypt.generate_password_hash(
                                    "123").decode('utf-8')

    user_1 = User(name='Susanna Onio',
            email='susannaonio@teste.com',
            password=hashed_password,
            gender_id=2)

    db.session.add(user_1)

    user_2 = User(name='Agenore Bruno',
                email='agenorebruno@teste.com',
                password=hashed_password,
                gender_id=1)

    db.session.add(user_2)

    user_3 = User(name='Amalio Davide',
                email='amaliodavide@teste.com',
                password=hashed_password,
                gender_id=1)

    db.session.add(user_3)

    db.session.commit()

    match_1 = Match(title='Beach Volley with Friends',
                description=('We play every day to train for a competition '
                    'in October. If you are interested come join us!'),
                date=datetime.strptime('2022-04-02', "%Y-%m-%d").date(),
                players_maxnumber=4,
                location='CUS Torino',
                sport_id=7,
                time_period_id=3,
                owner=user_1)
    
    match_1.players.append(user_2)
    match_1.players.append(user_3)
    
    db.session.add(match_1)

    db.session.commit()

    return redirect(url_for('index'))




# Shortcut to insert data in the database
@app.route("/insertdata")
def insertdata():
    
    # Create four timeperiods
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
    
    
    # Create standard sports
    sport_1 = Sport(name='Archery')
    db.session.add(sport_1)

    sport_2 = Sport(name='Artistic Gymnastics')
    db.session.add(sport_2)

    sport_3 = Sport(name='Artistic Swimming')
    db.session.add(sport_3)

    sport_4 = Sport(name='Athletics')
    db.session.add(sport_4)

    sport_5 = Sport(name='Badminton')
    db.session.add(sport_5)

    sport_6 = Sport(name='Basketball')
    db.session.add(sport_6)

    sport_7 = Sport(name='Beach Volleyball')
    db.session.add(sport_7)

    sport_8 = Sport(name='Biathlon')
    db.session.add(sport_8)

    sport_9 = Sport(name='BMX Racing')
    db.session.add(sport_9)

    sport_10 = Sport(name='Boxing')
    db.session.add(sport_10)

    sport_11 = Sport(name='Diving')
    db.session.add(sport_11)

    sport_12 = Sport(name='Equestrian')
    db.session.add(sport_12)

    sport_13 = Sport(name='Fencing')
    db.session.add(sport_13)

    sport_14 = Sport(name='Golf')
    db.session.add(sport_14)

    sport_15 = Sport(name='Handball')
    db.session.add(sport_15)

    sport_16 = Sport(name='Hockey')
    db.session.add(sport_16)

    sport_17 = Sport(name='Judo')
    db.session.add(sport_17)

    sport_18 = Sport(name='Kayak Flatwater')
    db.session.add(sport_18)

    sport_19 = Sport(name='Kayak Slalom')
    db.session.add(sport_19)

    sport_20 = Sport(name='Marathon Swimming')
    db.session.add(sport_20)

    sport_21 = Sport(name='Modern Pentatlhlon')
    db.session.add(sport_21)

    sport_22 = Sport(name='Montain Bike')
    db.session.add(sport_22)

    sport_23 = Sport(name='Rhythmic Gymnastics')
    db.session.add(sport_23)

    sport_24 = Sport(name='Road Cycling')
    db.session.add(sport_24)

    sport_25 = Sport(name='Rowing')
    db.session.add(sport_25)

    sport_26 = Sport(name='Rugby')
    db.session.add(sport_26)

    sport_27 = Sport(name='Sailing')
    db.session.add(sport_27)

    sport_28 = Sport(name='Soccer')
    db.session.add(sport_28)

    sport_29 = Sport(name='Surfing')
    db.session.add(sport_29)

    sport_30 = Sport(name='Swimming')
    db.session.add(sport_30)

    sport_31 = Sport(name='Table Tennis')
    db.session.add(sport_31)

    sport_32 = Sport(name='Tennis')
    db.session.add(sport_32)

    sport_33 = Sport(name='Track Cycling')
    db.session.add(sport_33)

    sport_34 = Sport(name='Trampoline')
    db.session.add(sport_34)

    sport_35 = Sport(name='Triathlon')
    db.session.add(sport_35)

    sport_36 = Sport(name='Volleyball')
    db.session.add(sport_36)

    sport_37 = Sport(name='Water Polo')
    db.session.add(sport_37)

    sport_38 = Sport(name='Weight Lifting')
    db.session.add(sport_38)

    sport_39 = Sport(name='Wrestling')
    db.session.add(sport_39)

    db.session.commit()

    # Create standard users
    hashed_password = bcrypt.generate_password_hash(
                                    "123").decode('utf-8')

    user_1 = User(name='Susanna Onio',
            email='susannaonio@teste.com',
            password=hashed_password,
            gender_id=2)

    db.session.add(user_1)

    user_2 = User(name='Agenore Bruno',
                email='agenorebruno@teste.com',
                password=hashed_password,
                gender_id=1)

    db.session.add(user_2)

    user_3 = User(name='Amalio Davide',
                email='amaliodavide@teste.com',
                password=hashed_password,
                gender_id=1)

    db.session.add(user_3)

    user_4 = User(name='Sandra Romani',
                email='sandraromani@teste.com',
                password=hashed_password,
                gender_id=2)

    db.session.add(user_4)

    user_5 = User(name='Maria Pia Udinese',
                email='mariapiaudinese@teste.com',
                password=hashed_password,
                gender_id=2)

    db.session.add(user_5)

    user_6 = User(name='Ornella Lettiere',
                email='ornellalettiere@teste.com',
                password=hashed_password,
                gender_id=2)

    db.session.add(user_6)

    user_7 = User(name='Bernardo Genovesi',
                email='bernardogenovesi@teste.com',
                password=hashed_password,
                gender_id=1)

    db.session.add(user_7)

    user_8 = User(name='Matteo Cattaneo',
                email='matteocattaneo@teste.com',
                password=hashed_password,
                gender_id=1)

    db.session.add(user_8)

    user_9 = User(name='Antonio Greece',
                email='antoniogreece',
                password=hashed_password,
                gender_id=1)

    db.session.add(user_9)

    user_10 = User(name='Ignazio Loggia',
                email='ignaziologgia@teste.com',
                password=hashed_password,
                gender_id=1)

    db.session.add(user_10)

    user_11 = User(name='Raffaella Genovesi',
                email='raffaellagenovesi@teste.com',
                password=hashed_password,
                gender_id=2)

    db.session.add(user_11)

    user_12 = User(name='Cecilia Calabrese',
                email='ceciliacalabrese@teste.com',
                password=hashed_password,
                gender_id=2)

    db.session.add(user_12)

    user_13 = User(name='Innocenzo Pisano',
                email='innocenzopisano@teste.com',
                password=hashed_password,
                gender_id=1)

    db.session.add(user_13)

    user_14 = User(name='Amerigo Udinesi',
                email='amerigoudinesi@teste.com',
                password=hashed_password,
                gender_id=1)

    db.session.add(user_14)

    user_15 = User(name='Aloisa Trentino',
                email='aloisatrentino@teste.com',
                password=hashed_password,
                gender_id=2)

    db.session.add(user_15)

    user_16 = User(name='Enrico Russo',
                email='enricorusso@teste.com',
                password=hashed_password,
                gender_id=1)

    db.session.add(user_16)

    user_17 = User(name='Gennaro Milano',
                email='gennaromilano@teste.com',
                password=hashed_password,
                gender_id=1)

    db.session.add(user_17)

    user_18 = User(name='Erminia Udinese',
                email='erminiaudinese@teste.com',
                password=hashed_password,
                gender_id=2)

    db.session.add(user_18)

    user_19 = User(name='Brigida Milani',
                email='brigidamilani@teste.com',
                password=hashed_password,
                gender_id=2)

    db.session.add(user_19)

    user_20 = User(name='Raffaele Lombardi',
                email='raffaelelombardi@teste.com',
                password=hashed_password,
                gender_id=1)

    db.session.add(user_20)

    db.session.commit()

    # Create standard coaches
    descr = ("I am a skilled Coach with 10 plus years of experience "
        "and in-depth knowledge of college athletic program regulations "
        "and mentoring of athletes. I consistently motivate and inspire "
        "players to bring their best to every game. My mission as a coach "
        "is to take the gifts young athletes have been blessed with and "
        "turn them into skills that will help them succeed on and off "
        "the court. I am an expert in recognizing and working on players' "
        "weakness and strengths by developing customized training sessions.")

    coach_1 = Coach(name='Adelaide Fiorentini',
                        email='adelaidefiorentini@teste.com',
                        gender_id=2,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=40.00, 
                        phone_number='3315532635', 
                        image_file='image-4.jpg',
                        description = descr)
    db.session.add(coach_1)



    coach_2 = Coach(name='Alceo Marchesi',
                        email='alceomarchesi@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=45.00, 
                        phone_number='3337432636', 
                        image_file='image-1.jpg',
                        description = descr)
    db.session.add(coach_2)

                        
    coach_3 = Coach(name='Siro Marcelo',
                        email='siromarcelo@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=80.00, 
                        phone_number='3404332567', 
                        image_file='image-2.jpg',
                        description = descr)
    db.session.add(coach_3)

                        
    coach_4 = Coach(name='Adele Baresi',
                        email='adelebaresi@teste.com',
                        gender_id=2,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=75.00, 
                        phone_number='3452435622', 
                        image_file='image-5.jpg',
                        description = descr)
    db.session.add(coach_4)

                        
    coach_5 = Coach(name='Gabriel Sanches',
                        email='gabrielsanches@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=40.00, 
                        phone_number='3314432435', 
                        image_file='image-3.jpg',
                        description = descr)
    db.session.add(coach_5)

                        
    coach_6 = Coach(name='Agatino Fallaci',
                        email='agatinofallaci@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=55.00, 
                        phone_number='3317312436', 
                        image_file='image-1.jpg',
                        description = descr)
    db.session.add(coach_6)

                        
    coach_7 = Coach(name='Gianetto Mazzi',
                        email='gianettomazzi@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=60.00, 
                        phone_number='3474432599', 
                        image_file='image-2.jpg',
                        description = descr)
    db.session.add(coach_7)


                        
    coach_8 = Coach(name='Facondo Lombardo',
                        email='facondolombardo@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=90.00, 
                        phone_number='3664532892', 
                        image_file='image-3.jpg',
                        description = descr)
    db.session.add(coach_8)

                        
    coach_9 = Coach(name='Vittoria Toscano',
                        email='vittoriatoscano@teste.com',
                        gender_id=2,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=75.00, 
                        phone_number='3317922835', 
                        image_file='image-6.jpg',
                        description = descr)
    db.session.add(coach_9)

                        
    coach_10 = Coach(name='Marcella Davide',
                        email='marcelladavide@teste.com',
                        gender_id=2,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=50.00, 
                        phone_number='3397292987', 
                        image_file='image-4.jpg',
                        description = descr)
    db.session.add(coach_10)

                        
    coach_11 = Coach(name='Cornelio Dellucci',
                        email='corneliodellucci@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=30.00, 
                        phone_number='3334451932', 
                        image_file='image-1.jpg',
                        description = descr)
    db.session.add(coach_11)

                        
    coach_12 = Coach(name='Diego Greco',
                        email='diegogreco@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=100.00, 
                        phone_number='3234932237', 
                        image_file='image-2.jpg',
                        description = descr)
    db.session.add(coach_12)

                        
    coach_13 = Coach(name='Leda Mancini',
                        email='ledamancini@teste.com',
                        gender_id=2,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=60.00, 
                        phone_number='3664533536', 
                        image_file='image-5.jpg',
                        description = descr)
    db.session.add(coach_13)

                        
    coach_14 = Coach(name='Luciano Palermo',
                        email='lucianopalermo@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=45.00, 
                        phone_number='3338732945', 
                        image_file='image-3.jpg',
                        description = descr)
    db.session.add(coach_14)

                        
    coach_15 = Coach(name='Egidio Belluci',
                        email='egidiobelluci@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=85.00, 
                        phone_number='3884634435', 
                        image_file='image-1.jpg',
                        description = descr)
    db.session.add(coach_15)

                        
    coach_16 = Coach(name='Roberto Mancini',
                        email='robertomancini@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=95.00, 
                        phone_number='3464643235', 
                        image_file='image-2.jpg',
                        description = descr)
    db.session.add(coach_16)

                        
    coach_17 = Coach(name='Prospero Russo',
                        email='prosperorusso@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=49.00, 
                        phone_number='3317832933', 
                        image_file='image-3.jpg',
                        description = descr)
    db.session.add(coach_17)

                        
    coach_18 = Coach(name='Aldo Longo',
                        email='aldolongo@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=55.00, 
                        phone_number='3335634431', 
                        image_file='image-1.jpg',
                        description = descr)
    db.session.add(coach_18)

                        
    coach_19 = Coach(name='Pasqualina Lombardi',
                        email='pasqualinalombardi@teste.com',
                        gender_id=2,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=2,
                        hourly_rate=60.00, 
                        phone_number='3317412936', 
                        image_file='image-6.jpg',
                        description = descr)
    db.session.add(coach_19)

                        
    coach_20 = Coach(name='Giulia Li Fonti',
                        email='giulialifonti@teste.com',
                        gender_id=2,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=2,
                        hourly_rate=50.00, 
                        phone_number='3604433935', 
                        image_file='image-4.jpg',
                        description = descr)
    db.session.add(coach_20)

                        
    coach_21 = Coach(name='Aladino Esposito',
                        email='aladinoesposito@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=120.00, 
                        phone_number='3314937255', 
                        image_file='image-2.jpg',
                        description = descr)
    db.session.add(coach_21)

                        
    coach_22 = Coach(name='Norma Sal',
                        email='normasal@teste.com',
                        gender_id=2,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=2,
                        hourly_rate=45.00, 
                        phone_number='3357042039', 
                        image_file='image-5.jpg',
                        description = descr)
    db.session.add(coach_22)

                        
    coach_23 = Coach(name='Consuelo Lucchesi',
                        email='consuelolucchesi@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=15.00, 
                        phone_number='3334902705', 
                        image_file='image-3.jpg',
                        description = descr)
    db.session.add(coach_23)

                        
    coach_24 = Coach(name='Ubalda Lorenzo',
                        email='ubaldalorenzo@teste.com',
                        gender_id=2,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=2,
                        hourly_rate=95.00, 
                        phone_number='3376534237', 
                        image_file='image-6.jpg',
                        description = descr)
    db.session.add(coach_24)

                        
    coach_25 = Coach(name='Emanuelle Pisano',
                        email='emanuellepisano@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=2,
                        hourly_rate=70.00, 
                        phone_number='3397232921', 
                        image_file='image-1.jpg',
                        description = descr)
    db.session.add(coach_25)

                        
    coach_26 = Coach(name='Dora Genovese',
                        email='doragenovese@teste.com',
                        gender_id=2,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=110.00, 
                        phone_number='3319944713', 
                        image_file='image-4.jpg',
                        description = descr)
    db.session.add(coach_26)

                        
    coach_27 = Coach(name='Matteo Lombardi',
                        email='matteolombardi@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=2,
                        hourly_rate=60.00, 
                        phone_number='3701572448', 
                        image_file='image-3.jpg',
                        description = descr)
    db.session.add(coach_27)

                        
    coach_28 = Coach(name='Rodrigo Napolitani',
                        email='rodrigonapolitani@teste.com',
                        gender_id=1,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=2,
                        hourly_rate=55.00, 
                        phone_number='3312985355', 
                        image_file='image-2.jpg',
                        description = descr)
    db.session.add(coach_28)

                        
    coach_29 = Coach(name='Berta Milano',
                        email='bertamilano@teste.com',
                        gender_id=2,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=55.00, 
                        phone_number='3314317866', 
                        image_file='image-5.jpg',
                        description = descr)
    db.session.add(coach_29)

                        
    coach_30 = Coach(name='Paola Longo',
                        email='paolalongo@teste.com',
                        gender_id=2,
                        role_id=2, 
                        password=hashed_password,
                        plan_id=1,
                        hourly_rate=90.00, 
                        phone_number='3336732961', 
                        image_file='image-6.jpg',
                        description = descr)
    db.session.add(coach_30)

    db.session.commit()

    match_1 = Match(title='Beach Volley with Friends',
                description=('We play every day to train for a competition '
                    'in October. If you are interested come join us!'),
                date=datetime.strptime('2022-04-02', "%Y-%m-%d").date(),
                players_maxnumber=4,
                location='CUS Torino',
                sport_id=7,
                time_period_id=3,
                owner=user_1)
    
    match_1.players.append(user_2)
    match_1.players.append(user_3)
    
    db.session.add(match_1)

    match_2 = Match(title='Judo Training Session!',
                description=("I'm trying to get my belt promotion so I'm "
                    "looking for people to train with!! Come join me!"),
                date=datetime.strptime('2022-04-13', "%Y-%m-%d").date(),
                players_maxnumber=6,
                location='CUS Torino',
                sport_id=17,
                time_period_id=1,
                owner=user_5)
    
    match_2.players.append(user_4)
    match_2.players.append(user_3)
    
    db.session.add(match_2)

    match_3 = Match(title='Soccer with the Piqué Blinders',
                description=('Hello guys, me and my team (the Piqué Blinders) '
                    'are looking for friends to play soccer. Join us!'),
                date=datetime.strptime('2022-05-01', "%Y-%m-%d").date(),
                players_maxnumber=10,
                location='Parco Valentino',
                sport_id=28,
                time_period_id=4,
                owner=user_2)
    
    match_3.players.append(user_4)
    match_3.players.append(user_5)
    
    db.session.add(match_3)

    match_4 = Match(title='Boxing in Torino!',
                description=('Ciao!!! Looking for a boxing partner for a '
                    'training session next week. See you in the ring!!'),
                date=datetime.strptime('2022-04-22', "%Y-%m-%d").date(),
                players_maxnumber=2,
                location='CUS Torino',
                sport_id=10,
                time_period_id=1,
                owner=user_1)
    
    match_4.players.append(user_2)
    
    
    db.session.add(match_4)

    match_5 = Match(title='Road to NBA!',
                description=("Do you think you can beat the Dunkin' Donuts? "
                    "Come find out!!!"),
                date=datetime.strptime('2022-05-12', "%Y-%m-%d").date(),
                players_maxnumber=10,
                location='Campi da Basket Braccini',
                sport_id=6,
                time_period_id=3,
                owner=user_6)
    
    match_5.players.append(user_7)
    match_5.players.append(user_3)
    
    db.session.add(match_5)

    match_6 = Match(title='Rugby team recruiting!',
                description=('Hey big guy! Come to our recruiting session '
                    'to show us your skills!!!'),
                date=datetime.strptime('2022-04-14', "%Y-%m-%d").date(),
                players_maxnumber=20,
                location='Parco Valentino',
                sport_id=26,
                time_period_id=2,
                owner=user_7)
    
    match_6.players.append(user_10)
    match_6.players.append(user_5)
    
    db.session.add(match_6)

    match_7 = Match(title='Sailing Event - Coconut Grove, Miami',
                description=('It is a-boat time you start learning to sail! '
                    'Come join us!!!'),
                date=datetime.strptime('2022-06-15', "%Y-%m-%d").date(),
                players_maxnumber=25,
                location='Coconut Grove',
                sport_id=27,
                time_period_id=1,
                owner=user_4)
    
    match_7.players.append(user_15)
    match_7.players.append(user_13)
    match_7.players.append(user_11)
    
    db.session.add(match_7)

    match_8 = Match(title='Volleyball with Friends',
                description=('We play every day to train for a competition '
                    'in October. If you are interested come join us!'),
                date=datetime.strptime('2022-06-02', "%Y-%m-%d").date(),
                players_maxnumber=8,
                location='LÉMAN ARCHERY',
                sport_id=1,
                time_period_id=2,
                owner=user_7)
    
    match_8.players.append(user_2)
    match_8.players.append(user_9)

    db.session.add(match_8)

    db.session.commit()

    flash('The database was populated', 'info')
    return redirect(url_for('index'))