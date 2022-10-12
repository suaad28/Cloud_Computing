import flask_wtf
import wtforms
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


#  form which has username password and submit field
class JobSearch(FlaskForm):
    job_title = StringField("Job Title", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    submit = SubmitField("Submit")