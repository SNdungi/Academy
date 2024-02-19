
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerField,FloatField,SelectField,PasswordField,EmailField,BooleanField
from wtforms.validators import DataRequired,Length 
from app import app,db

class LoginForm(FlaskForm):
    userid=StringField('userid',validators=[DataRequired(),Length(min=8,max=10)])
    password=StringField('password',validators=[DataRequired(),Length(min=4,max=15)])

class UserMaintenanceForm(FlaskForm):
    firstname=StringField('Firstname',validators=[DataRequired()],render_kw={"class": "capitalize-input"})
    lastname=StringField('lastname',validators=[DataRequired()],render_kw={"class": "capitalize-input"})
    email=StringField('email',validators=[DataRequired()])
    tasks= SelectField('tasks', choices=[
                                        ('MEMBER', 'Member'),
                                        ('DIRECTOR', 'Director'),
                                        ('CREDIT_COMMITTEE', 'Credit_Commitee'),
                                        ('COMPLIANCE', 'Compliance'),
                                        ('credit_OFFICER', 'credit Officer'),
                                        ('TREASURER', 'Treasurer'),
                                        ('FINANCE', 'Finance'),
                                        ('STAFF', 'Staff'),
                                        ('STAFF_ADMIN', 'Admin(Staff)')])
    memberid=StringField('Member ID (Where Applicable)')

    password=StringField('Password',validators=[DataRequired()])
    submit=SubmitField('Submit') 

class ForgotPassword(FlaskForm):
    email=EmailField('Email',validators=[DataRequired()])
    submit=SubmitField('Submit')
    
class PasswordReset(FlaskForm):
    userid = StringField('User ID', validators=[DataRequired(),Length(min=8,max=10)])
    current_password = PasswordField('Current Password Token', validators=[DataRequired(), Length(min=4,max=15)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=4,max=15)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=4,max=15)])
    submit=SubmitField('Submit')