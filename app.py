from flask import Flask, render_template, redirect, url_for, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime

from forms import (
    RegisterUserForm, LoginForm, RegisterBusinessForm, SearchBusinessForm,
    LeaveReviewForm, EditReviewForm, BusinessResponseForm, EditProfileForm,
    EditResponseForm, EditBusinessForm, LikeUnlikeForm, DeleteBusinessForm,
    DeleteUserForm, FlagReviewForm, AppealForm
)
from models import connect_db, db, User, Business, Review, Interaction, FlaggedReview
from admin.routes import admin_bp
from business_helpers import (
    get_business, get_reviews, get_average_rating, get_vote_counts,
    has_user_reviewed_business, has_user_liked_business,
    handle_response_form_submission, get_vote_forms, perform_search
)


app = Flask(__name__)
app.register_blueprint(admin_bp)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///validvouch'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "Sharapova1"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False  

toolbar = DebugToolbarExtension(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

with app.app_context():
    connect_db(app)
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchBusinessForm(request.form)
    if request.method == 'POST' and form.validate():
        results = perform_search(form)
        return render_template('search_results.html', results=results, form=form)
    return render_template('index.html', form=form)

@app.route('/search_results')
def search_results():
    return render_template('search_results.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterUserForm()
    if form.validate_on_submit():
        if User.is_phone_number_email_duplicate(form.phone_number.data, form.email.data):
            flash('A user with this phone number or email already exists. Please use different credentials.', 'error')
            return render_template('signup.html', form=form)

        is_admin = False 
        if form.admin_code.data == 'Riddles9278!':
            is_admin = True
        
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            dob=form.dob.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip=form.zip.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            is_admin=is_admin
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account: {}'.format(e), 'error')
            return render_template('signup.html', form=form)
    return render_template('signup.html', form=form)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        if (form.phone_number.data != current_user.phone_number and
            User.query.filter_by(phone_number=form.phone_number.data).first()):
            flash('Phone number already in use.', 'error')
            return render_template('edit_profile.html', form=form)

        if (form.email.data != current_user.email and
            User.query.filter_by(email=form.email.data).first()):
            flash('Email already in use.', 'error')
            return render_template('edit_profile.html', form=form)

        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.dob = form.dob.data
        current_user.address = form.address.data
        current_user.city = form.city.data
        current_user.state = form.state.data
        current_user.zip = form.zip.data
        current_user.phone_number = form.phone_number.data
        current_user.email = form.email.data

        if form.new_password.data:
            current_user.set_password(form.new_password.data)

        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('profile'))
    
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.dob.data = current_user.dob
        form.address.data = current_user.address
        form.city.data = current_user.city
        form.state.data = current_user.state
        form.zip.data = current_user.zip
        form.phone_number.data = current_user.phone_number
        form.email.data = current_user.email
    
    return render_template('edit_profile.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('You have been logged in!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Password or email incorrect, please try again', 'danger')
    return render_template('login.html', form=form)
            
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))
        
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    user_businesses = current_user.businesses  
    delete_user_form = DeleteUserForm()  

    delete_business_forms = {}
    for business in user_businesses:
        delete_business_forms[business.id] = DeleteBusinessForm()

    return render_template('profile.html', user=current_user, user_businesses=user_businesses,
                           delete_user_form=delete_user_form, delete_business_forms=delete_business_forms)

