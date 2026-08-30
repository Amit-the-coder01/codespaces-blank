import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'hr-db')
DB_NAME = os.getenv('DB_NAME', 'hr_database')
DB_USER = os.getenv('DB_USER', 'hr_admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'HR_Secure_Password_2026')

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

@app.route('/')
def index():
    message = request.args.get('message')
    employees = []
    try:
        # Fetch all existing records to display live on the full-stack UI
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT emp_id, first_name, last_name, email, status FROM employees ORDER BY emp_id DESC;")
        employees = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error fetching directory: {e}")
        
    return render_template('index.html', message=message, employees=employees)

@app.route('/add', methods=['POST'])
def add_employee():
    first_name = request.form['first_name'].strip()
    last_name = request.form['last_name'].strip()
    email = request.form['email'].strip()
    status = request.form['status']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (first_name, last_name, email, status) VALUES (%s, %s, %s, %s);",
            (first_name, last_name, email, status)
        )
        conn.commit()
        cursor.close()
        conn.close()
        msg = f"Audit Log: Successfully registered {first_name} {last_name}."
    except Exception as e:
        msg = f"Governance Alert: Transaction failed. Reason: {e}"
        
    return redirect(url_for('index', message=msg))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)