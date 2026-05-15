from flask import Flask, session, flash, redirect, url_for, make_response
from functools import wraps
from extensions import db

app = Flask(__name__)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/barangayprofiling'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db.init_app(app)

# login_required (unchanged)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'warning')
            response = make_response(redirect(url_for('login_page')))
            response.headers['Cache-Control'] = 'no-store'
            return response
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# ── Import routes AFTER app and db are ready ──
from routes.auth import *
from routes.employee import *
from routes.residence import *
from routes.finance import *
from routes.certificate import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)