@app.route('/register-business', methods=['GET', 'POST'])
@login_required
def register_business():
    form = RegisterBusinessForm()
    
    if form.validate_on_submit():
        existing_business = Business.query.filter_by(business_name=form.business_name.data).first()
        if existing_business:
            flash('A business with this name already exists. Please use a different name.', 'error')
            return render_template('register_business.html', form=form)

        if form.business_phone.data and form.business_phone.data != current_user.phone_number:
            existing_user = User.query.filter_by(phone_number=form.business_phone.data).first()
            if existing_user:
                flash('This phone number is already associated with another user. Please use your registered phone number.', 'error')
                return render_template('register_business.html', form=form)

        def format_hours(day_open, day_close):
            if day_open.closed.data == 'Closed' or day_close.closed.data == 'Closed':
                return 'Closed'
            else:
                return f"{day_open.hour.data}:{day_open.minute.data} - {day_close.hour.data}:{day_close.minute.data}"

        business_hours = {
            'Monday': format_hours(form.monday_hours_open, form.monday_hours_close),
            'Tuesday': format_hours(form.tuesday_hours_open, form.tuesday_hours_close),
            'Wednesday': format_hours(form.wednesday_hours_open, form.wednesday_hours_close),
            'Thursday': format_hours(form.thursday_hours_open, form.thursday_hours_close),
            'Friday': format_hours(form.friday_hours_open, form.friday_hours_close),
            'Saturday': format_hours(form.saturday_hours_open, form.saturday_hours_close),
            'Sunday': format_hours(form.sunday_hours_open, form.sunday_hours_close)
        }

        business_hours_str = ', '.join([f"{day}: {hours}" for day, hours in business_hours.items()])

        new_business = Business(
            business_name=form.business_name.data,
            business_category=form.business_category.data,
            business_address=form.business_address.data,
            business_city=form.business_city.data,
            business_state=form.business_state.data,
            business_zip=form.business_zip.data,
            business_description=form.business_description.data,
            business_phone=form.business_phone.data,
            business_website=form.business_website.data,
            business_hours=business_hours_str,
            time_zone=form.time_zone.data,
            user_id=current_user.id
        )
        
        db.session.add(new_business)
        try:
            db.session.commit()
            flash('Business registered successfully!', 'success')
            return redirect(url_for('business_details', business_id=new_business.id))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred. Business could not be registered: {str(e)}', 'error')
            return render_template('register_business.html', form=form)

    return render_template('register_business.html', form=form)

@app.route('/edit-business/<int:business_id>', methods=['GET', 'POST'])
@login_required
def edit_business(business_id):
    business = Business.query.get_or_404(business_id)
    
    if current_user.id != business.user_id:
        flash('You are not authorized to edit this business.', 'error')
        return redirect(url_for('business_details', business_id=business_id))

    form = EditBusinessForm(obj=business)
    if form.validate_on_submit():
        existing_business = Business.query.filter(Business.business_name == form.business_name.data, Business.id != business_id).first()
        if existing_business:
            flash('Another business with this name already exists. Please use a different name.', 'error')
            return render_template('edit_business.html', form=form, business_id=business_id)

        business.business_name = form.business_name.data
        business.business_category = form.business_category.data
        business.business_address = form.business_address.data
        business.business_city = form.business_city.data
        business.business_state = form.business_state.data
        business.business_zip = form.business_zip.data
        business.business_description = form.business_description.data
        business.business_phone = form.business_phone.data
        business.business_website = form.business_website.data
        business.time_zone = form.time_zone.data

        def format_hours(day_open, day_close):
            if day_open.closed.data == 'Closed' or day_close.closed.data == 'Closed':
                return 'Closed'
            else:
                return f"{day_open.hour.data}:{day_open.minute.data} - {day_close.hour.data}:{day_close.minute.data}"

        business_hours = {
            'Monday': format_hours(form.monday_hours_open, form.monday_hours_close),
            'Tuesday': format_hours(form.tuesday_hours_open, form.tuesday_hours_close),
            'Wednesday': format_hours(form.wednesday_hours_open, form.wednesday_hours_close),
            'Thursday': format_hours(form.thursday_hours_open, form.thursday_hours_close),
            'Friday': format_hours(form.friday_hours_open, form.friday_hours_close),
            'Saturday': format_hours(form.saturday_hours_open, form.saturday_hours_close),
            'Sunday': format_hours(form.sunday_hours_open, form.sunday_hours_close)
        }

        business.business_hours = ', '.join([f"{day}: {hours}" for day, hours in business_hours.items()])

        db.session.commit()
        flash('Business updated successfully!', 'success')
        return redirect(url_for('business_details', business_id=business.id))

    elif request.method == 'GET':
        form.business_name.data = business.business_name
        form.business_category.data = business.business_category
        form.business_address.data = business.business_address
        form.business_city.data = business.business_city
        form.business_state.data = business.business_state
        form.business_zip.data = business.business_zip
        form.business_description.data = business.business_description
        form.business_phone.data = business.business_phone
        form.business_website.data = business.business_website
        form.time_zone.data = business.time_zone

    return render_template('edit_business.html', form=form, business_id=business_id)

