from flask import Blueprint, render_template, url_for, flash, redirect, request
from website import db
from website.models import Sport, Coach
from website.coaches.forms import UpdateCoachAccountForm, FilterCoachForm
from website.main.utils import save_picture
from flask_login import current_user, login_required
from sqlalchemy import or_, and_


coaches = Blueprint('coaches', __name__)


@coaches.route("/coach/account", methods=['GET', 'POST'])
@login_required
def coach_account():
    if current_user.role.name != "Coach":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('main.index'))

    coach = Coach.query.filter_by(id=current_user.id).first()
    
    form = UpdateCoachAccountForm()
    form.sports.choices = [(row.id, row.name) for row 
                                    in Sport.query.order_by('name')]

    if form.validate_on_submit():
        if form.card.data:
            card_file = save_picture(form.card.data, 400, 400)
            coach.card_file = card_file

        coach.hourly_rate = round(form.hourly_rate.data, 2)
        print("TESTE \n\n")
        print(form.hourly_rate.data)
        print(type(form.hourly_rate.data))
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
        return redirect(url_for('coaches.coach_account'))

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


# Show a list of existing coaches
@coaches.route("/coach/find")
@coaches.route("/coach/find/<int:sport_id>/<int:gender_id>/<hourly_rate>/<name>/<int:page>")
@login_required
def find_coach(page=1, gender_id=0, sport_id=0, hourly_rate=0, name="-"):
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('main.index'))

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
@coaches.route("/coach/filter", methods=['GET', 'POST'])
@login_required
def filter_coach():
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('main.index'))

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

            return redirect(url_for('coaches.find_coach', sport_id=sport_id, name=name,
                    gender_id=gender, hourly_rate=hourly_rate, page=1))

    return render_template('filter_coach.html', title='Filter Coach', form=form)


# Show details of a single coach
@coaches.route("/coach/<int:coach_id>/details")
@login_required
def details_coach(coach_id):
    if current_user.role.name == "Company":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('main.index'))

    coach = Coach.query.get_or_404(coach_id)

    if coach.gender_id == 1:
        gender = "Male"
    else:
        gender = "Female"

    return render_template('details_coach.html', title='Coach Details', coach=coach, gender=gender)


# Shows the plans available for the coaches
@coaches.route("/coach/plans", methods=['GET', 'POST'])
@login_required
def plans():
    if current_user.role.name != "Coach":
        flash('Your cannot access this page!', 'danger')
        return redirect(url_for('main.index'))

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