from flask import Flask, render_template, request, redirect, url_for, session
from db import connection

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session management

# In-memory database
patients = {}
current_id = 1000  # Starting ID

# Doctor credentials
DOCTOR_ID = "doc123"
DOCTOR_PASSWORD = "321"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/doctor-login', methods=['POST'])
def doctor_login():
    doctor_id = request.form.get('doctor_id')
    password = request.form.get('password')
    
    # Check for specific doctor credentials
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM doctors WHERE doctor_id = %s AND password = %s", (doctor_id, password))
    doctor = cursor.fetchone()
    cursor.close()
    if doctor:
        session['doctor_id'] = doctor_id
        session['doctor_name'] = doctor[1]
        return redirect(url_for('doctor_dashboard'))
    else:
        # If login fails, redirect back to login page
        return redirect(url_for('login_page'))

@app.route('/doctor-dashboard')
def doctor_dashboard():
    # Check if doctor is logged in
    if 'doctor_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('doctor_dashboard.html', doctor_name=session.get('doctor_name'))

@app.route('/search-patient', methods=['POST'])
def search_patient():
    if 'doctor_id' not in session:
        return redirect(url_for('login_page'))
    
    patient_id = request.form.get('patient_id')
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    patient = cursor.fetchone()
    cursor.close()
    if patient:
        patient = {
        'patient_id': patient[0],
        'name': patient[1],
        'age': patient[2],
        'blood_group': patient[3],
        'weight': patient[5],
        'height': patient[6],
        'disease': patient[7],
        'phone': patient[8]
        }
        return render_template('doctor_dashboard.html', 
                             doctor_name=session.get('doctor_name'),
                             patient=patient,
                             active_section='view-patients')
    else:
        return render_template('doctor_dashboard.html', 
                             doctor_name=session.get('doctor_name'),
                             error="Patient not found",
                             active_section='view-patients')

@app.route('/edit-patient/<patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    if 'doctor_id' not in session:
        return redirect(url_for('login_page'))
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    patient = cursor.fetchone()
    cursor.close()
    patient = {
        'patient_id': patient[0],
        'name': patient[1],
        'age': patient[2],
        'blood_group': patient[3],
        'weight': patient[5],
        'height': patient[6],
        'disease': patient[7],
        'phone': patient[8]
    }
    if not patient:
        return redirect(url_for('doctor_dashboard'))
    
    if request.method == 'POST':
        # Update patient information
        cursor = connection.cursor()
        cursor.execute("UPDATE patients SET name = %s, age = %s, blood_group = %s, weight = %s, height = %s, disease = %s, phone = %s WHERE patient_id = %s",
                       (request.form.get('name'), request.form.get('age'), request.form.get('blood_group'), request.form.get('weight'), request.form.get('height'), request.form.get('disease'), request.form.get('phone'), patient_id))
        connection.commit()
        cursor.close()
        return redirect(url_for('search_patient', patient_id=patient_id))
    
    return render_template('edit_patient.html', patient=patient)

@app.route('/delete-patient/<patient_id>')
def delete_patient(patient_id):
    if 'doctor_id' not in session:
        return redirect(url_for('login_page'))
    
    cursor = connection.cursor()
    cursor.execute("DELETE FROM patients WHERE patient_id = %s", (patient_id,))
    connection.commit()
    cursor.close()
    
    return redirect(url_for('doctor_dashboard'))

@app.route('/patient-dashboard', methods=['GET', 'POST'])
def patient_dashboard():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        cursor.close()
        if patient:
            limited_patient = {
                'age': patient[2],
                'blood_group': patient[3],
                'weight': patient[5],
                'height': patient[6],
                'disease': patient[7]
            }
            return render_template('patient_dashboard.html', patient=limited_patient)
        else:
            return render_template('patient_dashboard.html', error='Patient ID not found')
    return render_template('patient_dashboard.html')

@app.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        if patient_id in patients:
            # Create a limited patient view without sensitive information
            limited_patient = {
                'age': patients[patient_id]['age'],
                'blood_group': patients[patient_id]['blood_group'],
                'weight': patients[patient_id]['weight'],
                'height': patients[patient_id]['height'],
                'disease': patients[patient_id]['disease']
            }
            return render_template('login.html', patient=limited_patient)
        else:
            return render_template('login.html', error='Patient ID not found')
    return render_template('login.html')

@app.route('/add-patient', methods=['POST'])
def add_patient():
    if 'doctor_id' not in session:
        return redirect(url_for('login_page'))
    
    patient_id = request.form.get('patient_id')
    patient_data = {
        'patient_id': patient_id,
        'name': request.form.get('name'),
        'age': request.form.get('age'),
        'blood_group': request.form.get('blood_group'),
        'weight': request.form.get('weight'),
        'height': request.form.get('height'),
        'disease': request.form.get('disease'),
        'phone': request.form.get('phone')
    }
    
    cursor = connection.cursor()
    cursor.execute("INSERT INTO patients (patient_id, name, age, blood_group,doctor_id, weight, height, disease, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)",
                   (patient_id, patient_data['name'], patient_data['age'], patient_data['blood_group'], session['doctor_id'], patient_data['weight'], patient_data['height'], patient_data['disease'], patient_data['phone']))
    connection.commit()
    cursor.close()
    
    return redirect(url_for('doctor_dashboard'))

@app.route('/view_patient', methods=['GET', 'POST'])
def view_patient():
    if not session.get('doctor_logged_in'):
        return redirect(url_for('doctor_login'))
    
    patient = None
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        #patient = patients.get(user_id)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (user_id,))
        patient = cursor.fetchone()
    return render_template('view_patient.html', patient=patient)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/limited-search', methods=['POST'])
def limited_search():
    if 'doctor_id' not in session:
        return redirect(url_for('login_page'))
    
    patient_id = request.form.get('patient_id')
    
    # Search for patient in the database
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    patient = cursor.fetchone()
    cursor.close()
    
    if patient:
        # Create a limited view without sensitive information
        limited_patient = {
            'age': patient[2],
            'blood_group': patient[3],
            'weight': patient[5],
            'height': patient[6],
            'disease': patient[7]
        }
        return render_template('doctor_dashboard.html', 
                             doctor_name=session.get('doctor_name'),
                             limited_patient=limited_patient,
                             active_section='patient-search')
    else:
        return render_template('doctor_dashboard.html', 
                             doctor_name=session.get('doctor_name'),
                             search_error="Patient not found",
                             active_section='patient-search')

if __name__ == '__main__':
    app.run(debug=True)
