from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,PasswordField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,Length,Email,EqualTo

class RegistrationForm(FlaskForm):
            # creating a new attribute 'username' of type string, and the value passed will be our label i.e. "Username"
            username = StringField('Username', validators=[DataRequired(),Length(min=2,max=20)])
            email = StringField('Email', validators=[DataRequired(),Email()])
            password = PasswordField('Password', validators=[DataRequired()])
            confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
            submit = SubmitField('Sign Up')  

class LoginForm(FlaskForm):
            email = StringField('Email', validators=[DataRequired(),Email()])
            password = PasswordField('Password', validators=[DataRequired()])
            submit = SubmitField('Sign In')

class UpdateAccountForm(FlaskForm):
            # creating a new attribute 'username' of type string, and the value passed will be our label i.e. "Username"
            username = StringField('Username', validators=[DataRequired(),Length(min=2,max=20)])
            email = StringField('Email', validators=[DataRequired(),Email()])
            picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
            submit = SubmitField('Update') 

class PostForm(FlaskForm):
            title = StringField('Title', validators=[DataRequired()])
            content = TextAreaField('Content', validators=[DataRequired()])
            submit = SubmitField('Post')