@app.route('/business-details/<int:business_id>', methods=['GET', 'POST'])
def business_details(business_id):
    business = get_business(business_id)
    formatted_hours = Business.format_business_hours(business.business_hours)
    leave_review_form = LeaveReviewForm()
    business_response_form = BusinessResponseForm()
    like_unlike_form = LikeUnlikeForm()

    reviews = get_reviews(business_id)
    average_rating = get_average_rating(business_id)
    vote_counts = get_vote_counts(reviews)

    user_has_reviewed = has_user_reviewed_business(current_user.id, business_id) if current_user.is_authenticated else False
    user_has_liked = has_user_liked_business(current_user.id, business_id) if current_user.is_authenticated else False

    vote_forms = get_vote_forms(reviews)
    
    user_flagged_reviews = []
    if current_user.is_authenticated:
        user_flagged_reviews = [flag.review_id for flag in FlaggedReview.query.filter_by(user_id=current_user.id).all()]

    if request.method == 'POST' and business_response_form.validate_on_submit():
        handle_response_form_submission(business, business_response_form, current_user)
        return redirect(url_for('business_details', business_id=business_id))

    return render_template('business_details.html', business=business, formatted_hours=formatted_hours,
                           leave_review_form=leave_review_form, like_unlike_form=like_unlike_form,
                           average_rating=average_rating, business_response_form=business_response_form,
                           reviews=reviews, user_has_reviewed=user_has_reviewed, user_has_liked=user_has_liked,
                           vote_forms=vote_forms, vote_counts=vote_counts, user_flagged_reviews=user_flagged_reviews)

@app.route('/search-business', methods=['GET', 'POST'])
def search_business():
    form = SearchBusinessForm(request.form)
    if request.method == 'POST' and form.validate():
        results = perform_search(form)
        return render_template('search_results.html', results=results, form=form)
    
    return render_template('search_business.html', form=form)

