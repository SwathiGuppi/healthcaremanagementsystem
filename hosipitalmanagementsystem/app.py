from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL


app = Flask(__name__)

app.secret_key = "healthcare_secret"


# MySQL Configuration

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Swathi@003'
app.config['MYSQL_DB'] = 'healthcare'


mysql = MySQL(app)



# Home

@app.route('/')
def home():

    return render_template('index.html')




# Register

@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']


        cur = mysql.connection.cursor()


        cur.execute(
            """
            INSERT INTO patients(name,email,password)
            VALUES(%s,%s,%s)
            """,
            (name,email,password)
        )


        mysql.connection.commit()

        cur.close()


        return redirect('/login')


    return render_template('register.html')





# Login

@app.route('/login', methods=['GET','POST'])
def login():


    if request.method == 'POST':


        email = request.form['email']
        password = request.form['password']


        cur = mysql.connection.cursor()


        cur.execute(
            """
            SELECT * FROM patients
            WHERE email=%s AND password=%s
            """,
            (email,password)
        )


        user = cur.fetchone()


        cur.close()



        if user:


            session['patient_id'] = user[0]

            session['patient_name'] = user[1]


            return redirect('/dashboard')



        else:

            return "Invalid Email or Password"



    return render_template('login.html')






# Dashboard

@app.route('/dashboard')
def dashboard():


    cur = mysql.connection.cursor()



    # Total Patients

    cur.execute("SELECT COUNT(*) FROM patients")

    patients = cur.fetchone()[0]




    # Total Doctors

    cur.execute("SELECT COUNT(*) FROM doctors")

    doctors = cur.fetchone()[0]




    # Total Appointments

    cur.execute("SELECT COUNT(*) FROM appointments")

    appointments = cur.fetchone()[0]





    # Doctor Availability

    cur.execute(
        """
        SELECT name, specialization, status
        FROM doctors
        LIMIT 5
        """
    )


    doctor_status = cur.fetchall()





    # Recent Appointments

    cur.execute(
        """
        SELECT patient_name,
               doctor_name,
               appointment_date
        FROM appointments
        ORDER BY appointment_date DESC
        LIMIT 5
        """
    )


    recent = cur.fetchall()



    cur.close()




    return render_template(

        "dashboard.html",

        patients=patients,

        doctors=doctors,

        appointments=appointments,

        recent=recent,

        doctor_status=doctor_status

    )







# Database Test

@app.route('/test')
def test():

    cur = mysql.connection.cursor()

    cur.execute("SELECT 1")

    cur.close()


    return "Database Connected Successfully!"







# Doctors Search

@app.route('/doctors')
def doctors():


    specialization = request.args.get('specialization')


    cur = mysql.connection.cursor()



    if specialization:


        cur.execute(
            """
            SELECT *
            FROM doctors
            WHERE specialization LIKE %s
            """,
            ('%' + specialization + '%',)
        )


    else:


        cur.execute(
            "SELECT * FROM doctors"
        )



    doctors = cur.fetchall()



    cur.close()



    return render_template(

        'doctors.html',

        doctors=doctors

    )







# Appointment Booking

@app.route('/appointment', methods=['GET','POST'])
def appointment():


    doctor_name = request.args.get('doctor')



    if request.method == "POST":



        patient_name = request.form['patient_name']

        doctor_name = request.form['doctor_name']

        appointment_date = request.form['appointment_date']




        cur = mysql.connection.cursor()



        cur.execute(
            
            """
INSERT INTO appointments
(patient_name,doctor_name,appointment_date,status)
VALUES(%s,%s,%s,%s)
            """,
            (
            patient_name,
            doctor_name,
            appointment_date,
            "Pending"

            )
        )



        mysql.connection.commit()


        cur.close()



        return "Appointment Booked Successfully"





    return render_template(

        "appointment.html",

        doctor_name=doctor_name,

        patient_name=session.get('patient_name')

    )







# All Appointments

