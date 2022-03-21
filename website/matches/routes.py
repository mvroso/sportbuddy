from flask import (Blueprint, render_template, url_for, flash, redirect,
                    request, abort)
from datetime import datetime, timedelta
from website import db
from website.models import User, Sport, Match
from website.matches.forms import (CreateMatchForm, UpdateMatchForm,
        FilterMatchForm)
from flask_login import current_user, login_required
from sqlalchemy import or_, and_

# Declares blueprint
matches = Blueprint('matches', __name__)


# Create a new match
@matches.route("/match/create", methods=['GET', 'POST'])
@login_required
def create_match():
    if current_user.role.name == "Company":
        abort(403) # 403 = forbidden access

    # initalizes the form and sport choices
    form = CreateMatchForm()
    form.sport_id.choices = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]
    
    if request.method == 'GET':
        # date input = tomorrow
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
            return redirect(url_for('matches.find'))
        else:
            flash('Your match has not been created! Check your inputs', 'danger')
    return render_template('create_update_match.html', title='Create Match', form=form, legend='Create')


# Show a list of existing matches
@matches.route("/match/find")
@matches.route("/match/find/<int:sport_id>/<int:time_period_id>/<date>/<match_title>/<location>/<description>/<int:players_maxnumber>/<int:page>")
@login_required
def find_match(page=1, sport_id=0, time_period_id=0, date="-", match_title="-", location="-", description="-", players_maxnumber=0):
    if current_user.role.name == "Company":
        abort(403) # 403 = forbidden access

    # builds the search query
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
@matches.route("/match/filter", methods=['GET', 'POST'])
@login_required
def filter_match():
    if current_user.role.name == "Company":
        abort(403) # 403 = forbidden access

    # initalizes the form, sport and timeperiod choices
    form = FilterMatchForm()
    sport_list = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]
    sport_list.insert(0, (0, "All Sports"))
    form.sport_id.choices = sport_list
    time_period_list = [(0, "All Periods"), (1, "Morning"),
                        (2, "Afternoon"), (3, "Evening"),
                        (4, "Night")]
    form.time_period.choices = time_period_list

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


        return redirect(url_for('matches.find_match', sport_id=sport_id, time_period_id=time_period_id,
                date=date, match_title=match_title, location=location, description=description,
                players_maxnumber=players_maxnumber, page=1))

    return render_template('create_update_match.html', title='Filter Match', form=form)


# Summarizes the matches that the user is involved
@matches.route("/match/summary")
@matches.route("/match/summary/<int:sport_id>/<int:time_period_id>/<date>/<match_title>/<location>/<description>/<int:players_maxnumber>/<int:page>")
@login_required
def summary_match(page=1, sport_id=0, time_period_id=0, date="-", match_title="-", location="-", description="-", players_maxnumber=0):
    if current_user.role.name == "Company":
        abort(403) # 403 = forbidden access

    # builds the search query
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
@matches.route("/match/<int:match_id>/details")
@login_required
def details_match(match_id):
    match = Match.query.get_or_404(match_id)

    if current_user.role.name == "Company":
        abort(403) # 403 = forbidden access

    # join match button
    able_to_join = True
    player_number = len(match.players) + 1 # +1 is the owner
    if current_user in match.players or player_number >= match.players_maxnumber:
        able_to_join = False

    return render_template('details_match.html', title='Match Details', match=match, able_to_join=able_to_join, player_number=player_number)


# Join a match as a player
@matches.route("/match/<int:match_id>/join", methods=['POST'])
@login_required
def join_match(match_id):
    match = Match.query.get_or_404(match_id)

    if current_user.role.name == "Company":
        abort(403) # 403 = forbidden access

    if current_user == match.owner:
        abort(403) # 403 = forbidden access

    if len(match.players) >= match.players_maxnumber:

        flash('This match is full!', 'danger')
        return redirect(url_for('matches.details_match', match_id=match.id))

    match.players.append(current_user)
    db.session.commit()

    flash('You have joined!', 'success')
    return redirect(url_for('matches.details_match', match_id=match.id))


# Quit a match as a player
@matches.route("/match/<int:match_id>/quit", methods=['POST'])
@login_required
def quit_match(match_id):
    match = Match.query.get_or_404(match_id)

    if current_user.role.name == "Company":
        abort(403) # 403 = forbidden access

    if current_user == match.owner:
        abort(403) # 403 = forbidden access

    if current_user not in match.players:

        flash('You are not in this match!', 'danger')
        return redirect(url_for('matches.details_match', match_id=match.id))

    match.players.remove(current_user)
    db.session.commit()

    flash('You have quit the match!', 'success')
    return redirect(url_for('matches.details_match', match_id=match.id))


# Remove a player from a match
@matches.route("/match/<int:match_id>/remove/<int:player_id>", methods=['POST'])
@login_required
def remove_player_match(match_id, player_id):
    match = Match.query.get_or_404(match_id)
    player = User.query.get_or_404(player_id)

    if current_user != match.owner:
        abort(403) # 403 = forbidden access

    if player not in match.players:

        flash('This player is not in this match!', 'danger')
        return redirect(url_for('matches.details_match', match_id=match.id))

    match.players.remove(player)
    db.session.commit()

    flash('You have removed the player ' + player.name + ' from the match!', 'success')
    return redirect(url_for('matches.details_match', match_id=match.id))


# Update a single match that you own
@matches.route("/match/<int:match_id>/update", methods=['GET', 'POST'])
@login_required
def update_match(match_id):
    match = Match.query.get_or_404(match_id)

    if current_user != match.owner:
        abort(403) # 403 = forbidden access
    
    # initalizes the form, sport and timeperiod choices (current sport and timeperiod are first)
    form = UpdateMatchForm()
    sport_list = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]
    sport_list.remove((match.sport.id, match.sport.name))
    sport_list.insert(0, (match.sport.id, match.sport.name))
    form.sport_id.choices = sport_list
    time_period_list = [(1, "Morning"), (2, "Afternoon"),
                        (3, "Evening"), (4, "Night")]
    time_period_list.remove((match.timeperiod.id, match.timeperiod.name))
    time_period_list.insert(0, (match.timeperiod.id, match.timeperiod.name))
    form.time_period.choices = time_period_list

    # update match in database
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

        return redirect(url_for('matches.details_match', match_id=match.id))

    # populate form
    elif request.method == 'GET':

        form.title.data = match.title
        form.description.data = match.description
        form.date.data = match.date
        form.players_maxnumber.data = match.players_maxnumber
        form.location.data = match.location

    return render_template('create_update_match.html', title='Update Match', form=form, legend='Update', match=match)


# Delete a single match that you own
@matches.route("/match/<int:match_id>/delete", methods=['POST'])
@login_required
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)

    if current_user != match.owner:
        abort(403) # 403 = forbidden access

    db.session.delete(match)
    db.session.commit()
    
    flash('Your match has been deleted!', 'success')
    return redirect(url_for('matches.find_match'))