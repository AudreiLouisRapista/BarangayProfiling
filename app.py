from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import make_response

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/barangayprofiling'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db = SQLAlchemy(app)

# ── Models ──────────────────────────────────────────────
class Employee(db.Model):
    __tablename__ = 'employees'
    id             = db.Column(db.Integer, primary_key=True)
    first_name     = db.Column(db.String(100), nullable=False)
    last_name      = db.Column(db.String(100), nullable=False)
    position_id       = db.Column(db.Integer, db.ForeignKey('position.id'), nullable=False)
    employee_email = db.Column(db.String(100), unique=True)   
    password       = db.Column(db.String(100))                
    created_at     = db.Column(db.DateTime, default=db.func.current_timestamp())  
    updated_at     = db.Column(db.DateTime, onupdate=db.func.current_timestamp()) 

    position     = db.relationship('Position', backref='employees')

class Admin(db.Model):
    __tablename__ = 'admin'
    id             = db.Column(db.Integer, primary_key=True)
    admin_email       = db.Column(db.String(100), unique=True, nullable=False)
    admin_password       = db.Column(db.String(255), nullable=False)

class Position(db.Model):
    __tablename__ = 'position'
    id             = db.Column(db.Integer, primary_key=True)
    position_type   = db.Column(db.String(100), unique=True, nullable=False)

# ── login Routes ──────────────────────────────────────────────────────
@app.route('/')
def login_page():
    if 'admin_id' in session:
        return redirect(url_for('BarangayAdmin/dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    email    = request.form.get('admin_email')
    password = request.form.get('admin_password')

    # Check if fields are empty
    if not email or not password:
        flash('Please fill in all fields.', 'warning')
        return redirect(url_for('login_page'))

    # Find admin by email
    admin = Admin.query.filter_by(admin_email=email).first()

    # Verify admin and password
    if admin and check_password_hash(admin.admin_password, password):
        session['admin_id']    = admin.id
        session['admin_email'] = admin.admin_email
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid email or password.', 'danger')
        return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.clear()                     
    session.modified = True                  
    response = make_response(redirect(url_for('login_page')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma']        = 'no-cache'
    return response

@app.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma']        = 'no-cache'
    response.headers['Expires']       = '-1'
    return response



# ── Protect All Systems Routes (ADMIN) ───────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login first.', 'warning')
            response = make_response(redirect(url_for('login_page')))
            response.headers['Cache-Control'] = 'no-store'
            return response
        return f(*args, **kwargs)
    return decorated_function
    

@app.route('/dashboard')
@login_required
def dashboard():
    total_employees = Employee.query.count()
    return render_template('BarangayAdmin/dashboard.html', segment='dashboard', total_employees=total_employees)




# Employees route to display all employees
@app.route('/employees')
@login_required
def employees():
    all_employees = Employee.query.all()
    all_positions = Position.query.all()
    total_employees = Employee.query.count()
    return render_template('BarangayAdmin/employees.html', segment='employees', employees=all_employees, positions=all_positions, total_employees=total_employees)

#Employees route to add new employee
@app.route('/add_employee', methods=['POST'])
def add_employee():
    try: 
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        position_id = request.form['position_id']
        employee_email = request.form['employee_email']
        password = request.form['password']

        existing = Employee.query.filter_by(employee_email=employee_email).first()
        if existing:
            flash('Employee with this email already exists.', 'warning')
            return redirect(url_for('BarangayAdmin/employees'))

        new_employee = Employee(
            first_name=first_name,
            last_name=last_name,
            position_id=position_id,
            employee_email=employee_email,
            password=password
        )
        db.session.add(new_employee)
        db.session.commit()
        flash('Employee added successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding employee: {str(e)}', 'danger')

    return redirect(url_for('employees'))




@app.route('/finances')
@login_required
def finances():
    return render_template('BarangayAdmin/finances.html', segment='finances')



@app.route('/certificates')
@login_required
def certificates():
    return render_template('BarangayAdmin/certificates.html', segment='certificates')



# ── Protect All Systems Routes (OFFICIALS) ───────────────────────────────────────────



# ── Init DB ─────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)