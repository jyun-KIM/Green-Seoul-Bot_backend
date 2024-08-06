from flask_wtf import FlaskForm # 폼 유효성 확인
from wtforms import StringField, SelectField, FileField
from wtforms.validators import DataRequired, Optional, URL, ValidationError

class ChatForm(FlaskForm):
    user_input = StringField('User Input', validators=[Optional()])
    payload = SelectField(
        'Payload',
        choices=[
            ("usage", "Usage"),
            ("policy", "Policy"),
            ("select_district", "Select District"),
            ("input_district", "Input District"),
            ("how_to_dispose", "How to Dispose"),
            ("upload_photo", "Upload Photo"),
            ("upload_another", "Upload Another")
        ],
        validators=[DataRequired(message="Payload is required")]
    )
    photo = StringField('Photo URL', validators=[Optional(), URL(message="Invalid URL format")])

    def validate_user_input(self, field):
        if self.payload.data == "input_district" and not field.data:
            raise ValidationError("District name is required when selecting 'input_district' payload.")

class DistrictForm(FlaskForm):
    district_name = StringField('District Name', validators=[DataRequired(message="Please enter a district name")])

class PhotoUploadForm(FlaskForm):
    photo = FileField('Upload Photo', validators=[DataRequired(message="Please upload a photo")])
