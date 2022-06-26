from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import Length, EqualTo, DataRequired, ValidationError
from services.models import User

class registerForm(FlaskForm):
    def validate_email(self, email_to_check):
        print('********this is the email to check',email_to_check.data )
        user = User.getByEmail(email_to_check.data)
        if user== None:
            pass
        elif user.email:
            raise ValidationError('email already exists! Please try a different email')

    name = StringField('Name:', validators=[Length(min=3, max=100), DataRequired()])
    email = EmailField('Email:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[Length(min=8, max=100),DataRequired()])
    confirmPassword = PasswordField('Confirm Password:', validators=[EqualTo('password'), DataRequired()])
    
    submit = SubmitField('Create Account')