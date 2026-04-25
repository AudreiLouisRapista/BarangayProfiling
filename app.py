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

class Admin(db.Model):
    __tablename__ = 'admin'
    id             = db.Column(db.Integer, primary_key=True)
    admin_firstname       = db.Column(db.String(100), unique=True, nullable=False)
    admin_lastname        = db.Column(db.String(100), nullable=False)

class Role(db.Model):
    __tablename__ = 'role'
    id             = db.Column(db.Integer, primary_key=True)
    role_type      = db.Column(db.String(100), unique=True, nullable=False)

class User(db.Model):
    __tablename__    = 'users'
    id               = db.Column(db.Integer, primary_key=True)
    user_email       = db.Column(db.String(100), unique=True, nullable=False)
    user_password    = db.Column(db.String(255), nullable=False)
    role_id          = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    user_role        = db.relationship('Role', backref='users')

class Position(db.Model):
    __tablename__ = 'position'
    id             = db.Column(db.Integer, primary_key=True)
    position_type   = db.Column(db.String(100), unique=True, nullable=False)


class Status(db.Model):
    __tablename__ = 'status'
    id             = db.Column(db.Integer, primary_key=True)
    status   = db.Column(db.String(100), unique=True, nullable=False)

class Employee(db.Model):
    __tablename__          = 'employees'
    id                     = db.Column(db.Integer, primary_key=True)
    employee_firstname     = db.Column(db.String(100), nullable=False)
    employee_lastname      = db.Column(db.String(100), nullable=False)
    position_id            = db.Column(db.Integer, db.ForeignKey('position.id'), nullable=False)
    status_id              = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    user_id                = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    employee_phonenumber   = db.Column(db.String(20))
    term_start_date        = db.Column(db.String(100))
    term_end_date          = db.Column(db.String(100))
    created_at             = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at             = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    deleted_at             = db.Column(db.DateTime, nullable=True) 

    # Relationships
    position = db.relationship('Position', backref='employees')
    status   = db.relationship('Status', backref='employees')
    user     = db.relationship('User', backref='employee', uselist=False)

    def soft_delete(self):
        """Mark the employee as deleted without removing from DB."""
        self.deleted_at = datetime.now(timezone.utc)
        db.session.commit()

    def restore(self):
        """Bring a soft-deleted employee back to active status."""
        self.deleted_at = None
        db.session.commit()




class HealthStatus(db.Model):
    __tablename__    = 'healthstatus'
    id               = db.Column(db.Integer, primary_key=True)
    blood_type       = db.Column(db.String(100), nullable=True)
    is_pwd           = db.Column(db.Integer, nullable=True)
    disability_type  = db.Column(db.String(100), nullable=True)
    is_senior_citizen = db.Column(db.Integer, nullable=True)
    created_at       = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at       = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))


class Demographic(db.Model):
    __tablename__          = 'demographic'
    id                     = db.Column(db.Integer, primary_key=True)
    educational_attaiment  = db.Column(db.String(100), nullable=True)
    occupation             = db.Column(db.String(100), nullable=True)
    monthly_income         = db.Column(db.Float(precision=2), nullable=True)
    is_voter               = db.Column(db.Integer, nullable=True)
    created_at             = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at             = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))


class Address(db.Model):
    __tablename__    = 'address'
    id               = db.Column(db.Integer, primary_key=True)
    purok_number     = db.Column(db.Integer, nullable=True)
    street_name      = db.Column(db.String(100), nullable=True)
    house_number     = db.Column(db.Integer, nullable=True)
    is_head_of_family = db.Column(db.String(100), nullable=True)
    creatd_at        = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # ✅ typo matches your DB
    updated_at       = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))



class Residence(db.Model):
    __tablename__            = 'residence'  
    id                       = db.Column(db.Integer, primary_key=True)
    user_id                  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    heathStatus_id           = db.Column(db.Integer, db.ForeignKey('healthstatus.id'), nullable=False)
    address_id               = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)
    demographic_id           = db.Column(db.Integer, db.ForeignKey('demographic.id'), nullable=False)
    status_id                = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    residence_firstname      = db.Column(db.String(100), nullable=True)
    residence_lastname       = db.Column(db.String(100), nullable=True)
    residence_middlename     = db.Column(db.String(100), nullable=True)
    residence_suffix         = db.Column(db.String(100), nullable=True)
    residence_birthday       = db.Column(db.String(100), nullable=True)
    residence_civilStatus    = db.Column(db.String(100), nullable=True)
    residence_citizenship    = db.Column(db.String(100), nullable=True)
    residence_phoneNumber    = db.Column(db.Integer, nullable=True)
    created_at               = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at               = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))
    created_by               = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    deleted_at             = db.Column(db.DateTime, nullable=True) 

    # Relationships
    user        = db.relationship('User', foreign_keys=[user_id], backref='residence')
    creator     = db.relationship('User', foreign_keys=[created_by], backref='created_residences')
    status      = db.relationship('Status', backref='residence')
    health      = db.relationship('HealthStatus', backref='residence')
    address     = db.relationship('Address', backref='residence')
    demographic = db.relationship('Demographic', backref='residence')

    def soft_delete(self):
        self.deleted_at = datetime.now(timezone.utc)
        db.session.commit()

    def restore(self):
        self.deleted_at = None
        db.session.commit()



    
