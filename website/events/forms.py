from datetime import date as date_func
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, DateField, TextAreaField,
		SelectField, IntegerField, DecimalField)
from wtforms.validators import (DataRequired, Length, EqualTo, ValidationError,
		Optional, NumberRange)

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
					validators=[FileAllowed(['jpg', 'jpeg', 'png'])])

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