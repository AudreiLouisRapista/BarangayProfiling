from datetime import datetime, timezone

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
    position_id    = db.Column(db.Integer, db.ForeignKey('position.id'), nullable=False)
    status_id      = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    employee_email = db.Column(db.String(100), unique=True)
    phone_number   = db.Column(db.String(20))   
    password       = db.Column(db.String(255)) # Increased to 255 for secure hashes                
    created_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  
    updated_at     = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    deleted_at     = db.Column(db.DateTime, nullable=True) 

    # Relationships
    position = db.relationship('Position', backref='employees')
    status   = db.relationship('Status', backref='employees')

    def soft_delete(self):
        """Mark the employee as deleted without removing from DB."""
        self.deleted_at = datetime.now(timezone.utc)
        db.session.commit()

    def restore(self):
        """Bring a soft-deleted employee back to active status."""
        self.deleted_at = None
        db.session.commit()

class Admin(db.Model):
    __tablename__ = 'admin'
    id             = db.Column(db.Integer, primary_key=True)
    admin_email       = db.Column(db.String(100), unique=True, nullable=False)
    admin_password       = db.Column(db.String(255), nullable=False)

class Position(db.Model):
    __tablename__ = 'position'
    id             = db.Column(db.Integer, primary_key=True)
    position_type   = db.Column(db.String(100), unique=True, nullable=False)


class Status(db.Model):
    __tablename__ = 'status'
    id             = db.Column(db.Integer, primary_key=True)
    status   = db.Column(db.String(100), unique=True, nullable=False)
# ── login Routes ──────────────────────────────────────────────────────
@app.route('/')
def login_page():
    if 'admin_id' in session:
        return redirect(url_for('dashboard'))
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
    total_employees = Employee.query.filter(Employee.deleted_at == None).count()
    return render_template('BarangayAdmin/dashboard.html', segment='dashboard', total_employees=total_employees)




# Employees route to display all employees
@app.route('/employees')
@login_required
def employees():
    active_employees = Employee.query.filter(Employee.deleted_at == None).all()
    all_positions = Position.query.all()
    all_statuses = Status.query.all()
    total_employees = Employee.query.filter(Employee.deleted_at == None).count()
    return render_template('BarangayAdmin/employees.html', segment='employees', employees=active_employees, positions=all_positions, statuses=all_statuses, total_employees=total_employees, edit_employee=None, active_employees=active_employees )

#All employee management routes (add, update, edit) will be here
@app.route('/add_employee', methods=['POST'])
@login_required
def add_employee():
    try: 
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        position_id = request.form['position_id']
        status_id = request.form['status_id']
        employee_email = request.form['employee_email']
        phone_number = request.form['phone_number']
        password = request.form['password']

        existing = Employee.query.filter_by(employee_email=employee_email).filter(Employee.deleted_at == None).first()
        if existing:
            flash('Employee with this email already exists.', 'warning')
            return redirect(url_for('employees'))

        new_employee = Employee(
            first_name=first_name,
            last_name=last_name,
            position_id=position_id,
            status_id=status_id,
            employee_email=employee_email,
            phone_number=phone_number,
            password=password,
            updated_at=datetime.now(timezone.utc),
           
        )
        db.session.add(new_employee)
        db.session.commit()
        flash('Employee added successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding employee: {str(e)}', 'danger')

    return redirect(url_for('employees'))

@app.route('/update_employee', methods=['POST'])
@login_required
def update_employee():
    try:
        employee_id    = request.form.get('employee_id')   
        employee       = Employee.query.get(employee_id)   

        if not employee:
            flash('Employee not found.', 'danger')
            return redirect(url_for('employees'))

        new_email = request.form.get('employee_email')

    
        existing = Employee.query.filter(
            Employee.employee_email == new_email,
            Employee.id != employee_id             
        ).first()

        if existing:
            flash('Email already used by another employee.', 'warning')
            return redirect(url_for('employees'))

       
        employee.first_name     = request.form.get('first_name')
        employee.last_name      = request.form.get('last_name')
        employee.position_id    = request.form.get('position_id')
        employee.status_id      = request.form.get('status_id')
        employee.employee_email = new_email
        employee.phone_number   = request.form.get('phone_number')
        employee.updated_at     = datetime.now(timezone.utc)

     
        new_password = request.form.get('password')
        if new_password:
            employee.password = generate_password_hash(new_password)
        
        db.session.commit()   
        flash('Employee updated successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating employee: {str(e)}', 'danger')

    return redirect(url_for('employees'))

@app.route('/edit_employee/<int:id>')
@login_required
def edit_employee(id):
    employee = Employee.query.filter_by(id=id, deleted_at=None).first()
    if not employee:
        flash('Employee not found.', 'danger')
        return redirect(url_for('employees'))
    all_positions = Position.query.all()
    all_employees = Employee.query.filter(Employee.deleted_at == None).all()
    all_statuses  = Status.query.all()
    total_employees = Employee.query.filter(Employee.deleted_at == None).count()
    return render_template('BarangayAdmin/employees.html',
                           segment='employees',
                           employees=all_employees,
                           positions=all_positions,
                           total_employees=total_employees,
                            statuses=all_statuses,
                           edit_employee=employee)  

@app.route('/delete_employee/<int:id>', methods=['POST'])
@login_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    try:
        employee.soft_delete()
        flash(f'Employee {employee.first_name} has been moved to archives.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"DELETE ERROR: {str(e)}")  # Print to terminal
        flash(f'Error during deletion: {str(e)}', 'danger')  # Show actual error
    return redirect(url_for('employees'))

@app.route('/employees_archive')
@login_required
def employees_archive():
    """View soft-deleted (archived) employees"""
    archived_employees = Employee.query.filter(Employee.deleted_at != None).all()
    all_positions = Position.query.all()
    all_statuses = Status.query.all()
    total_archived = Employee.query.filter(Employee.deleted_at != None).count()
    return render_template('BarangayAdmin/employees.html', 
                           segment='employees_archive',
                           employees=archived_employees,
                           positions=all_positions,
                           statuses=all_statuses,
                           total_employees=total_archived,
                           edit_employee=None,
                           is_archive=True)

@app.route('/restore_employee/<int:id>', methods=['POST'])
@login_required
def restore_employee(id):
    """Restore a soft-deleted employee"""
    employee = Employee.query.get_or_404(id)
    try:
        employee.restore()  # Uses the restore() method from your model
        flash(f'Employee {employee.first_name} has been restored.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error restoring employee: {str(e)}', 'danger')
    return redirect(url_for('employees_archive'))


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