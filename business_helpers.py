from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from models import db, Business, Review, Interaction
from forms import VoteForm
from datetime import datetime
from sqlalchemy import func

def get_business(business_id):
    return Business.query.get_or_404(business_id)

def get_reviews(business_id):
    return Review.query.filter_by(business_id=business_id, is_visible=True).all()

def get_average_rating(business_id):
    average_rating = db.session.query(func.avg(Review.rating)) \
                               .filter(Review.business_id == business_id, Review.is_visible == True) \
                               .scalar()
    return round(average_rating, 1) if average_rating is not None else None

def get_vote_counts(reviews):
    return {
        review.id: {
            'up': Interaction.query.filter_by(review_id=review.id, interaction_type='up').count(),
            'down': Interaction.query.filter_by(review_id=review.id, interaction_type='down').count()
        }
        for review in reviews
    }

def has_user_reviewed_business(user_id, business_id):
    return Review.user_has_reviewed_business(user_id, business_id) if user_id else False

def has_user_liked_business(user_id, business_id):
    return Interaction.query.filter_by(user_id=user_id, business_id=business_id, interaction_type='favorite').first() is not None if user_id else False

def handle_response_form_submission(business, form):
    review_id = request.form.get('review_id')
    review = Review.query.get_or_404(review_id)
    if review.business_id == business.id and business.user_id == current_user.id:
        review.response = form.response.data
        review.response_at = datetime.utcnow()
        db.session.commit()
        flash('Your response has been submitted.', 'success')
    else:
        flash('You are not authorized to respond to this review.', 'error')

def get_vote_forms(reviews):
    return {review.id: VoteForm() for review in reviews}

def perform_search(form):
    query = Business.query

    if form.search_business_name.data:
        query = query.filter(Business.business_name.ilike(f"%{form.search_business_name.data}%"))

    if form.search_business_category.data and form.search_business_category.data != '':
        query = query.filter(Business.business_category == form.search_business_category.data)

    if form.search_business_city.data:
        query = query.filter(Business.business_city.ilike(f"%{form.search_business_city.data}%"))

    if form.business_state.data:
        query = query.filter(Business.business_state == form.business_state.data)

    if form.business_zip.data:
        query = query.filter(Business.business_zip == form.business_zip.data)

    if form.min_rating.data:
        min_rating = int(form.min_rating.data)
        results = [business for business in query.all() if business.average_rating() >= min_rating]
    else:
        results = query.all()

    if form.sort_by.data == 'highest':
        results = sorted(results, key=lambda b: b.average_rating(), reverse=True)
    elif form.sort_by.data == 'lowest':
        results = sorted(results, key=lambda b: b.average_rating())
    elif form.sort_by.data == 'most_reviews':
        results = sorted(results, key=lambda b: len(b.reviews), reverse=True)

    return results
