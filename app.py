from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', segment='dashboard')

@app.route('/employees')
def employees():
    return render_template('employees.html', segment='employees')    

@app.route('/finances')
def finances():
    return render_template('finances.html', segment='finances')

@app.route('/certificates')
def certificates():
    return render_template('certificates.html', segment='certificates')



if __name__ == '__main__':
    app.run(debug=True)