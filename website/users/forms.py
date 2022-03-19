from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField, EmailField,
		SelectField)
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
		ValidationError)
from flask_login import current_user
from website.models import User

# User registration
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

	# email validation
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('This e-mail is already been used')

# Login User form
class LoginForm(FlaskForm):
	email = StringField('Email',
				validators=[DataRequired(), Email()])

	password = PasswordField('Password',
				validators=[DataRequired()])

	submit = SubmitField('Login')

# Request reset password User form
class RequestResetForm(FlaskForm):
	email = StringField('Email',
				validators=[DataRequired(), Email()])

	submit = SubmitField('Request Password Reset')

	# email validation
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('This e-mail is not linked to any account')

# Reset password User form
class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password',
				validators=[DataRequired()])

	confirm_password = PasswordField('Confirm Password',
				validators=[DataRequired(), EqualTo('password')])

	submit = SubmitField('Reset Password')

# Update User form
class UpdateAccountForm(FlaskForm):
	name = StringField('Name',
				validators=[DataRequired(), Length(min=2, max=20)])

	email = EmailField('E-mail Adress',
				validators=[DataRequired(), Email()])

	picture = FileField('Profile Picture',
					validators=[FileAllowed(['jpg', 'jpeg', 'png'])])

	submit = SubmitField('Update')

	# email validation
	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('This e-mail is already been used')
