from asyncio import current_task
from datetime import datetime, timezone
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from app import app, db, login_required
from models import Residence, Address, HealthStatus, Demographic, Status, User


@app.route('/residence')
@login_required
def residence():
    active_residences = Residence.query.filter(Residence.deleted_at == None).all()
    all_statuses = Status.query.all()
    all_purok = Address.query.all()
    total_residences = Residence.query.filter(Residence.deleted_at == None).count()

    return render_template(
        'BarangayAdmin/residence.html',
        segment='residence',
        residence=active_residences,
        statuses=all_statuses,
        puroks=all_purok,
        total_residences=total_residences,
        view_residence=None,
        edit_residence=None,
        is_archive=False,
    )


@app.route('/add_residence', methods=['POST'])
@login_required
def add_residence():
    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        middle_name = request.form['middle_name']
        suffix = request.form.get('suffix', None)
        birthday = request.form['birthday']
        civil_status = request.form['civil_status']
        citizenship = request.form['citizenship']
        phone_number = request.form.get('phone_number', None)
        status_id = request.form['status_id']
        email = request.form['email']
        password = request.form['password']

        purok_number = request.form.get('purok_number', None)
        street_name = request.form.get('street_name', None)
        house_number = request.form.get('house_number', None)
        is_head_of_family = request.form.get('is_head_of_family', None)

        blood_type = request.form.get('blood_type', None)
        is_pwd = request.form.get('is_pwd', 0)
        disability_type = request.form.get('disability_type', None)
        is_senior_citizen = request.form.get('is_senior_citizen', 0)

        educational_attaiment = request.form.get('educational_attaiment', None)
        occupation = request.form.get('occupation', None)
        monthly_income = request.form.get('monthly_income', None)
        is_voter = request.form.get('is_voter', 0)

        existing_user = User.query.filter_by(user_email=email).first()
        if existing_user:
            flash('Residence with this email already exists.', 'warning')
            return redirect(url_for('residence'))

        new_user = User(
            user_email=email,
            user_password=generate_password_hash(password),
            role_id=3,
        )
        db.session.add(new_user)
        db.session.flush()

        new_address = Address(
            purok_number=purok_number,
            street_name=street_name,
            house_number=house_number,
            is_head_of_family=is_head_of_family,
        )
        db.session.add(new_address)
        db.session.flush()

        new_health = HealthStatus(
            blood_type=blood_type,
            is_pwd=is_pwd,
            disability_type=disability_type,
            is_senior_citizen=is_senior_citizen,
        )
        db.session.add(new_health)
        db.session.flush()

        new_demographic = Demographic(
            educational_attaiment=educational_attaiment,
            occupation=occupation,
            monthly_income=monthly_income,
            is_voter=is_voter,
        )
        db.session.add(new_demographic)
        db.session.flush()

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
            created_by=session['user_id'] if 'user_id' in session else None,
        )
        db.session.add(new_residence)
        db.session.commit()

        flash('Residence added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        # Log the actual error for developers
        app.logger.error(f'Error adding residence: {str(e)}')
        # Show-friendly message to user
        flash('Unable to add residence. Double check your input or contact support.', 'danger')

    return redirect(url_for('residence'))


@app.route('/edit_residence/<int:id>')
@login_required
def edit_residence(id):
    residence = Residence.query.filter_by(id=id, deleted_at=None).first()
    if not residence:
        flash('Residence not found.', 'danger')
        return redirect(url_for('residence'))

    all_statuses = Status.query.all()
    all_residences = Residence.query.filter(Residence.deleted_at == None).all()
    total_residences = Residence.query.filter(Residence.deleted_at == None).count()

    return render_template(
        'BarangayAdmin/residence.html',
        segment='residence',
        residence=all_residences,
        statuses=all_statuses,
        total_residences=total_residences,
        edit_residence=residence,
        is_archive=False,
        view_residence=None,
    )


@app.route('/view_residence/<int:id>')
@login_required
def view_residence(id):
    residence = Residence.query.get_or_404(id)
    if residence.deleted_at:
        return redirect(url_for('residence'))

    all_statuses = Status.query.all()
    all_residences = Residence.query.filter_by(deleted_at=None).all()

    return render_template(
        'BarangayAdmin/residence.html',
        segment='residence',
        view_residence=residence,
        statuses=all_statuses,
        residence=all_residences,
        edit_residence=None,
    )


@app.route('/update_residence', methods=['POST'])
@login_required
def update_residence():
    try:
        residence_id = request.form.get('residence_id')
        residence = Residence.query.get(residence_id)

        if not residence:
            flash('Residence not found.', 'danger')
            return redirect(url_for('residence'))

        new_email = request.form.get('email')
        existing_user = User.query.filter(
            User.user_email == new_email,
            User.id != residence.user.id,
        ).first()
        if existing_user:
            flash('Email already used by another residence.', 'warning')
            return redirect(url_for('residence'))

        residence.residence_firstname = request.form.get('first_name')
        residence.residence_lastname = request.form.get('last_name')
        residence.residence_middlename = request.form.get('middle_name')
        residence.residence_suffix = request.form.get('suffix')
        residence.residence_birthday = request.form.get('birthday')
        residence.residence_civilStatus = request.form.get('civil_status')
        residence.residence_citizenship = request.form.get('citizenship')
        residence.residence_phoneNumber = request.form.get('phone_number')
        residence.status_id = request.form.get('status_id')
        residence.updated_at = datetime.now(timezone.utc)

        if residence.address:
            residence.address.purok_number = request.form.get('purok_number')
            residence.address.street_name = request.form.get('street_name')
            residence.address.house_number = request.form.get('house_number')
            residence.address.is_head_of_family = request.form.get('is_head_of_family')

        if residence.health:
            residence.health.blood_type = request.form.get('blood_type')
            residence.health.is_pwd = request.form.get('is_pwd', 0)
            residence.health.disability_type = request.form.get('disability_type')
            residence.health.is_senior_citizen = request.form.get('is_senior_citizen', 0)

        if residence.demographic:
            residence.demographic.educational_attaiment = request.form.get('educational_attaiment')
            residence.demographic.occupation = request.form.get('occupation')
            residence.demographic.monthly_income = request.form.get('monthly_income')
            residence.demographic.is_voter = request.form.get('is_voter', 0)

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
    all_statuses = Status.query.all()
    total_archived = Residence.query.filter(Residence.deleted_at != None).count()

    return render_template(
        'BarangayAdmin/residence.html',
        segment='residences_archive',
        residence=archived_residences,
        statuses=all_statuses,
        total_residences=total_archived,
        edit_residence=None,
        is_archive=True,
    )


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
