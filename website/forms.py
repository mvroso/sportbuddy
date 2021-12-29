from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, EmailField, DateTimeField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
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
	email = StringField('email',
				validators=[DataRequired(), Email()])
	password = PasswordField('Password',
				validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')



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


# Implementing MatchForm Mixin
class MatchFormMixin():

	title = StringField('Title',
					validators=[DataRequired(), Length(min=2, max=50)])
	description = TextAreaField('Description')

	date = DateTimeField('Match Date', format='%Y-%m-%d %H:%M:%S')#, render_kw={"placeholder": "test"})

	location = StringField('Location', validators=[Length(min=2, max=50)])

	sport_id = SelectField('Sport', validators=[DataRequired()])

	# Date validation
	def validate_date(self, date):
		if date.data < datetime.now():
			raise ValidationError("The date cannot be in the past!")

# Create new match Form
class CreateMatchForm(FlaskForm, MatchFormMixin):

    submit = SubmitField('Create Match')

# Update match Form
class UpdateMatchForm(FlaskForm, MatchFormMixin):

    submit = SubmitField('Update Match')

    