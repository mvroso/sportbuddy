from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, SelectField,
		SelectMultipleField, DecimalField)
from wtforms.validators import DataRequired, Optional, NumberRange

# Update coach account
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


# Filter coaches
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