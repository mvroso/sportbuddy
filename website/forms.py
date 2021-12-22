from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from website.models import User

class RegistrationForm(FlaskForm):
	name = StringField('Name',
				validators=[DataRequired(), Length(min=2, max=20)])
	email = EmailField('E-mail Adress',
				validators=[DataRequired(), Email()])
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