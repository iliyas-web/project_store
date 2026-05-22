from flask import Flask, render_template, request, redirect, session
import mysql.connector
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.secret_key = "secret123"

# =========================
# IMAGE UPLOAD FOLDER
# =========================

UPLOAD_FOLDER = 'static/images'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# =========================
# MYSQL CONNECTION
# =========================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="project_store"
)

cursor = db.cursor(dictionary=True)

# =========================
# HOME PAGE + SEARCH
# =========================

@app.route('/')
def home():

    search = request.args.get('search')
    category = request.args.get('category')

    sql = "SELECT * FROM projects WHERE 1=1"
    values = []

    if search:

        sql += """
        AND (
            title LIKE %s
            OR tech_stack LIKE %s
        )
        """

        values.append(f"%{search}%")
        values.append(f"%{search}%")

    if category and category != "All":

        sql += " AND category=%s"

        values.append(category)

    cursor.execute(sql, tuple(values))

    projects = cursor.fetchall()

    return render_template(
        'index.html',
        projects=projects
    )

# =========================
# PROJECT DETAILS
# =========================

@app.route('/project/<int:id>')
def project_details(id):

    cursor.execute(
        "SELECT * FROM projects WHERE id=%s",
        (id,)
    )

    project = cursor.fetchone()

    return render_template(
        'details.html',
        project=project
    )

# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":

            session['admin'] = True

            return redirect('/admin')

    return render_template('login.html')

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.pop('admin', None)

    return redirect('/login')

# =========================
# ADMIN PANEL
# =========================

@app.route('/admin', methods=['GET', 'POST'])
def admin():

    if 'admin' not in session:
        return redirect('/login')

    # ADD PROJECT
    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        tech_stack = request.form['tech_stack']
        price = request.form['price']

        image = request.files['image']

        filename = secure_filename(image.filename)

        image_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )

        image.save(image_path)

        sql = """
        INSERT INTO projects(
            title,
            description,
            category,
            tech_stack,
            price,
            image
        )
        VALUES(%s,%s,%s,%s,%s,%s)
        """

        values = (
            title,
            description,
            category,
            tech_stack,
            price,
            image_path
        )

        cursor.execute(sql, values)
        db.commit()

        return redirect('/admin')

    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()

    return render_template(
        'admin.html',
        projects=projects
    )

# =========================
# DELETE PROJECT
# =========================

@app.route('/delete/<int:id>')
def delete_project(id):

    if 'admin' not in session:
        return redirect('/login')

    cursor.execute(
        "DELETE FROM projects WHERE id=%s",
        (id,)
    )

    db.commit()

    return redirect('/admin')

# =========================
# EDIT PROJECT
# =========================

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_project(id):

    if 'admin' not in session:
        return redirect('/login')

    cursor.execute(
        "SELECT * FROM projects WHERE id=%s",
        (id,)
    )

    project = cursor.fetchone()

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        tech_stack = request.form['tech_stack']
        price = request.form['price']

        image = request.files['image']

        filename = secure_filename(image.filename)

        image_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )

        image.save(image_path)

        sql = """
        UPDATE projects
        SET
            title=%s,
            description=%s,
            category=%s,
            tech_stack=%s,
            price=%s,
            image=%s
        WHERE id=%s
        """

        values = (
            title,
            description,
            category,
            tech_stack,
            price,
            image_path,
            id
        )

        cursor.execute(sql, values)
        db.commit()

        return redirect('/admin')

    return render_template(
        'edit.html',
        project=project
    )

# =========================
# RUN APP
# =========================

if __name__ == '__main__':
    app.run(debug=True)