@app.route('/leave-review/<int:business_id>', methods=['GET', 'POST'])
@login_required
def leave_review(business_id):
    form = LeaveReviewForm()

    existing_review = Review.query.filter_by(user_id=current_user.id, business_id=business_id).first()
    business_owner = Business.query.filter_by(id=business_id, user_id=current_user.id).first()

    if existing_review:
        flash('You have already left a review for this business.', 'error')
        return redirect(url_for('business_details', business_id=business_id))
    
    if business_owner:
        flash('You cannot leave a review for your own business.', 'error')
        return redirect(url_for('business_details', business_id=business_id))

    if form.validate_on_submit():
        if not form.proof_of_purchase.data:
            flash('You must have proof of purchase to leave a review.', 'error')
            return render_template('leave_review.html', form=form, business_id=business_id)

        new_review = Review(
            content=form.content.data,
            rating=form.rating.data,
            user_id=current_user.id,
            business_id=business_id
        )
        db.session.add(new_review)
        try:
            db.session.commit()
            flash('Your review has been posted!', 'success')
            return redirect(url_for('business_details', business_id=business_id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while posting your review.', 'error')
            print(e)
        return redirect(url_for('business_details', business_id=business_id))
    return render_template('leave_review.html', form=form, business_id=business_id)

@app.route('/edit-review/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)
    
    if current_user.id != review.user_id:
        flash('You cannot edit this review.', 'error')
        return redirect(url_for('index'))

    form = EditReviewForm(obj=review)
    
    if form.validate_on_submit():
        review.content = form.content.data
        review.rating = form.rating.data
        db.session.commit()
        flash('Your review has been updated.', 'success')
        return redirect(url_for('business_details', business_id=review.business_id))
    
    return render_template('edit_review.html', form=form, review=review)

@app.route('/business-details/<int:business_id>/reviews', methods=['GET'])
def filter_reviews(business_id):
    filter_by = request.args.get('filter_by', 'newest')
    business = Business.query.get_or_404(business_id)
    reviews_query = Review.query.filter_by(business_id=business_id)

    if filter_by == 'oldest':
        reviews_query = reviews_query.order_by(Review.created_at.asc())
    elif filter_by == 'newest':
        reviews_query = reviews_query.order_by(Review.created_at.desc())
    elif filter_by == 'highest':
        reviews_query = reviews_query.order_by(Review.rating.desc())
    elif filter_by == 'lowest':
        reviews_query = reviews_query.order_by(Review.rating.asc())

    reviews = reviews_query.all()
    average_rating = get_average_rating(business_id)
    formatted_hours = Business.format_business_hours(business.business_hours)
    vote_counts = get_vote_counts(reviews)
    user_has_liked = has_user_liked_business(current_user.id, business_id) if current_user.is_authenticated else False
    user_has_reviewed = has_user_reviewed_business(current_user.id, business_id) if current_user.is_authenticated else False
    vote_forms = get_vote_forms(reviews)

    return render_template('business_details.html', business=business, formatted_hours=formatted_hours,
                           leave_review_form=LeaveReviewForm(), like_unlike_form=LikeUnlikeForm(),
                           average_rating=average_rating, business_response_form=BusinessResponseForm(),
                           reviews=reviews, user_has_reviewed=user_has_reviewed, user_has_liked=user_has_liked,
                           vote_forms=vote_forms, vote_counts=vote_counts)

@app.route('/respond-review/<int:review_id>', methods=['POST'])
@login_required
def respond_review(review_id):
    form = BusinessResponseForm() 
    review = Review.query.get_or_404(review_id)
    
    if form.validate_on_submit():
        review.response = form.response.data
        db.session.commit()
        flash('Your response has been submitted.', 'success')
    else:
        flash('Failed to submit response. Please try again.', 'error')
    
    return redirect(url_for('business_details', business_id=review.business_id))

@app.route('/edit-response/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_response(review_id):
    review = Review.query.get_or_404(review_id)
    business = Business.query.get_or_404(review.business_id)

    if current_user.id != business.user_id:
        flash('You are not authorized to edit this response.', 'error')
        return redirect(url_for('business_details', business_id=review.business_id))

    form = EditResponseForm()

    if form.validate_on_submit():
        review.response = form.response.data
        db.session.commit()
        flash('Your response has been updated.', 'success')
        return redirect(url_for('business_details', business_id=review.business_id))
    
    elif request.method == 'GET':
        form.response.data = review.response

    return render_template('edit_response.html', form=form, review_id=review_id)

@app.route('/like-business/<int:business_id>', methods=['POST'])
@login_required
def like_business(business_id):
    business = Business.query.get(business_id)
    if not business:
        flash('Business not found.', 'danger')
        return redirect(url_for('index'))

    existing_interaction = Interaction.query.filter_by(
        user_id=current_user.id, 
        business_id=business_id, 
        interaction_type='favorite'
    ).first()

    if existing_interaction:
        flash('You have already liked this business.', 'info')
    else:
        new_interaction = Interaction(
            user_id=current_user.id,
            business_id=business_id,
            interaction_type='favorite'
        )
        db.session.add(new_interaction)
        db.session.commit()
        flash('Business liked successfully!', 'success')

    return redirect(url_for('business_details', business_id=business_id))

@app.route('/unlike-business/<int:business_id>', methods=['POST'])
@login_required
def unlike_business(business_id):
    business = Business.query.get(business_id)
    if not business:
        flash('Business not found.', 'danger')
        return redirect(url_for('index'))

    like_interaction = Interaction.query.filter_by(
        user_id=current_user.id,
        business_id=business_id,
        interaction_type='favorite'
    ).first()

    if like_interaction:
        db.session.delete(like_interaction)
        db.session.commit()
        flash('Business unliked successfully!', 'success')
    else:
        flash('You have not liked this business.', 'info')

    return redirect(url_for('business_details', business_id=business_id))

@app.route('/liked-businesses', methods=['GET', 'POST'])
@login_required
def liked_businesses():
    liked_businesses = Business.query.join(Interaction).filter(
        Interaction.user_id == current_user.id,
        Interaction.interaction_type == 'favorite'
    ).all()

    categorized_businesses = {}
    for business in liked_businesses:
        if business.business_category not in categorized_businesses:
            categorized_businesses[business.business_category] = []
        categorized_businesses[business.business_category].append(business)

    selected_category = request.args.get('category', None)

    return render_template('liked_businesses.html', 
                           categorized_businesses=categorized_businesses,
                           selected_category=selected_category)

@app.route('/vote-review/<int:review_id>/<vote_type>', methods=['POST'])
@login_required
def vote_review(review_id, vote_type):
    review = Review.query.get_or_404(review_id)
    existing_interaction = Interaction.query.filter_by(user_id=current_user.id, review_id=review_id).first()

    if existing_interaction:
        if existing_interaction.interaction_type == vote_type:
            db.session.delete(existing_interaction)
            flash('Your vote has been removed.', 'info')
        else:
            existing_interaction.interaction_type = vote_type
            flash('Your vote has been changed.', 'success')
    else:
        new_interaction = Interaction(user_id=current_user.id, review_id=review_id, interaction_type=vote_type)
        db.session.add(new_interaction)
        flash('Your vote has been recorded.', 'success')

    db.session.commit()
    return redirect(url_for('business_details', business_id=review.business_id))

@app.route('/delete-business/<int:business_id>', methods=['POST'])
@login_required
def delete_business(business_id):
    return redirect(url_for('confirm_delete_business', business_id=business_id))

@app.route('/confirm_delete_business/<int:business_id>', methods=['GET', 'POST'])
@login_required
def confirm_delete_business(business_id):
    business = Business.query.get_or_404(business_id)
    form = DeleteBusinessForm()  

    if form.validate_on_submit():
        try:
            reviews = Review.query.filter_by(business_id=business_id).all()
            
            review_ids = [review.id for review in reviews]
            
            if review_ids:
                FlaggedReview.query.filter(FlaggedReview.review_id.in_(review_ids)).delete(synchronize_session=False)
                
            if review_ids:
                Interaction.query.filter(Interaction.review_id.in_(review_ids)).delete(synchronize_session=False)

            Review.query.filter_by(business_id=business_id).delete(synchronize_session=False)

            db.session.delete(business)
            db.session.commit()
            flash("Business and all associated reviews and interactions have been successfully deleted.", "success")
            return redirect(url_for('profile')) 
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while trying to delete the business: {str(e)}', 'error')
            return redirect(url_for('confirm_delete_business', business_id=business_id))
    
    return render_template('confirm_delete_business.html', form=form, business=business)


@app.route('/delete-user', methods=['GET', 'POST'])
@login_required
def delete_user():
    form = DeleteUserForm()

    if form.validate_on_submit():
        if current_user.check_password(form.password.data):
            if current_user.businesses:
                flash("You must delete all your businesses before you can delete your account.", "error")
                return redirect(url_for('profile'))

            try:
                Interaction.query.filter_by(user_id=current_user.id).delete()
                db.session.delete(current_user)
                db.session.commit()
                flash("Your account has been successfully deleted.", "success")
                logout_user()  
                return redirect(url_for('index'))
            except Exception as e:
                db.session.rollback()
                flash("An error occurred while deleting your account: {}".format(e), "error")
                return redirect(url_for('profile'))  
        else:
            flash("Incorrect password. Please try again.", "error")

    return render_template('confirm_delete_user.html', form=form)

@app.route('/confirm-delete-user', methods=['GET', 'POST'])
@login_required
def confirm_delete_user():
    form = DeleteUserForm()
    if form.validate_on_submit():
        if current_user.check_password(form.password.data):
            if current_user.businesses:
                flash("You must delete all your businesses before you can delete your account.", "error")
                return redirect(url_for('profile'))

            try:
                Interaction.query.filter_by(user_id=current_user.id).delete()
                db.session.delete(current_user)
                db.session.commit()
                flash("Your account has been successfully deleted.", "success")
                logout_user()
                return redirect(url_for('index'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred while deleting your account: {e}", "error")
        else:
            flash("Incorrect password. Please try again.", "error")
    return render_template('confirm_delete_user.html', form=form)

@app.route('/flag-review/<int:review_id>', methods=['GET', 'POST'])
@login_required
def flag_review(review_id):
    form = FlagReviewForm()
    review = Review.query.get_or_404(review_id)
    
    user_flagged = FlaggedReview.query.filter_by(review_id=review_id, user_id=current_user.id).first() is not None

    if review.business.user_id != current_user.id:
        flash('You are not authorized to flag reviews for this business.', 'error')
        return redirect(url_for('business_details', business_id=review.business_id))

    if user_flagged:
        flash('You have already flagged this review.', 'error')
        return redirect(url_for('business_details', business_id=review.business_id))

    if form.validate_on_submit():
        new_flag = FlaggedReview(
            review_id=review.id,
            user_id=current_user.id, 
            flag_reason=form.reason.data,
            flag_timestamp=datetime.utcnow(),
            admin_decision='pending'
        )
        db.session.add(new_flag)
        db.session.commit()
        flash('Your flag has been submitted for review by an administrator.', 'info')
        return redirect(url_for('business_details', business_id=review.business_id))

    return render_template('flag_review.html', form=form, review=review, user_flagged=user_flagged)

@app.route('/my-cases', methods=['GET', 'POST'])
@login_required
def my_cases():
    """View for displaying flagged reviews for business owners."""
    if not current_user.businesses:
        flash('You do not have any businesses registered.', 'error')
        return redirect(url_for('profile'))

    business_ids = [business.id for business in current_user.businesses]

    pending_reviews = FlaggedReview.query.join(Review).filter(
        Review.business_id.in_(business_ids),
        FlaggedReview.admin_decision == 'pending'
    ).all()

    resolved_reviews = FlaggedReview.query.join(Review).filter(
        Review.business_id.in_(business_ids),
        (FlaggedReview.admin_decision == 'approve') |
        ((FlaggedReview.admin_decision == 'deny') & (FlaggedReview.appeal_reason.is_(None)))
    ).all()

    my_appeals = FlaggedReview.query.join(Review).filter(
        Review.business_id.in_(business_ids),
        FlaggedReview.appeal_reason.isnot(None)
    ).all()

    return render_template('my_cases.html', pending_reviews=pending_reviews, resolved_reviews=resolved_reviews, my_appeals=my_appeals)

@app.route('/appeal-flagged-review/<int:flagged_review_id>', methods=['GET', 'POST'])
@login_required
def appeal_flagged_review(flagged_review_id):
    flagged_review = FlaggedReview.query.get_or_404(flagged_review_id)

    if flagged_review.admin_decision != 'deny' or flagged_review.review.business.user_id != current_user.id:
        flash('You cannot appeal this decision.', 'error')
        return redirect(url_for('my_cases'))

    form = AppealForm()
    if form.validate_on_submit():
        flagged_review.appeal_reason = form.appeal_reason.data
        flagged_review.appeal_timestamp = datetime.utcnow()
        flagged_review.appeal_decision = 'pending' 
        db.session.commit()
        flash('Your appeal has been submitted and is pending review.', 'success')
        return redirect(url_for('my_cases'))
    
    return render_template('appeal_flagged_review.html', form=form, flagged_review=flagged_review)


if __name__ == "__main__":
    app.run(debug=True)