# ── login Routes ──────────────────────────────────────────────────────
@app.route('/')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():

    user_email    = request.form.get('user_email')
    user_password = request.form.get('user_password')

    # Check if fields are empty
    if not user_email or not user_password:
        flash('Please fill in all fields.', 'warning')
        return redirect(url_for('login_page'))

    # Find user by email
    user = User.query.filter_by(user_email=user_email).first()

    # Verify user and password
    if user and check_password_hash(user.user_password, user_password):
        session['user_id']    = user.id
        session['user_email'] = user.user_email
        session['user_role'] = user.user_role.role_type
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
        if 'user_id' not in session:
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




@app.route('/employees')
@login_required
def employees():
    active_employees = Employee.query.filter(Employee.deleted_at == None).all()
    all_positions = Position.query.all()
    all_statuses = Status.query.all()
    user_credentials = User.query.all()
    total_employees = Employee.query.filter(Employee.deleted_at == None).count()
    return render_template('BarangayAdmin/employees.html', 
                           segment='employees', 
                           employees=active_employees, 
                           positions=all_positions, 
                           statuses=all_statuses,
                           user=user_credentials,
                           total_employees=total_employees, 
                           edit_employee=None,
                           is_archive=False)


@app.route('/add_employee', methods=['POST'])
@login_required
def add_employee():
    try: 
        first_name     = request.form['first_name']
        last_name      = request.form['last_name']
        position_id    = request.form['position_id']
        status_id      = request.form['status_id']
        employee_email = request.form['employee_email']
        phone_number   = request.form['phone_number']
        password       = request.form['password']

        existing_user = User.query.filter_by(user_email=employee_email).first()
        if existing_user:
            flash('Employee with this email already exists.', 'warning')
            return redirect(url_for('employees'))

        # 1. Create User first
        new_user = User(
            user_email=employee_email,
            user_password=generate_password_hash(password),
            role_id=3
        )
        db.session.add(new_user)
        db.session.flush()  

        # 2. Create Employee with user_id
        new_employee = Employee(
            employee_firstname=first_name,
            employee_lastname=last_name,
            position_id=position_id,
            status_id=status_id,
            employee_phonenumber=phone_number,
            user_id=new_user.id,
            term_start_date=now(),
            updated_at=datetime.now(timezone.utc),
        )
        db.session.add(new_employee)
        db.session.commit()  

        flash('Employee added successfully.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error adding employee: {str(e)}', 'danger')

    return redirect(url_for('employees'))

@app.route('/edit_employee/<int:id>')
@login_required
def edit_employee(id):
    employee = Employee.query.filter_by(id=id, deleted_at=None).first()
    if not employee:
        flash('Employee not found.', 'danger')
        return redirect(url_for('employees'))
    
    all_positions   = Position.query.all()
    all_employees   = Employee.query.filter(Employee.deleted_at == None).all()
    all_statuses    = Status.query.all()
    total_employees = Employee.query.filter(Employee.deleted_at == None).count()

    return render_template('BarangayAdmin/employees.html',
                           segment='employees',
                           employees=all_employees,
                           positions=all_positions,
                           statuses=all_statuses,
                           total_employees=total_employees,
                           edit_employee=employee,
                           is_archive=False)  


@app.route('/update_employee', methods=['POST'])
@login_required
def update_employee():
    try:
        employee_id = request.form.get('employee_id')
        employee    = Employee.query.get(employee_id)

        if not employee:
            flash('Employee not found.', 'danger')
            return redirect(url_for('employees'))

        new_email = request.form.get('employee_email')

        # Check email conflict in users table (excluding current employee's user)
        existing_user = User.query.filter(
            User.user_email == new_email,
            User.id != employee.user.id  
        ).first()

        if existing_user:
            flash('Email already used by another employee.', 'warning')
            return redirect(url_for('employees'))

        #  Update Employee fields with correct column names
        employee.employee_firstname   = request.form.get('first_name')
        employee.employee_lastname    = request.form.get('last_name')
        employee.position_id          = request.form.get('position_id')
        employee.status_id            = request.form.get('status_id')
        employee.employee_phonenumber = request.form.get('phone_number')
        employee.updated_at           = datetime.now(timezone.utc)

        #  Update User email and password
        if employee.user:
            employee.user.user_email = new_email
            new_password = request.form.get('password')
            if new_password:
                employee.user.user_password = generate_password_hash(new_password)

        db.session.commit()
        flash('Employee updated successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating employee: {str(e)}', 'danger')

    return redirect(url_for('employees'))


