from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Unnati@123'
app.config['MYSQL_DB'] = 'employee_db'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'role' in request.form:
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM employees WHERE username = %s AND password = %s AND role = %s', (username, password, role))
        account = cursor.fetchone()
        if account:
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'employee':
                return redirect(url_for('employee_dashboard'))
        else:
            msg = 'Incorrect username / password or role!'
    return render_template('login.html', msg=msg)


@app.route('/logout', methods=['POST'])
def logout():
    return redirect(url_for('login'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        email = request.form.get('email')
        mobile_number = request.form.get('mobile_number')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM employees WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password:
            msg = 'Please fill out the form!'
        else:
            try:
                cursor.execute('INSERT INTO employees (username, password, role, email, mobile_number) VALUES (%s, %s, %s, %s, %s)', 
                               (username, password, role, email, mobile_number))
                mysql.connection.commit()
                msg = 'You have successfully registered!'
            except Exception as e:
                mysql.connection.rollback()
                print(f"Error: {e}")
                msg = 'An error occurred. Please try again later.'
    
    return render_template('register.html', msg=msg)

@app.route('/delete_employee/<int:id>', methods=['POST'])
def delete_employee(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # Delete the employee record from the database
        cursor.execute('DELETE FROM employees WHERE id = %s', (id,))
        mysql.connection.commit()
        msg = 'Employee has been deleted successfully!'
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error: {e}")
        msg = 'An error occurred while deleting the employee. Please try again later.'
    
    # Redirect back to the admin dashboard with a success or error message
    return redirect(url_for('admin_dashboard'))


@app.route('/admin_dashboard')
def admin_dashboard():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT id, username, role, email, mobile_number FROM employees')
    employees = cursor.fetchall()
    return render_template('admin_dashboard.html', employees=employees)


@app.route('/employee_dashboard')
def employee_dashboard():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT id, username, role, email, mobile_number FROM employees')
    employees = cursor.fetchall()
    return render_template('employee_dashboard.html', employees=employees)

@app.route('/edit_employee/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        password = request.form['password']
        
        # Check if any field has been updated
        cursor.execute('SELECT * FROM employees WHERE id = %s', (id,))
        employee = cursor.fetchone()
        
        # Construct the update query
        update_query = 'UPDATE employees SET username = %s, role = %s, email = %s, mobile_number = %s'
        params = [username, role, email, mobile_number]
        
        if password:
            update_query += ', password = %s'
            params.append(password)
        
        update_query += ' WHERE id = %s'
        params.append(id)
        
        cursor.execute(update_query, tuple(params))
        mysql.connection.commit()
        
        msg = 'Employee updated successfully!' if cursor.rowcount > 0 else 'No changes made.'
        return redirect(url_for('edit_employee', id=id, msg=msg))
    
    else:
        cursor.execute('SELECT * FROM employees WHERE id = %s', (id,))
        employee = cursor.fetchone()
        return render_template('edit_employee.html', employee=employee, msg=request.args.get('msg', ''))
    
if __name__ == '__main__':
    app.run(debug=True)
