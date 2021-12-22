from flask import render_template, url_for, flash, redirect
from website import app, db, bcrypt
from website.models import User
from website.forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, current_user, login_required

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

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

@app.route("/login",  methods=['GET', 'POST'])
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


@login_required
@app.route("/account")
def account():
    
    return render_template('account.html', title='Account')