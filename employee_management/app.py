# app.py
from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for sessions

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="minahil12",
    database="employee_management"
)

@app.route('/')
def home():
    return redirect('/select')

@app.route('/select', methods=['GET', 'POST'])
def select():
    if request.method == 'POST':
        session['domain'] = request.form['domain']
        action = request.form['action']
        return redirect(url_for(action))
    return render_template('select.html')

@app.route('/view', methods=['GET'])
def view():
    cursor = db.cursor(dictionary=True)
    domain = session.get('domain')
    cursor.execute("""
        SELECT e.id, e.name, e.dob, e.position, e.salary,
               d.department_name, dom.domain_name
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        JOIN domains dom ON d.domain_id = dom.id
        WHERE dom.domain_name = %s
    """, (domain,))
    employees = cursor.fetchall()
    for emp in employees:
        emp['age'] = datetime.now().year - emp['dob'].year
    return render_template('view.html', employees=employees, domain=domain)

@app.route('/search', methods=['GET', 'POST'])
def search():
    cursor = db.cursor(dictionary=True)
    domain = session.get('domain')
    results = []
    query = None

    if request.method == 'POST':
        query = request.form['query']
        cursor.execute("""
            SELECT e.id, e.name, e.dob, e.position, e.salary,
                   d.department_name, dom.domain_name
            FROM employees e
            JOIN departments d ON e.department_id = d.id
            JOIN domains dom ON d.domain_id = dom.id
            WHERE dom.domain_name = %s AND (e.name LIKE %s OR e.position LIKE %s)
        """, (domain, f"%{query}%", f"%{query}%"))
        results = cursor.fetchall()
        for emp in results:
            emp['age'] = datetime.now().year - emp['dob'].year

    return render_template('search.html', employees=results, query=query, domain=domain)

@app.route('/add', methods=['GET', 'POST'])
def add():
    cursor = db.cursor(dictionary=True)
    domain = session.get('domain')
    cursor.execute("SELECT d.* FROM departments d JOIN domains dom ON d.domain_id = dom.id WHERE dom.domain_name = %s", (domain,))
    departments = cursor.fetchall()

    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        position = request.form['position']
        salary = request.form['salary']
        department_id = request.form['department_id']

        cursor.execute("INSERT INTO employees (name, dob, position, salary, department_id) VALUES (%s, %s, %s, %s, %s)",
                       (name, dob, position, salary, department_id))
        db.commit()
        return redirect('/view')

    return render_template('add.html', departments=departments, domain=domain)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        position = request.form['position']
        salary = request.form['salary']
        department_id = request.form['department_id']

        cursor.execute("""
            UPDATE employees
            SET name=%s, dob=%s, position=%s, salary=%s, department_id=%s
            WHERE id=%s
        """, (name, dob, position, salary, department_id, id))
        db.commit()
        return redirect('/view')

    cursor.execute("SELECT * FROM employees WHERE id = %s", (id,))
    emp = cursor.fetchone()
    emp['dob'] = emp['dob'].strftime('%Y-%m-%d') if emp and 'dob' in emp else ''

    domain = session.get('domain')
    cursor.execute("SELECT d.* FROM departments d JOIN domains dom ON d.domain_id = dom.id WHERE dom.domain_name = %s", (domain,))
    departments = cursor.fetchall()
    return render_template('edit.html', employee=emp, departments=departments)

@app.route('/delete/<int:id>')
def delete(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM employees WHERE id = %s", (id,))
    db.commit()
    return redirect('/view')

if __name__ == '__main__':
    app.run(debug=True)