@app.route('/delete_employee/<int:id>', methods=['POST'])
@login_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    try:
        employee.soft_delete()
        # correct attribute name
        flash(f'Employee {employee.employee_firstname} has been moved to archives.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error during deletion: {str(e)}', 'danger')
    return redirect(url_for('employees'))


@app.route('/employees_archive')
@login_required
def employees_archive():
    archived_employees = Employee.query.filter(Employee.deleted_at != None).all()
    all_positions  = Position.query.all()
    all_statuses   = Status.query.all()
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
    employee = Employee.query.get_or_404(id)
    try:
        employee.restore()
        # correct attribute name
        flash(f'Employee {employee.employee_firstname} has been restored.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error restoring employee: {str(e)}', 'danger')
    return redirect(url_for('employees_archive'))


# ── Residence Routes ──────────────────────────────────────────────────────

@app.route('/residence')
@login_required
def residence():
    active_residences = Residence.query.filter(Residence.deleted_at == None).all()
    all_statuses      = Status.query.all()
    all_purok         = Address.query.all()
    total_residences  = Residence.query.filter(Residence.deleted_at == None).count()
    return render_template('BarangayAdmin/residence.html',
                           segment='residence',
                           residence=active_residences,
                           statuses=all_statuses,
                           puroks=all_purok,
                           total_residences=total_residences,
                           edit_residence=None,
                           is_archive=False)


@app.route('/add_residence', methods=['POST'])
@login_required
def add_residence():
    try:
        first_name    = request.form['first_name']
        last_name     = request.form['last_name']
        middle_name   = request.form['middle_name']
        suffix        = request.form.get('suffix', None)
        birthday      = request.form['birthday']
        civil_status  = request.form['civil_status']
        citizenship   = request.form['citizenship']
        phone_number  = request.form.get('phone_number', None)
        status_id     = request.form['status_id']
        email         = request.form['email']
        password      = request.form['password']

        # Address fields
        purok_number     = request.form.get('purok_number', None)
        street_name      = request.form.get('street_name', None)
        house_number     = request.form.get('house_number', None)
        is_head_of_family = request.form.get('is_head_of_family', None)

        # Health fields
        blood_type        = request.form.get('blood_type', None)
        is_pwd            = request.form.get('is_pwd', 0)
        disability_type   = request.form.get('disability_type', None)
        is_senior_citizen = request.form.get('is_senior_citizen', 0)

        # Demographic fields
        educational_attaiment = request.form.get('educational_attaiment', None)
        occupation            = request.form.get('occupation', None)
        monthly_income        = request.form.get('monthly_income', None)
        is_voter              = request.form.get('is_voter', 0)

        # Check if email already exists
        existing_user = User.query.filter_by(user_email=email).first()
        if existing_user:
            flash('Residence with this email already exists.', 'warning')
            return redirect(url_for('residence'))

        # 1. Create User account (role_id=3 for residence)
        new_user = User(
            user_email=email,
            user_password=generate_password_hash(password),
            role_id=3,
            updated_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )
        db.session.add(new_user)
        db.session.flush()  # get new_user.id

        # 2. Create Address
        new_address = Address(
            purok_number=purok_number,
            street_name=street_name,
            house_number=house_number,
            is_head_of_family=is_head_of_family,
            updated_at=datetime.now(timezone.utc),
        )
        db.session.add(new_address)
        db.session.flush()  # get new_address.id

        # 3. Create HealthStatus
        new_health = HealthStatus(
            blood_type=blood_type,
            is_pwd=is_pwd,
            disability_type=disability_type,
            is_senior_citizen=is_senior_citizen,
            updated_at=datetime.now(timezone.utc),
        )
        db.session.add(new_health)
        db.session.flush()  # get new_health.id

        # 4. Create Demographic
        new_demographic = Demographic(
            educational_attaiment=educational_attaiment,
            occupation=occupation,
            monthly_income=monthly_income,
            is_voter=is_voter,
            updated_at=datetime.now(timezone.utc),
        )
        db.session.add(new_demographic)
        db.session.flush()  # get new_demographic.id

        # 5. Create Residence linking everything together
        new_residence = Residence(
            user_id=new_user.id,
            heathStatus_id=new_health.id,
            address_id=new_address.id,
            demographic_id=new_demographic.id,
            status_id=status_id,
            residence_firstname=first_name,
            residence_lastname=last_name,
            residence_middlename=middle_name,
            residence_suffix=suffix,
            residence_birthday=birthday,
            residence_civilStatus=civil_status,
            residence_citizenship=citizenship,
            residence_phoneNumber=phone_number,
            updated_at=datetime.now(timezone.utc),
            created_by=session['user_id'],
        )
        db.session.add(new_residence)
        db.session.commit()  # single commit at the end

        flash('Residence added successfully.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error adding residence: {str(e)}', 'danger')

    return redirect(url_for('residence'))


