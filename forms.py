from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField, FormField, DateField, EmailField, PasswordField, HiddenField, RadioField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, URL, Optional, EqualTo, Email
from choices import STATE_CHOICES, BUSINESS_CATEGORIES, TIME_ZONE_CHOICES, HOUR_CHOICES, MINUTE_CHOICES

class RegisterUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=20)])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired(), Length(max=40)])
    city = StringField('City', validators=[DataRequired(), Length(max=20)])
    state = SelectField('State', choices=STATE_CHOICES, validators=[DataRequired(), Length(max=12)])
    zip = StringField('ZIP Code', validators=[DataRequired(), Length(max=5)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    admin_code = StringField('Admin Code (optional)')  # Optional field for admin registration
    
class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=20)])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired(), Length(max=40)])
    city = StringField('City', validators=[DataRequired(), Length(max=20)])
    state = StringField('State', validators=[DataRequired(), Length(max=12)])
    zip = StringField('Zip Code', validators=[DataRequired(), Length(max=5)])
    phone_number = StringField('Phone Number', validators=[Length(min=10, max=15), Optional()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Update Profile')
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class BusinessHourForm(FlaskForm):
    hour = SelectField('Hour', choices=HOUR_CHOICES, default='6')
    minute = SelectField('Minute', choices=MINUTE_CHOICES, default='00')
    closed = SelectField('Status', choices=[('Open', 'Open'), ('Closed', 'Closed')])

class RegisterBusinessForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=30)])
    business_category = SelectField('Category', choices=BUSINESS_CATEGORIES, validators=[DataRequired()])
    business_address = StringField('Address', validators=[DataRequired(), Length(max=40)])
    business_city = StringField('City', validators=[DataRequired(), Length(max=25)])
    business_state = SelectField('State', choices=STATE_CHOICES, validators=[DataRequired()])
    business_zip = StringField('ZIP Code', validators=[DataRequired(), Length(min=5, max=5)])
    business_description = TextAreaField('Description', validators=[DataRequired()])
    business_phone = StringField('Phone Number', validators=[Optional(), Length(max=15)])
    business_website = StringField('Website', validators=[Optional(), URL(), Length(max=100)])
    time_zone = SelectField('Time Zone', choices=TIME_ZONE_CHOICES, validators=[DataRequired()])
    monday_hours_open = FormField(BusinessHourForm, label='Monday Opening Time')
    monday_hours_close = FormField(BusinessHourForm, label='Monday Closing Time')
    tuesday_hours_open = FormField(BusinessHourForm, label='Tuesday Opening Time')
    tuesday_hours_close = FormField(BusinessHourForm, label='Tuesday Closing Time')
    wednesday_hours_open = FormField(BusinessHourForm, label='Wednesday Opening Time')
    wednesday_hours_close = FormField(BusinessHourForm, label='Wednesday Closing Time')
    thursday_hours_open = FormField(BusinessHourForm, label='Thursday Opening Time')
    thursday_hours_close = FormField(BusinessHourForm, label='Thursday Closing Time')
    friday_hours_open = FormField(BusinessHourForm, label='Friday Opening Time')
    friday_hours_close = FormField(BusinessHourForm, label='Friday Closing Time')
    saturday_hours_open = FormField(BusinessHourForm, label='Saturday Opening Time')
    saturday_hours_close = FormField(BusinessHourForm, label='Saturday Closing Time')
    sunday_hours_open = FormField(BusinessHourForm, label='Sunday Opening Time')
    sunday_hours_close = FormField(BusinessHourForm, label='Sunday Closing Time')
    
class EditBusinessForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=30)])
    business_category = SelectField('Category', choices=BUSINESS_CATEGORIES, validators=[DataRequired()])
    business_address = StringField('Address', validators=[DataRequired(), Length(max=40)])
    business_city = StringField('City', validators=[DataRequired(), Length(max=25)])
    business_state = SelectField('State', choices=STATE_CHOICES, validators=[DataRequired()])
    business_zip = StringField('ZIP Code', validators=[DataRequired(), Length(min=5, max=5)])
    business_description = TextAreaField('Description', validators=[DataRequired()])
    business_phone = StringField('Phone Number', validators=[Optional(), Length(max=15)])
    business_website = StringField('Website', validators=[Optional(), URL(), Length(max=100)])
    time_zone = SelectField('Time Zone', choices=TIME_ZONE_CHOICES, validators=[DataRequired()])
    monday_hours_open = FormField(BusinessHourForm, label='Monday Opening Time')
    monday_hours_close = FormField(BusinessHourForm, label='Monday Closing Time')
    tuesday_hours_open = FormField(BusinessHourForm, label='Tuesday Opening Time')
    tuesday_hours_close = FormField(BusinessHourForm, label='Tuesday Closing Time')
    wednesday_hours_open = FormField(BusinessHourForm, label='Wednesday Opening Time')
    wednesday_hours_close = FormField(BusinessHourForm, label='Wednesday Closing Time')
    thursday_hours_open = FormField(BusinessHourForm, label='Thursday Opening Time')
    thursday_hours_close = FormField(BusinessHourForm, label='Thursday Closing Time')
    friday_hours_open = FormField(BusinessHourForm, label='Friday Opening Time')
    friday_hours_close = FormField(BusinessHourForm, label='Friday Closing Time')
    saturday_hours_open = FormField(BusinessHourForm, label='Saturday Opening Time')
    saturday_hours_close = FormField(BusinessHourForm, label='Saturday Closing Time')
    sunday_hours_open = FormField(BusinessHourForm, label='Sunday Opening Time')
    sunday_hours_close = FormField(BusinessHourForm, label='Sunday Closing Time')
    submit = SubmitField('Edit Business')
    
class SearchBusinessForm(FlaskForm):
    search_business_name = StringField('Business Name', validators=[Optional()])
    search_business_category = SelectField('Category', choices=BUSINESS_CATEGORIES, validators=[Optional()])
    search_business_city = StringField('City', validators=[Optional()])
    business_state = SelectField('State', choices=STATE_CHOICES, validators=[Optional()])
    business_zip = StringField('ZIP Code', validators=[Optional()])
    min_rating = SelectField('Minimum Rating', choices=[('', 'Any')] + [(str(i), f'{i} Stars') for i in range(1, 6)], validators=[Optional()])
    sort_by = SelectField('Sort By', choices=[
        ('relevance', 'Relevance'),
        ('highest', 'Highest Reviews'),
        ('lowest', 'Lowest Reviews'),
        ('most_reviews', 'Most Reviews')
    ], validators=[Optional()])
        
class LeaveReviewForm(FlaskForm):
    content = TextAreaField('Review', validators=[DataRequired()])
    rating = SelectField(
        'Rating',
        choices=[
            ('1', '1 Star'),
            ('2', '2 Stars'),
            ('3', '3 Stars'),
            ('4', '4 Stars'),
            ('5', '5 Stars')
        ],
        validators=[DataRequired()],
        coerce=int
    )
    proof_of_purchase = BooleanField('I have proof of purchase', validators=[DataRequired()])
    
class EditReviewForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    rating = SelectField(
        'Rating',
        choices=[
            ('1', '1 Star'),
            ('2', '2 Stars'),
            ('3', '3 Stars'),
            ('4', '4 Stars'),
            ('5', '5 Stars')
        ],
        validators=[DataRequired()],
        coerce=int 
    )
    submit = SubmitField('Update Review') 

class BusinessResponseForm(FlaskForm):
    response = TextAreaField('Response', validators=[DataRequired()])
    submit = SubmitField('Submit Response')
    
class EditResponseForm(FlaskForm):
    response = TextAreaField('Response', validators=[DataRequired()])
    submit = SubmitField('Update Response')

class LikeUnlikeForm(FlaskForm):
    pass

class VoteForm(FlaskForm):
    review_id = HiddenField('Review ID')  # Hidden field to store review ID if needed
    submit = SubmitField('Vote')
    
class DeleteBusinessForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Delete Business')

class DeleteUserForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Delete Business')
    
class AdminDeleteBusinessForm(FlaskForm):
    business_id = HiddenField('Business ID', validators=[DataRequired()])
    submit = SubmitField('Delete Business')

class AdminDeleteUserForm(FlaskForm):
    user_id = HiddenField('User ID', validators=[DataRequired()])
    submit = SubmitField('Delete User')

class FlagReviewForm(FlaskForm):
    reason = TextAreaField('Reason for Flagging', validators=[DataRequired(), Length(min=10, max=500)], 
                           render_kw={"placeholder": "Describe why this review should be flagged for further inspection. Please provide as much detail as possible."})
    submit = SubmitField('Flag Review')

class AdminDecisionForm(FlaskForm):
    decision = RadioField('Decision', choices=[('approve', 'Approve'), ('deny', 'Deny')], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AppealForm(FlaskForm):
    appeal_reason = TextAreaField('Reason for Appeal', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Submit Appeal')
    
class AdminAppealDecisionForm(FlaskForm):
    decision = RadioField('Decision', choices=[('approve', 'Approve'), ('deny', 'Deny')], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[DataRequired()])
    submit = SubmitField('Submit')