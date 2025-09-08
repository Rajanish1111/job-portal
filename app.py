import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

# ✅ Use environment variable for secret key (better for deployment)
app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key")

# Database configuration
DATABASE = 'job_portal.db'


# ---------------------- Helper Functions ----------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session:
                flash("You need to login first.", "danger")
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash("You are not authorized to access this page.", "danger")
                return redirect(url_for('dashboard'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


# ---------------------- Routes ----------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                         (username, hashed_password, role))
            conn.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists. Please choose another.", "danger")
        finally:
            conn.close()

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password", "danger")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required()
def dashboard():
    if session['role'] == 'recruiter':
        return redirect(url_for('recruiter_dashboard'))
    else:
        return redirect(url_for('candidate_dashboard'))


# ---------------------- Recruiter Routes ----------------------

@app.route('/recruiter/dashboard')
@login_required(role='recruiter')
def recruiter_dashboard():
    conn = get_db_connection()
    jobs = conn.execute("SELECT * FROM jobs WHERE recruiter_id = ?", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('recruiter_dashboard.html', jobs=jobs)


@app.route('/recruiter/post_job', methods=['GET', 'POST'])
@login_required(role='recruiter')
def post_job():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        conn = get_db_connection()
        conn.execute("INSERT INTO jobs (title, description, recruiter_id) VALUES (?, ?, ?)",
                     (title, description, session['user_id']))
        conn.commit()
        conn.close()

        flash("Job posted successfully!", "success")
        return redirect(url_for('recruiter_dashboard'))

    return render_template('post_job.html')


# ---------------------- Candidate Routes ----------------------

@app.route('/candidate/dashboard')
@login_required(role='candidate')
def candidate_dashboard():
    conn = get_db_connection()
    jobs = conn.execute("SELECT * FROM jobs").fetchall()
    conn.close()
    return render_template('candidate_dashboard.html', jobs=jobs)


@app.route('/apply_job/<int:job_id>', methods=['POST'])
@login_required(role='candidate')
def apply_job(job_id):
    conn = get_db_connection()
    conn.execute("INSERT INTO applications (job_id, candidate_id) VALUES (?, ?)",
                 (job_id, session['user_id']))
    conn.commit()
    conn.close()
    flash("Applied to job successfully!", "success")
    return redirect(url_for('candidate_dashboard'))


# ---------------------- API ----------------------

@app.route('/api/jobs_search')
def jobs_search():
    query = request.args.get('q', '')

    conn = get_db_connection()
    jobs = conn.execute("SELECT * FROM jobs WHERE title LIKE ?", ('%' + query + '%',)).fetchall()
    conn.close()

    jobs_list = [dict(job) for job in jobs]
    return jsonify(jobs_list)


# ---------------------- Run ----------------------

if __name__ == '__main__':
    # ✅ host=0.0.0.0 for deployment, PORT from env or default 5000
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
