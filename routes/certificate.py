from datetime import datetime, timezone
from io import BytesIO
from flask import render_template, request, make_response
from app import app, login_required
from models import Employee, Residence


@app.route('/certificates')
@login_required
def certificates():
    employees = Employee.query.filter(Employee.deleted_at == None).all()
    residences = Residence.query.filter(Residence.deleted_at == None).all()
    return render_template(
        'BarangayAdmin/certificates.html',
        segment='certificates',
        employees=employees,
        residences=residences,
    )


@app.route('/certificate/employee-clearance/<int:employee_id>')
@login_required
def employee_clearance(employee_id):
    from xhtml2pdf import pisa

    employee = Employee.query.filter_by(id=employee_id, deleted_at=None).first_or_404()
    html = render_template(
        'BarangayAdmin/certificate/employee_clearance.html',
        employee=employee,
        issued_date=datetime.now(timezone.utc),
        barangay_name='Barangay Salimbao',
        municipality='General Santos City',
        captain_name='Hon. Ricardo Cruz Jr.',
    )

    buf = BytesIO()
    pisa.CreatePDF(html, dest=buf)
    buf.seek(0)

    response = make_response(buf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="clearance_{employee.id}.pdf"'
    return response


@app.route('/certificate/residency/<int:residence_id>')
@login_required
def residency_certificate(residence_id):
    from xhtml2pdf import pisa

    residence = Residence.query.filter_by(id=residence_id, deleted_at=None).first_or_404()
    purpose = request.args.get('purpose', 'whatever purpose it may serve')
    html = render_template(
        'BarangayAdmin/certificate/residency_certificate.html',
        residence=residence,
        issued_date=datetime.now(timezone.utc),
        purpose=purpose,
        barangay_name='Barangay Salimbao',
        municipality='General Santos City',
        captain_name='Hon. Ricardo Cruz Jr.',
    )

    buf = BytesIO()
    pisa.CreatePDF(html, dest=buf)
    buf.seek(0)

    response = make_response(buf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="residency_{residence_id}.pdf"'
    return response
