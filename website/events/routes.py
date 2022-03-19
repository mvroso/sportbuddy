from flask import (Blueprint, render_template, url_for, flash, redirect,
                    request, abort)
from datetime import datetime, timedelta
from website import db, bcrypt
from website.models import Sport, Event
from website.events.forms import (CreateEventForm, UpdateEventForm,
        FilterEventForm)
from website.main.utils import save_picture
from flask_login import current_user, login_required
from sqlalchemy import or_, and_

# Declares blueprint
events = Blueprint('events', __name__)


# Create a new event
@events.route("/event/create", methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role.name != "Company":
        abort(403) # 403 = forbidden access

    # initalizes the form and sport choices
    form = CreateEventForm()
    form.sport_id.choices = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]

    if request.method == 'GET':
        # date input = tomorrow
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

            # saves background image and hash
            if form.background.data:
                background_file = save_picture(form.background.data, 1320, 440)
                event.background_file = background_file

            db.session.add(event)
            db.session.commit()

            flash('Your event has been created!', 'success')
            return redirect(url_for('events.find_event'))

        else:
            flash('Your event has not been created! Check your inputs', 'danger')

    return render_template('create_update_event.html', title='Create Event', form=form, legend='Create')


# Show a list of existing events
@events.route("/event/find")
@events.route("/event/find/<int:sport_id>/<event_title>/<date>/<price>/<location>/<int:page>")
@login_required
def find_event(page=1, sport_id=0, event_title="-", date="-", price=0, location="-"):
    
    # builds the search query
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
@events.route("/event/filter", methods=['GET', 'POST'])
@login_required
def filter_event():
    # initalizes the form and sport choices
    form = FilterEventForm()
    sport_list = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]
    sport_list.insert(0, (0, "All Sports"))
    form.sport_id.choices = sport_list

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

        return redirect(url_for('events.find_event', sport_id=sport_id, 
                event_title=event_title, date=date, 
                price=price, location=location, page=1))

    return render_template('filter_event.html', title='Filter Event', form=form)


# Show details of a single event
@events.route("/event/<int:event_id>/details")
@login_required
def details_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # buy ticket button
    buy_ticket = True
    attendees_number = len(event.attendees)
    if current_user.role.name == "Company" or attendees_number >= event.attendees_maxnumber or current_user in event.attendees:
        buy_ticket = False

    return render_template('details_event.html', title='Event Details', event=event, buy_ticket=buy_ticket, attendees_number=attendees_number)


# Update a single event that you own
@events.route("/event/<int:event_id>/update", methods=['GET', 'POST'])
@login_required
def update_event(event_id):
    event = Event.query.get_or_404(event_id)

    if current_user != event.owner:
        abort(403) # 403 = forbidden access
    
    # initalizes the form and sport choices (current sport is first)
    form = UpdateEventForm()
    sport_list = [(row.id, row.name) for row 
                                in Sport.query.order_by('name')]
    sport_list.remove((event.sport.id, event.sport.name))
    sport_list.insert(0, (event.sport.id, event.sport.name))
    form.sport_id.choices = sport_list

    # update event in database
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

            # saves background image and hash
            if form.background.data:
                background_file = save_picture(form.background.data, 1320, 440)
                event.background_file = background_file

            db.session.commit()
            flash('Your event has been updated!', 'success')

        return redirect(url_for('events.details_event', event_id=event.id))

    # populate form
    elif request.method == 'GET':

        form.title.data = event.title
        form.description.data = event.description
        form.date.data = event.date
        form.price.data = event.price
        form.attendees_maxnumber.data = event.attendees_maxnumber
        form.location.data = event.location

    return render_template('create_update_event.html', title='Update Event', form=form, legend='Update', event=event)


# Delete a single event that you own
@events.route("/event/<int:event_id>/delete", methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    if current_user != event.owner:
        abort(403) # 403 = forbidden access

    db.session.delete(event)
    db.session.commit()

    flash('Your event has been deleted!', 'success')
    return redirect(url_for('events.find_event'))


# Buy a ticket for an event
@events.route("/event/<int:event_id>/buy_ticket", methods=['POST'])
@login_required
def buy_ticket_event(event_id):
    event = Event.query.get_or_404(event_id)

    if current_user.role.name == "Company":
        abort(403) # 403 = forbidden access

    if current_user == event.owner:
        abort(403) # 403 = forbidden access

    if len(event.attendees) >= event.attendees_maxnumber:

        flash('This event is full!', 'danger')
        return redirect(url_for('events.details_event', event_id=event.id))

    event.attendees.append(current_user)
    db.session.commit()

    flash('You have bought a ticket!', 'success')
    return redirect(url_for('events.details_event', event_id=event.id))


# Summarizes the events that the user is involved
@events.route("/event/summary")
@events.route("/event/summary/<int:sport_id>/<event_title>/<date>/<price>/<location>/<int:page>")
@login_required
def summary_event(page=1, sport_id=0, event_title="-", date="-", price=0, location="-"):

    # builds the search query
    query = or_(Event.owner == current_user, Event.attendees.any(id=current_user.id))

    events = Event.query.filter(query) \
            .order_by(Event.date.asc()) \
            .paginate(page=page, per_page=6)

    return render_template('find_event.html', title='Summary Event', 
            events=events,
            sport_id=sport_id, event_title=event_title, date=date,
            price=price, location=location)