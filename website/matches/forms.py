from datetime import date as date_func
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, DateField, TextAreaField,
		SelectField, IntegerField)
from wtforms.validators import (DataRequired, Length, ValidationError,
		Optional, NumberRange)

# Mixin for create and update match
class MatchFormMixin():

	title = StringField('Title',
					validators=[DataRequired(), Length(min=2, max=50)])
	description = TextAreaField('Description')

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

	# date validation
	def validate_date(self, date):
		if date.data < date_func.today():
			raise ValidationError("The date cannot be in the past!")


# Create Match form extends MatchFormMixin
class CreateMatchForm(FlaskForm, MatchFormMixin):

    submit = SubmitField('Create Match')


# Update Match form extends MatchFormMixin
class UpdateMatchForm(FlaskForm, MatchFormMixin):

    submit = SubmitField('Update Match')


# Filter match Form
class FilterMatchForm(FlaskForm):


	title = StringField('Title',
					validators=[Optional()])
	description = TextAreaField('Description')

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