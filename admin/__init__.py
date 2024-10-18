from flask import Blueprint

# Create a Blueprint for the admin functionality
admin_bp = Blueprint('admin', __name__, template_folder='templates')

# Import the routes to ensure they are attached to the blueprint
from . import routes