from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, IntegerField
from wtforms.validators import InputRequired
from flask_wtf.file import FileAllowed

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    file = FileField(
        "File", validators=[InputRequired(), FileAllowed(["csv"], "CSV Document Only")]
    ) 
    submit = SubmitField("Upload File")


class ChangeWaitTimeForm(FlaskForm):
    wait_time = IntegerField("Wait Time", validators=[InputRequired()])
    submit = SubmitField("Change Wait Time")