@app.route('/appointments')
def appointments():


    cur = mysql.connection.cursor()



    cur.execute(
        "SELECT * FROM appointments"
    )



    appointments = cur.fetchall()



    cur.close()



    return render_template(

        'appointments.html',

        appointments=appointments

    )


# My Appointments

@app.route('/my_appointments')
def my_appointments():


    patient_name=session.get('patient_name')



    cur=mysql.connection.cursor()



    cur.execute(

        """
        SELECT *
        FROM appointments
        WHERE patient_name=%s
        """,

        (patient_name,)

    )



    appointments=cur.fetchall()



    cur.close()



    return render_template(

        "my_appointments.html",

        appointments=appointments

    )







# AI Symptom Checker


@app.route('/update_status/<int:id>/<status>')
def update_status(id,status):
 
    cur = mysql.connection.cursor()


    cur.execute(
        """
        UPDATE appointments
        SET status=%s
        WHERE id=%s
        """,
        (status,id)
    )


    mysql.connection.commit()

    cur.close()


    return redirect('/appointments')


# AI Symptom Checker

@app.route('/symptom_checker', methods=['GET','POST'])
def symptom_checker():


    result=""

    specialization=""

    doctors=[]



    if request.method=="POST":


        symptoms=request.form['symptoms'].lower()



        if "fever" in symptoms or "cough" in symptoms:


            result="Possible Fever / Viral Infection"

            specialization="General Physician"



        elif "chest pain" in symptoms:


            result="Possible Heart Related Issue"

            specialization="Cardiologist"



        elif "headache" in symptoms:


            result="Possible Migraine"

            specialization="Neurologist"



        elif "skin" in symptoms:


            result="Possible Skin Problem"

            specialization="Dermatologist"



        else:


            result="General Checkup Recommended"

            specialization="General Physician"




        cur=mysql.connection.cursor()



        cur.execute(

            """
            SELECT *
            FROM doctors
            WHERE specialization LIKE %s
            """,

            ('%' + specialization + '%',)

        )



        doctors=cur.fetchall()


        cur.close()




    return render_template(

        "symptom_checker.html",

        result=result,

        specialization=specialization,

        doctors=doctors

    )

# Doctor Login

@app.route('/doctor_login', methods=['GET','POST'])
def doctor_login():

    if request.method == "POST":

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            """
            SELECT *
            FROM doctors
            WHERE email=%s AND password=%s
            """,
            (email,password)
        )

        doctor = cur.fetchone()

        cur.close()

        if doctor:

            session['doctor_id'] = doctor[0]
            session['doctor_name'] = doctor[1]

            return redirect('/doctor_dashboard')

        else:

            return "Invalid Doctor Login"

    return render_template("doctor_login.html")



# Doctor Dashboard

@app.route('/doctor_dashboard')
def doctor_dashboard():

    if 'doctor_id' not in session:
        return redirect('/doctor_login')

    doctor_name = session['doctor_name']

    cur = mysql.connection.cursor()


    cur.execute("""
        SELECT *
        FROM doctors
        WHERE id=%s
    """, (session['doctor_id'],))


    doctor = cur.fetchone()



    cur.execute("""
        SELECT *
        FROM appointments
        WHERE doctor_name=%s
        ORDER BY appointment_date
    """, (doctor_name,))


    appointments = cur.fetchall()


    total = len(appointments)


    cur.close()


    return render_template(
        "doctor_dashboard.html",
        doctor=doctor,
        appointments=appointments,
        total=total
    )



# ADD NEW CODE BELOW THIS 👇


@app.route('/doctor_update/<int:id>/<status>')
def doctor_update(id,status):

    cur=mysql.connection.cursor()


    cur.execute(
    """
    UPDATE appointments

    SET status=%s

    WHERE id=%s

    """,
    (status,id)
    )


    mysql.connection.commit()


    cur.close()


    return redirect('/doctor_dashboard')

