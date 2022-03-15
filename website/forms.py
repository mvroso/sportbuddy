from datetime import date as date_func
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, EmailField, DateField, TextAreaField, SelectField, SelectMultipleField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, Optional, NumberRange
from flask_login import current_user
from website.models import User, Sport

class RegistrationForm(FlaskForm):
	name = StringField('Name',
				validators=[DataRequired(), Length(min=2, max=20)])
	email = EmailField('E-mail Adress',
				validators=[DataRequired(), Email()])
	gender = SelectField('Gender',
				validators=[DataRequired()],
				choices=[(1, "Male"), (2, "Female"),
						(3, "Not applicable")])
	role = SelectField('Role',
				validators=[DataRequired()],
				choices=[(1, "Common"), (2, "Coach"),
						(3, "Company")])
	password = PasswordField('Password',
				validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',
				validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('This e-mail is already been used')


class LoginForm(FlaskForm):
	email = StringField('Email',
				validators=[DataRequired(), Email()])
	password = PasswordField('Password',
				validators=[DataRequired()])
	submit = SubmitField('Login')

class RequestResetForm(FlaskForm):
	email = StringField('Email',
				validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('This e-mail is not linked to any account')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password',
				validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',
				validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Reset Password')

class UpdateAccountForm(FlaskForm):
	name = StringField('Name',
				validators=[DataRequired(), Length(min=2, max=20)])
	email = EmailField('E-mail Adress',
				validators=[DataRequired(), Email()])
	picture = FileField('Profile Picture',
					validators=[FileAllowed(['jpg', 'png'])])
	submit = SubmitField('Update')

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('This e-mail is already been used')


class UpdateCoachAccountForm(FlaskForm):
	hourly_rate = DecimalField('Hourly Rate',
					validators=[DataRequired(),
							NumberRange(min=1, max=10000)])
	description = TextAreaField('Description')

	phone_number = StringField('Phone Number')
	
	sports = SelectMultipleField('Sports', coerce=int)

	card = FileField('Card Picture',
					validators=[FileAllowed(['jpg', 'png'])])

	submit = SubmitField('Update')

class FilterCoachForm(FlaskForm):
	name = StringField('Name',
				validators=[Optional()])
	hourly_rate = DecimalField('Maximum Hourly Rate',
					validators=[Optional()])

	gender = SelectField('Gender',
				validators=[Optional()],
				choices=[(0, "All Genders"), (1, "Male"),
						(2, "Female")])

	sport_id = SelectField('Sport', coerce=int)

	submit = SubmitField('Filter Coach')

# Implementing MatchForm Mixin
class MatchFormMixin():

	title = StringField('Title',
					validators=[DataRequired(), Length(min=2, max=50)])
	description = TextAreaField('Description')

	# DateTime is deprecated
	date = DateField('Match Date', format='%Y-%m-%d',
					validators=[DataRequired()])

	time_period = SelectField('Time Period',
				validators=[DataRequired()],
				choices=[(1, "Morning"), (2, "Afternoon"),
						(3, "Evening"), (4, "Night")])

	location = StringField('Location', validators=[Length(min=2, max=50)])
	
	players_maxnumber = IntegerField('Number of Players',
					validators=[DataRequired(),	NumberRange(min=1, max=30)])

	sport_id = SelectField('Sport', coerce=int)

	# Date validation
	def validate_date(self, date):
		if date.data < date_func.today():
			raise ValidationError("The date cannot be in the past!")

# Create new match Form
class CreateMatchForm(FlaskForm, MatchFormMixin):

    submit = SubmitField('Create Match')

# Update match Form
class UpdateMatchForm(FlaskForm, MatchFormMixin):

    submit = SubmitField('Update Match')


# Filter match Form
class FilterMatchForm(FlaskForm):


	title = StringField('Title',
					validators=[Optional()])
	description = TextAreaField('Description')

	# DateTime is deprecated
	date = DateField('Match Date', format='%Y-%m-%d',
					validators=[Optional()])

	time_period = SelectField('Time Period',
				validators=[Optional()],
				choices=[(1, "Morning"), (2, "Afternoon"),
						(3, "Evening"), (4, "Night")])

	location = StringField('Location', validators=[Optional()])

	players_maxnumber = IntegerField('Number of Players',
					validators=[Optional()])

	sport_id = SelectField('Sport', validators=[Optional()])

	submit = SubmitField('Filter Match')


class EventFormMixin():

	title = StringField('Title',
					validators=[DataRequired(), Length(min=2, max=50)])
	description = TextAreaField('Description')

	date = DateField('Event Date', format='%Y-%m-%d',
					validators=[DataRequired()])

	price = DecimalField('Price',
					validators=[DataRequired(),
							NumberRange(min=0, max=10000)], places=2)

	attendees_maxnumber = IntegerField('Number of Attendees',
					validators=[DataRequired(),	NumberRange(min=20, max=3000)])

	location = StringField('Location', validators=[Length(min=2, max=50)])

	background = FileField('Background Picture',
					validators=[FileAllowed(['jpg', 'png'])])

	sport_id = SelectField('Sport', coerce=int)

	# Date validation
	def validate_date(self, date):
		if date.data < date_func.today():
			raise ValidationError("The date cannot be in the past!")

# Create new Event Form
class CreateEventForm(FlaskForm, EventFormMixin):

    submit = SubmitField('Create Event')

# Update Event Form
class UpdateEventForm(FlaskForm, EventFormMixin):

    submit = SubmitField('Update Event')


# Filter event Form
class FilterEventForm(FlaskForm):


	title = StringField('Title',
					validators=[Optional()])

	date = DateField('Event Date', format='%Y-%m-%d',
					validators=[Optional()])

	price = DecimalField('Maximum Price',
					validators=[Optional()])

	location = StringField('Location', validators=[Optional()])

	sport_id = SelectField('Sport', validators=[Optional()])

	submit = SubmitField('Filter Event')