@app.route('/edit_residence/<int:id>')
@login_required
def edit_residence(id):
    residence = Residence.query.filter_by(id=id, deleted_at=None).first()
    if not residence:
        flash('Residence not found.', 'danger')
        return redirect(url_for('residence'))

    all_statuses      = Status.query.all()
    all_residences    = Residence.query.filter(Residence.deleted_at == None).all()
    total_residences  = Residence.query.filter(Residence.deleted_at == None).count()

    return render_template('BarangayAdmin/residence.html',
                           segment='residence',
                           residence=all_residences,
                           statuses=all_statuses,
                           total_residences=total_residences,
                           edit_residence=residence,
                           is_archive=False)


@app.route('/update_residence', methods=['POST'])
@login_required
def update_residence():
    try:
        residence_id = request.form.get('residence_id')
        residence    = Residence.query.get(residence_id)

        if not residence:
            flash('Residence not found.', 'danger')
            return redirect(url_for('residence'))

        new_email = request.form.get('email')

        # Check email conflict excluding current residence's user
        existing_user = User.query.filter(
            User.user_email == new_email,
            User.id != residence.user.id
        ).first()
        if existing_user:
            flash('Email already used by another residence.', 'warning')
            return redirect(url_for('residence'))

        # Update Residence fields
        residence.residence_firstname   = request.form.get('first_name')
        residence.residence_lastname    = request.form.get('last_name')
        residence.residence_middlename  = request.form.get('middle_name')
        residence.residence_suffix      = request.form.get('suffix')
        residence.residence_birthday    = request.form.get('birthday')
        residence.residence_civilStatus = request.form.get('civil_status')
        residence.residence_citizenship = request.form.get('citizenship')
        residence.residence_phoneNumber = request.form.get('phone_number')
        residence.status_id             = request.form.get('status_id')
        residence.updated_at            = datetime.now(timezone.utc)

        # Update Address
        if residence.address:
            residence.address.purok_number      = request.form.get('purok_number')
            residence.address.street_name       = request.form.get('street_name')
            residence.address.house_number      = request.form.get('house_number')
            residence.address.is_head_of_family = request.form.get('is_head_of_family')

        # Update HealthStatus
        if residence.health:
            residence.health.blood_type        = request.form.get('blood_type')
            residence.health.is_pwd            = request.form.get('is_pwd', 0)
            residence.health.disability_type   = request.form.get('disability_type')
            residence.health.is_senior_citizen = request.form.get('is_senior_citizen', 0)

        # Update Demographic
        if residence.demographic:
            residence.demographic.educational_attaiment = request.form.get('educational_attaiment')
            residence.demographic.occupation            = request.form.get('occupation')
            residence.demographic.monthly_income        = request.form.get('monthly_income')
            residence.demographic.is_voter              = request.form.get('is_voter', 0)

        # Update User email and password
        if residence.user:
            residence.user.user_email = new_email
            new_password = request.form.get('password')
            if new_password:
                residence.user.user_password = generate_password_hash(new_password)

        db.session.commit()
        flash('Residence updated successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating residence: {str(e)}', 'danger')

    return redirect(url_for('residence'))


@app.route('/delete_residence/<int:id>', methods=['POST'])
@login_required
def delete_residence(id):
    residence = Residence.query.get_or_404(id)
    try:
        residence.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        flash(f'Residence {residence.residence_firstname} has been moved to archives.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error during deletion: {str(e)}', 'danger')
    return redirect(url_for('residence'))


@app.route('/residences_archive')
@login_required
def residences_archive():
    archived_residences = Residence.query.filter(Residence.deleted_at != None).all()
    all_statuses        = Status.query.all()
    total_archived      = Residence.query.filter(Residence.deleted_at != None).count()

    return render_template('BarangayAdmin/residence.html',
                           segment='residences_archive',
                           residence=archived_residences,
                           statuses=all_statuses,
                           total_residences=total_archived,
                           edit_residence=None,
                           is_archive=True)


@app.route('/restore_residence/<int:id>', methods=['POST'])
@login_required
def restore_residence(id):
    residence = Residence.query.get_or_404(id)
    try:
        residence.deleted_at = None
        db.session.commit()
        flash(f'Residence {residence.residence_firstname} has been restored.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error restoring residence: {str(e)}', 'danger')
    return redirect(url_for('residences_archive'))








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
    app.run(debug=True, port=5001)