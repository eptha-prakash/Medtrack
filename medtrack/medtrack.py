from flask import Flask, render_template, request, redirect, session, flash
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# ---------------- LOCAL DATA STORE ----------------
users = {}  # key: email, value: user dict
appointments = {}  # key: appointment_id, value: appointment dict

# ---------------- ROUTES ----------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']
        spec = request.form.get('specialization', '')

        if email in users:
            flash('User already exists.', 'danger')
            return redirect('/register')

        user = {
            'email': email,
            'name': name,
            'password': password,
            'age': age,
            'gender': gender,
            'role': role,
            'created_at': datetime.now().isoformat()
        }
        if role == 'doctor':
            user['specialization'] = spec

        users[email] = user
        flash('Registered successfully. Please log in.', 'success')
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        user = users.get(email)
        if user and user['password'] == password and user['role'] == role:
            session['email'] = email
            session['role'] = role
            session['name'] = user['name']
            return redirect('/doctor' if role == 'doctor' else '/patient')
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/doctor')
def doctor_dashboard():
    if session.get('role') != 'doctor':
        return redirect('/')
    doctor_email = session['email']
    appts = [a for a in appointments.values() if a['doctor_email'] == doctor_email]
    return render_template('doctor_dashboard.html', appointments=appts)

@app.route('/patient')
def patient_dashboard():
    if session.get('role') != 'patient':
        return redirect('/')
    patient_email = session['email']
    appts = [a for a in appointments.values() if a['patient_email'] == patient_email]
    doctors = [u for u in users.values() if u['role'] == 'doctor']
    return render_template('patient_dashboard.html', appointments=appts, doctors=doctors)

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if request.method == 'POST':
        doctor_email = request.form['doctor_email']
        symptoms = request.form['symptoms']
        date = request.form['appointment_date']

        appointment_id = str(uuid.uuid4())
        appointment = {
            'appointment_id': appointment_id,
            'doctor_email': doctor_email,
            'patient_email': session['email'],
            'doctor_name': users[doctor_email]['name'],
            'patient_name': session['name'],
            'symptoms': symptoms,
            'status': 'pending',
            'appointment_date': date,
            'created_at': datetime.now().isoformat()
        }
        appointments[appointment_id] = appointment
        flash('Appointment booked!', 'success')
        return redirect('/patient')

    doctors = [u for u in users.values() if u['role'] == 'doctor']
    return render_template('book_appointment.html', doctors=doctors)

@app.route('/view_appointment/<appointment_id>', methods=['GET', 'POST'])
def view_appointment(appointment_id):
    appt = appointments.get(appointment_id)
    if not appt:
        return "Appointment not found", 404

    if request.method == 'POST' and session['role'] == 'doctor':
        appt['diagnosis'] = request.form['diagnosis']
        appt['treatment_plan'] = request.form['treatment_plan']
        appt['prescription'] = request.form['prescription']
        appt['status'] = 'completed'
        flash('Appointment updated successfully.', 'success')
        return redirect('/doctor')

    template = 'view_appointment_doctor.html' if session['role'] == 'doctor' else 'view_appointment_patient.html'
    return render_template(template, appointment=appt)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
