from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from utils import admin_required  
from models import db, User, Business, Review, FlaggedReview, Interaction
from forms import AdminDeleteBusinessForm, AdminDecisionForm, AdminAppealDecisionForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    user_count = User.query.count()
    business_count = Business.query.count()
    review_count = Review.query.count()

    return render_template('admin/admin_dashboard.html', user_count=user_count,
                           business_count=business_count, review_count=review_count)
    
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/admin_users.html', users=users)

@admin_bp.route('/businesses')
@login_required
@admin_required
def businesses():
    businesses = Business.query.all()
    delete_business_form = AdminDeleteBusinessForm()
    return render_template('admin/admin_businesses.html', businesses=businesses, delete_business_form=delete_business_form)

@admin_bp.route('/delete-business/<int:business_id>', methods=['POST'], endpoint='admin_delete_business')
@login_required
@admin_required
def delete_business(business_id):
    business = Business.query.get_or_404(business_id)  
    db.session.delete(business)  
    db.session.commit() 
    flash('Business successfully deleted.', 'success') 
    return redirect(url_for('admin.businesses')) 

@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'], endpoint='delete_user')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)  

    try:
        Interaction.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        reviews = Review.query.filter_by(user_id=user_id).all()
        for review in reviews:
            FlaggedReview.query.filter_by(review_id=review.id).delete(synchronize_session=False)
            Interaction.query.filter_by(review_id=review.id).delete(synchronize_session=False)
            db.session.delete(review)

        businesses = Business.query.filter_by(user_id=user_id).all()
        for business in businesses:
            business_reviews = Review.query.filter_by(business_id=business.id).all()
            for business_review in business_reviews:
                FlaggedReview.query.filter_by(review_id=business_review.id).delete(synchronize_session=False)
                Interaction.query.filter_by(review_id=business_review.id).delete(synchronize_session=False)
                db.session.delete(business_review)
            db.session.delete(business)

        db.session.delete(user)  
        db.session.commit()  
        flash('User successfully deleted.', 'success')  
    except Exception as e:
        db.session.rollback() 
        flash(f'An error occurred while deleting the user: {str(e)}', 'error')

    return redirect(url_for('admin.users'))  


@admin_bp.route('/flagged-reviews')
@login_required
@admin_required
def flagged_reviews():
    flagged_reviews = FlaggedReview.query.filter(FlaggedReview.admin_decision == "pending").all()
    form = AdminDecisionForm()
    return render_template('admin/flagged_reviews.html', flagged_reviews=flagged_reviews, form=form)


@admin_bp.route('/review-decision/<int:flagged_review_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def review_decision(flagged_review_id):
    flagged_review = FlaggedReview.query.get_or_404(flagged_review_id)
    form = AdminDecisionForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        flagged_review.admin_decision = request.form['decision']
        flagged_review.admin_notes = form.notes.data

        if request.form['decision'] == 'approve':
            flagged_review.review.is_visible = False
        elif request.form['decision'] == 'deny':
            flagged_review.review.is_visible = True

        try:
            db.session.commit()
            flash('Decision has been saved successfully.', 'success')
            return redirect(url_for('admin.flagged_reviews'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to save decision.', 'error')
            print(f"Database Error: {e}")

    return render_template('admin/admin_review_decision.html', review=flagged_review.review, flag=flagged_review, form=form)

@admin_bp.route('/appeals')
@login_required
@admin_required
def appeals():
    appeals = FlaggedReview.query.filter(FlaggedReview.appeal_decision == "pending").all()
    form = AdminAppealDecisionForm()
    return render_template('admin/appeals.html', appeals=appeals, form=form)

@admin_bp.route('/process-appeal/<int:flagged_review_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def process_appeal(flagged_review_id):
    flagged_review = FlaggedReview.query.get_or_404(flagged_review_id)
    form = AdminAppealDecisionForm()

    if request.method == 'POST' and form.validate_on_submit():
        flagged_review.appeal_decision = form.decision.data
        flagged_review.admin_notes = form.notes.data

        if form.decision.data == 'approve':
            flagged_review.review.is_visible = False
        elif form.decision.data == 'deny':
            flagged_review.review.is_visible = True

        try:
            db.session.commit()
            flash('Appeal decision has been saved successfully.', 'success')
            return redirect(url_for('admin.appeals'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to save appeal decision.', 'error')
            print(f"Database Error: {e}")

    return render_template('admin/admin_appeal_decision.html', review=flagged_review.review, flag=flagged_review, form=form)




























