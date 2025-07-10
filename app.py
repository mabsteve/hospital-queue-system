from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            symptoms TEXT,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            checkin_time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

priority_order = {'Emergency': 1, 'Serious': 2, 'Normal': 3}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        symptoms = request.form['symptoms']
        priority = request.form['priority']
        checkin_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = 'waiting'

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO patients (name, symptoms, priority, status, checkin_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, symptoms, priority, status, checkin_time))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        cursor.execute('UPDATE patients SET status = "served" WHERE id = ?', (patient_id,))
        conn.commit()

    cursor.execute('''
        SELECT * FROM patients
        WHERE status = "waiting"
        ORDER BY 
            CASE priority 
                WHEN 'Emergency' THEN 1
                WHEN 'Serious' THEN 2
                WHEN 'Normal' THEN 3
            END,
            checkin_time ASC
    ''')
    patients = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', patients=patients)

if __name__ == '__main__':
    app.run(debug=True)