@app.route('/doctor_status/<status>')
def doctor_status(status):

    if 'doctor_id' not in session:
        return redirect('/doctor_login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        UPDATE doctors
        SET status=%s
        WHERE id=%s
        """,
        (status, session['doctor_id'])
    )

    mysql.connection.commit()

    cur.close()

    return redirect('/doctor_dashboard')

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        print("Username =", username)
        print("Password =", password)

        if username == "admin" and password == "admin123":
            print("SUCCESS")
            session['admin'] = True
            return redirect('/admin')
        else:
            print("FAILED")
            return "Invalid Admin Credentials"

    return render_template("admin_login.html")

# -----------------------------
# ADMIN DASHBOARD
# -----------------------------

@app.route('/admin')
def admin():

    if 'admin' not in session:
        return redirect('/admin_login')


    cur = mysql.connection.cursor()



    # Total Patients
    cur.execute(
        "SELECT COUNT(*) FROM patients"
    )

    total_patients = cur.fetchone()[0]



    # Total Doctors
    cur.execute(
        "SELECT COUNT(*) FROM doctors"
    )

    total_doctors = cur.fetchone()[0]



    # Total Appointments
    cur.execute(
        "SELECT COUNT(*) FROM appointments"
    )

    total_appointments = cur.fetchone()[0]




    # Pending Appointments
    cur.execute(
        """
        SELECT COUNT(*)
        FROM appointments
        WHERE status='Pending'
        """
    )

    pending = cur.fetchone()[0]




    # Completed Appointments
    cur.execute(
        """
        SELECT COUNT(*)
        FROM appointments
        WHERE status='Completed'
        """
    )

    completed = cur.fetchone()[0]





    # Recent Appointments

    cur.execute(
        """
        SELECT *
        FROM appointments
        ORDER BY appointment_date DESC
        LIMIT 5
        """
    )


    recent = cur.fetchall()



    cur.close()



    return render_template(

        "admin.html",

        total_patients=total_patients,

        total_doctors=total_doctors,

        total_appointments=total_appointments,

        pending=pending,

        completed=completed,

        recent=recent

    )

@app.route('/manage_doctors')
def manage_doctors():

    if 'admin' not in session:
        return redirect('/admin_login')

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT id,
               name,
               specialization,
               email,
               phone,
               status
        FROM doctors
        ORDER BY name
    """)

    doctors = cur.fetchall()

    cur.close()

    return render_template(
        "manage_doctors.html",
        doctors=doctors
    )
@app.route('/add_doctor', methods=['GET','POST'])
def add_doctor():

    if 'admin' not in session:
        return redirect('/admin_login')

    if request.method == "POST":

        name = request.form['name']
        specialization = request.form['specialization']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO doctors
            (name,specialization,email,password,phone,status)
            VALUES(%s,%s,%s,%s,%s,%s)
        """,(name,specialization,email,password,phone,"Available"))

        mysql.connection.commit()

        cur.close()

        return redirect('/manage_doctors')

    return render_template("add_doctor.html")

@app.route('/edit_doctor/<int:id>', methods=['GET','POST'])
def edit_doctor(id):

    if 'admin' not in session:
        return redirect('/admin_login')

    cur = mysql.connection.cursor()

    if request.method == "POST":

        name = request.form['name']
        specialization = request.form['specialization']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        status = request.form['status']

        cur.execute("""
            UPDATE doctors
            SET name=%s,
                specialization=%s,
                email=%s,
                password=%s,
                phone=%s,
                status=%s
            WHERE id=%s
        """,(name,specialization,email,password,phone,status,id))

        mysql.connection.commit()

        cur.close()

        return redirect('/manage_doctors')

    cur.execute("SELECT * FROM doctors WHERE id=%s",(id,))
    doctor = cur.fetchone()

    cur.close()

    return render_template("edit_doctor.html",doctor=doctor)
@app.route('/delete_doctor/<int:id>')
def delete_doctor(id):

    if 'admin' not in session:
        return redirect('/admin_login')

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM doctors WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    cur.close()

    return redirect('/manage_doctors') 
@app.route('/manage_patients')
def manage_patients():

    cursor=mysql.connection.cursor()

    cursor.execute("SELECT * FROM patients")

    patients=cursor.fetchall()

    cursor.close()

    return render_template(
        "manage_patients.html",
        patients=patients
    )
@app.route('/add_patient', methods=['GET','POST'])
def add_patient():

    if request.method=="POST":

        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        age=request.form['age']
        gender=request.form['gender']
        phone=request.form['phone']
        disease=request.form['disease']
        doctor=request.form['doctor']


        cursor=mysql.connection.cursor()


        cursor.execute(
        """
        INSERT INTO patients
        (name,email,password,age,gender,phone,disease,doctor)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
        name,
        email,
        password,
        age,
        gender,
        phone,
        disease,
        doctor
        )
        )


        mysql.connection.commit()

        cursor.close()


        return redirect('/manage_patients')


    return render_template('add_patient.html')
