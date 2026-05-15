from flask import render_template
from app import app, login_required


@app.route('/finances')
@login_required
def finances():
    return render_template('BarangayAdmin/finances.html', segment='finances')
