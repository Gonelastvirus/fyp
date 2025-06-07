from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, Optional
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired()])
    role = SelectField('I am a:', choices=[('student', 'Student'), ('expert', 'Expert/Advisor')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    
    # Conditional fields
    university = StringField('University/Institution', validators=[Optional(), Length(max=100)])
    bio = TextAreaField('Bio/Experience', validators=[Optional(), Length(max=500)])
    skills = TextAreaField('Skills/Expertise Areas', validators=[Optional(), Length(max=300)])
    
    submit = SubmitField('Register')

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired(), Length(min=5, max=200)])
    category = SelectField('Category', choices=[
        ('web_development', 'Web Development'),
        ('mobile_app', 'Mobile Application'),
        ('data_science', 'Data Science & Analytics'),
        ('machine_learning', 'Machine Learning/AI'),
        ('software_engineering', 'Software Engineering'),
        ('database_systems', 'Database Systems'),
        ('cybersecurity', 'Cybersecurity'),
        ('game_development', 'Game Development'),
        ('embedded_systems', 'Embedded Systems'),
        ('blockchain', 'Blockchain'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    description = TextAreaField('Project Description', validators=[DataRequired(), Length(min=50)], widget=TextArea())
    requirements = TextAreaField('Specific Requirements', validators=[DataRequired(), Length(min=20)], widget=TextArea())
    tech_stack = StringField('Preferred Technology Stack', validators=[Optional(), Length(max=200)])
    budget_min = FloatField('Minimum Budget ($)', validators=[DataRequired(), NumberRange(min=50)])
    budget_max = FloatField('Maximum Budget ($)', validators=[DataRequired(), NumberRange(min=50)])
    duration_weeks = IntegerField('Expected Duration (weeks)', validators=[DataRequired(), NumberRange(min=1, max=52)])
    
    submit = SubmitField('Post Project')

class ProposalForm(FlaskForm):
    cover_letter = TextAreaField('Cover Letter', validators=[DataRequired(), Length(min=100)], widget=TextArea())
    proposed_budget = FloatField('Proposed Budget ($)', validators=[DataRequired(), NumberRange(min=1)])
    delivery_time_weeks = IntegerField('Delivery Time (weeks)', validators=[DataRequired(), NumberRange(min=1, max=52)])
    
    submit = SubmitField('Submit Proposal')

class MilestoneForm(FlaskForm):
    title = StringField('Milestone Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    budget_percentage = FloatField('Budget Percentage (%)', validators=[DataRequired(), NumberRange(min=1, max=100)])
    
    submit = SubmitField('Add Milestone')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        ('5', '5 Stars - Excellent'),
        ('4', '4 Stars - Very Good'),
        ('3', '3 Stars - Good'),
        ('2', '2 Stars - Fair'),
        ('1', '1 Star - Poor')
    ], validators=[DataRequired()])
    comment = TextAreaField('Review Comment', validators=[Optional(), Length(max=500)])
    
    submit = SubmitField('Submit Review')

class DisputeForm(FlaskForm):
    title = StringField('Issue Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Describe the Issue', validators=[DataRequired(), Length(min=20)], widget=TextArea())
    
    submit = SubmitField('Raise Dispute')
