from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class MarksForm(FlaskForm):
    subject = StringField('Предмет', validators=[DataRequired()])
    mark = IntegerField("Оценка", validators=[DataRequired()])
    submit = SubmitField('Применить')
