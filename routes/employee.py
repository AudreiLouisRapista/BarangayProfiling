from datetime import datetime, timezone
from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app import app, db, login_required
from models import Employee, Position, Status, User


@app.route('/employees')
@login_required
def employees():
    active_employees = Employee.query.filter(Employee.deleted_at == None).all()
    all_positions = Position.query.all()
    all_statuses = Status.query.all()
    user_credentials = User.query.all()
    total_employees = Employee.query.filter(Employee.deleted_at == None).count()

    return render_template(
        'BarangayAdmin/employees.html',
        segment='employees',
        employees=active_employees,
        positions=all_positions,
        statuses=all_statuses,
        user=user_credentials,
        total_employees=total_employees,
        edit_employee=None,
        is_archive=False,
    )


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

        existing_user = User.query.filter_by(user_email=employee_email).first()
        if existing_user:
            flash('Employee with this email already exists.', 'warning')
            return redirect(url_for('employees'))

        new_user = User(
            user_email=employee_email,
            user_password=generate_password_hash(password),
            role_id=3,
        )
        db.session.add(new_user)
        db.session.flush()

        new_employee = Employee(
            employee_firstname=first_name,
            employee_lastname=last_name,
            position_id=position_id,
            status_id=status_id,
            employee_phonenumber=phone_number,
            user_id=new_user.id,
            term_start_date=datetime.now(timezone.utc),
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

    all_positions = Position.query.all()
    all_employees = Employee.query.filter(Employee.deleted_at == None).all()
    all_statuses = Status.query.all()
    total_employees = Employee.query.filter(Employee.deleted_at == None).count()

    return render_template(
        'BarangayAdmin/employees.html',
        segment='employees',
        employees=all_employees,
        positions=all_positions,
        statuses=all_statuses,
        total_employees=total_employees,
        edit_employee=employee,
        is_archive=False,
    )


@app.route('/update_employee', methods=['POST'])
@login_required
def update_employee():
    try:
        employee_id = request.form.get('employee_id')
        employee = Employee.query.get(employee_id)

        if not employee:
            flash('Employee not found.', 'danger')
            return redirect(url_for('employees'))

        new_email = request.form.get('employee_email')
        existing_user = User.query.filter(
            User.user_email == new_email,
            User.id != employee.user.id,
        ).first()

        if existing_user:
            flash('Email already used by another employee.', 'warning')
            return redirect(url_for('employees'))

        employee.employee_firstname = request.form.get('first_name')
        employee.employee_lastname = request.form.get('last_name')
        employee.position_id = request.form.get('position_id')
        employee.status_id = request.form.get('status_id')
        employee.employee_phonenumber = request.form.get('phone_number')
        employee.updated_at = datetime.now(timezone.utc)

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
        flash(f'Employee {employee.employee_firstname} has been moved to archives.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error during deletion: {str(e)}', 'danger')
    return redirect(url_for('employees'))


@app.route('/employees_archive')
@login_required
def employees_archive():
    archived_employees = Employee.query.filter(Employee.deleted_at != None).all()
    all_positions = Position.query.all()
    all_statuses = Status.query.all()
    total_archived = Employee.query.filter(Employee.deleted_at != None).count()

    return render_template(
        'BarangayAdmin/employees.html',
        segment='employees_archive',
        employees=archived_employees,
        positions=all_positions,
        statuses=all_statuses,
        total_employees=total_archived,
        edit_employee=None,
        is_archive=True,
    )


@app.route('/restore_employee/<int:id>', methods=['POST'])
@login_required
def restore_employee(id):
    employee = Employee.query.get_or_404(id)
    try:
        employee.restore()
        flash(f'Employee {employee.employee_firstname} has been restored.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error restoring employee: {str(e)}', 'danger')
    return redirect(url_for('employees_archive'))
