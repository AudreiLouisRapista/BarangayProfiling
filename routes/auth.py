from flask import render_template, request, redirect, url_for, flash, session, make_response
from werkzeug.security import check_password_hash
from app import app, login_required
from models import User


@app.route('/')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('BarangayAdmin/dashboard.html')


@app.route('/login', methods=['POST'])
def login():
    user_email = request.form.get('user_email')
    user_password = request.form.get('user_password')

    if not user_email or not user_password:
        flash('Please fill in all fields.', 'warning')
        return redirect(url_for('login_page'))

    user = User.query.filter_by(user_email=user_email).first()
    if user and check_password_hash(user.user_password, user_password):
        session['user_id'] = user.id
        session['user_email'] = user.user_email
        session['user_role'] = user.user_role.role_type
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))

    flash('Invalid email or password.', 'danger')
    return redirect(url_for('login_page'))


@app.route('/logout')
def logout():
    session.clear()
    session.modified = True
    response = make_response(redirect(url_for('login_page')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response
