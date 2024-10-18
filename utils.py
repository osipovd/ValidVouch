from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash("This section is only accessible to administrators.", "warning")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def format_business_hours(hours_str):
    days_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    days = {day: '' for day in days_order}  # Initialize dictionary with ordered days
    
    # Assuming hours_str is a string like "Monday: 6:0 - 18:0, Tuesday: 6:0 - 18:0, ..."
    if hours_str:
        parts = hours_str.split(', ')
        for part in parts:
            day, hours = part.split(': ')
            if hours == 'Closed':
                days[day] = 'Closed'
            else:
                start, end = hours.split(' - ')
                start_hour, start_minute = start.split(':')
                end_hour, end_minute = end.split(':')
                # Format hours as AM/PM
                start_hour = int(start_hour)
                end_hour = int(end_hour)
                formatted_start = f"{start_hour % 12 if start_hour % 12 else 12} {'AM' if start_hour < 12 else 'PM'}"
                formatted_end = f"{end_hour % 12 if end_hour % 12 else 12} {'AM' if end_hour < 12 else 'PM'}"
                days[day] = f"{formatted_start}–{formatted_end}"
    
    # Build the output string in the order you want
    formatted_hours = '\n'.join(f"{day}\t{hours}" for day, hours in days.items())
    return formatted_hours