@app.route('/edit_patient/<int:id>', methods=['GET','POST'])
def edit_patient(id):

    cursor = mysql.connection.cursor()


    if request.method == "POST":


        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        disease = request.form['disease']
        doctor = request.form['doctor']



        cursor.execute(
        """
        UPDATE patients

        SET 
        name=%s,
        email=%s,
        age=%s,
        gender=%s,
        phone=%s,
        disease=%s,
        doctor=%s

        WHERE id=%s

        """,

        (
        name,
        email,
        age,
        gender,
        phone,
        disease,
        doctor,
        id
        )
        )


        mysql.connection.commit()

        cursor.close()


        return redirect('/manage_patients')



    cursor.execute(
        "SELECT * FROM patients WHERE id=%s",
        (id,)
    )


    patient = cursor.fetchone()


    cursor.close()



    return render_template(
        "edit_patient.html",
        patient=patient
    )
@app.route('/delete_patient/<int:id>')
def delete_patient(id):


    cursor=mysql.connection.cursor()


    cursor.execute(
    "DELETE FROM patients WHERE id=%s",
    (id,)
    )


    mysql.connection.commit()


    cursor.close()


    return redirect('/manage_patients')

@app.route('/manage_appointments')
def manage_appointments():

    cursor=mysql.connection.cursor()


    cursor.execute(
        "SELECT * FROM appointments"
    )


    appointments=cursor.fetchall()


    cursor.close()


    return render_template(
        "manage_appointments.html",
        appointments=appointments
    )
@app.route('/update_appointment/<int:id>/<status>')
def update_appointment(id,status):

    cursor=mysql.connection.cursor()


    cursor.execute(
    """
    UPDATE appointments

    SET status=%s

    WHERE id=%s

    """,
    (status,id)
    )


    mysql.connection.commit()


    cursor.close()


    return redirect('/manage_appointments')
@app.route('/delete_appointment/<int:id>')
def delete_appointment(id):

    cursor=mysql.connection.cursor()


    cursor.execute(
    "DELETE FROM appointments WHERE id=%s",
    (id,)
    )


    mysql.connection.commit()


    cursor.close()


    return redirect('/manage_appointments')


@app.route('/book_appointment', methods=['GET','POST'])
def book_appointment():

    if request.method=="POST":


        patient_name = request.form['patient']

        doctor_name = request.form['doctor']

        appointment_date = request.form['date']

        time = request.form['time']


        status = "Pending"



        cursor = mysql.connection.cursor()


        cursor.execute(
        """
        INSERT INTO appointments
        (patient_name,
        doctor_name,
        appointment_date,
        status,
        time)

        VALUES(%s,%s,%s,%s,%s)

        """,

        (
        patient_name,
        doctor_name,
        appointment_date,
        status,
        time
        )
        )


        mysql.connection.commit()


        cursor.close()


        return redirect('/manage_appointments')



    return render_template("book_appointment.html")
# -----------------------------
# LOGOUT
# -----------------------------

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

if __name__ == '__main__':

    app.run(debug=True)