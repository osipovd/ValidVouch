from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime


db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    """Table for registering users"""
    
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(40), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(12), nullable=False)
    zip = db.Column(db.String(5), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    
    businesses = db.relationship('Business', backref='owner', lazy=True)
    
    def set_password(self, password):
        """Set the password hash for the user."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if the given password matches the hashed password."""
        return bcrypt.check_password_hash(self.password_hash, password)

    @classmethod
    def is_phone_number_email_duplicate(cls, phone_number, email):
        """Check if the phone number or email already exists in the database independently."""
        existing_user = cls.query.filter((cls.phone_number == phone_number) | (cls.email == email)).first()
        return existing_user is not None
    
    
class Business(db.Model):
    """Model for businesses"""
    
    __tablename__ = 'businesses'
    
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(30), unique=True, nullable=False)
    business_category = db.Column(db.String(50), nullable=False)
    business_address = db.Column(db.String(40), nullable=False)
    business_city = db.Column(db.String(25), nullable=False)
    business_state = db.Column(db.String(2), nullable=False)
    business_zip = db.Column(db.String(5), nullable=False)  
    business_description = db.Column(db.Text, nullable=False)
    business_phone = db.Column(db.String(15), nullable=True)
    business_website = db.Column(db.String(100), nullable=True)
    business_hours = db.Column(db.String(300), nullable=False)
    time_zone = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  

    def full_address(self):
        """Return the full address as a single formatted string."""
        return f"{self.business_address}, {self.business_city}, {self.business_state}, {self.business_zip}"
    
    def average_rating(self):
        if self.reviews:
            return sum(review.rating for review in self.reviews) / len(self.reviews)
        return 0
    
    @staticmethod
    def format_business_hours(hours_str):
        """Format business hours from a string into a more readable form."""
        days_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        days = {day: '' for day in days_order}  
        
        try:
            if hours_str:
                parts = hours_str.split(', ')
                for part in parts:
                    day, hours = part.split(': ')
                    if hours == 'Closed':
                        days[day] = 'Closed'
                    else:
                        start, end = hours.split(' - ')
                        start_hour, start_minute = map(int, start.split(':'))
                        end_hour, end_minute = map(int, end.split(':'))
                        formatted_start = f"{start_hour % 12 if start_hour % 12 else 12}:{start_minute:02d} {'AM' if start_hour < 12 else 'PM'}"
                        formatted_end = f"{end_hour % 12 if end_hour % 12 else 12}:{end_minute:02d} {'AM' if end_hour < 12 else 'PM'}"
                        days[day] = f"{formatted_start}–{formatted_end}"
            
            formatted_hours = ', '.join(f"{day}: {hours}" for day, hours in days.items() if hours)
            return formatted_hours
        except Exception as e:
            print(f"Error formatting business hours: {e}")
            return "Hours format error"

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    response = db.Column(db.Text, nullable=True)
    response_at = db.Column(db.DateTime, nullable=True)
    is_visible = db.Column(db.Boolean, default=True, nullable=False) 

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    business = db.relationship('Business', backref=db.backref('reviews', lazy=True))

    def __repr__(self):
        return f'<Review {self.id} by User {self.user_id} on Business {self.business_id}>'

    @classmethod
    def user_has_reviewed_business(cls, user_id, business_id):
        """
        Check if the user has already left a review for the given business.
        Args:
            user_id: The ID of the user.
            business_id: The ID of the business.
        Returns:
            bool: True if the user has already left a review, False otherwise.
        """
        existing_review = cls.query.filter_by(user_id=user_id, business_id=business_id).first()
        return existing_review is not None

    
class Interaction(db.Model):
    """Table to store user interactions with businesses and reviews"""
    
    __tablename__ = 'interactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=True) 
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=True)  
    interaction_type = db.Column(db.String(10), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
    user = db.relationship('User', backref=db.backref('interactions', lazy='dynamic'))
    business = db.relationship('Business', backref=db.backref('interactions', lazy='dynamic'))
    review = db.relationship('Review', backref=db.backref('interactions', lazy='dynamic'))

    def __repr__(self):
        return f'<Interaction user_id={self.user_id} business_id={self.business_id} review_id={self.review_id} type={self.interaction_type}>'

class FlaggedReview(db.Model):
    __tablename__ = 'flagged_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    flag_reason = db.Column(db.Text, nullable=False)
    flag_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    admin_decision = db.Column(db.String(10), nullable=True)  
    admin_notes = db.Column(db.Text, nullable=True)
    appeal_reason = db.Column(db.Text, nullable=True)
    appeal_timestamp = db.Column(db.DateTime, nullable=True)
    appeal_decision = db.Column(db.String(10), nullable=True)  

    review = db.relationship('Review', backref=db.backref('flagged_review', uselist=False))
    user = db.relationship('User', backref=db.backref('flagged_reviews', lazy=True))  # New relationship

    def process_admin_decision(self):
        """Process the admin decision on the flagged review and update the review visibility."""
        if self.admin_decision == 'approve':
            self.review.is_visible = False
        elif self.admin_decision == 'deny':
            self.review.is_visible = True

    def __repr__(self):
        return f'<FlaggedReview {self.id} for Review {self.review_id}>'

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)
