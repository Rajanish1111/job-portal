import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key")
#app.secret_key = os.urandom(24) # Used for session management

DATABASE = 'job_portal.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # This allows us to access columns by name
    return conn

# --- Authentication Routes ---

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                         (username, hashed_password, role))
            conn.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'danger')
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
            flash(f'Logged in as {user["username"]} ({user["role"]})', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# --- Helper for Login Required ---
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

import functools # Add this import at the top

# --- Main Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/jobs')
@login_required
def job_listings():
    conn = get_db_connection()
    jobs = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template('job_listings.html', jobs=jobs)

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    if session['role'] == 'recruiter':
        user_jobs = conn.execute("SELECT * FROM jobs WHERE recruiter_id = ? ORDER BY created_at DESC",
                                 (session['user_id'],)).fetchall()
        return render_template('recruiter_dashboard.html', jobs=user_jobs)
    elif session['role'] == 'candidate':
        applied_jobs = conn.execute("""
            SELECT j.*, a.created_at AS application_date
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.candidate_id = ?
            ORDER BY a.created_at DESC
        """, (session['user_id'],)).fetchall()
        return render_template('candidate_dashboard.html', applied_jobs=applied_jobs)
    conn.close()
    return redirect(url_for('index')) # Should not happen

# --- Recruiter Features ---
@app.route('/post_job', methods=['GET', 'POST'])
@login_required
def post_job():
    if session['role'] != 'recruiter':
        flash('Only recruiters can post jobs.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        skills = request.form['skills']
        salary = request.form['salary']
        location = request.form['location']
        experience = request.form['experience']

        conn = get_db_connection()
        conn.execute("INSERT INTO jobs (recruiter_id, title, description, skills, salary, location, experience) VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (session['user_id'], title, description, skills, salary, location, experience))
        conn.commit()
        conn.close()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('post_job.html')

@app.route('/view_applications/<int:job_id>')
@login_required
def view_applications(job_id):
    if session['role'] != 'recruiter':
        flash('Only recruiters can view applications.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    job = conn.execute("SELECT * FROM jobs WHERE id = ? AND recruiter_id = ?",
                       (job_id, session['user_id'])).fetchone()
    if not job:
        flash('Job not found or you do not have permission to view it.', 'danger')
        conn.close()
        return redirect(url_for('dashboard'))

    applications = conn.execute("SELECT * FROM applications WHERE job_id = ? ORDER BY created_at DESC",
                                (job_id,)).fetchall()
    conn.close()
    return render_template('view_applications.html', job=job, applications=applications)

# --- Candidate Features ---
@app.route('/apply_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    if session['role'] != 'candidate':
        flash('Only candidates can apply for jobs.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not job:
        flash('Job not found.', 'danger')
        conn.close()
        return redirect(url_for('job_listings'))

    # Check if candidate has already applied
    existing_application = conn.execute(
        "SELECT * FROM applications WHERE job_id = ? AND candidate_id = ?",
        (job_id, session['user_id'])
    ).fetchone()
    if existing_application:
        flash('You have already applied for this job.', 'info')
        conn.close()
        return redirect(url_for('job_listings'))

    if request.method == 'POST':
        candidate_name = request.form['candidate_name']
        candidate_email = request.form['candidate_email']
        cv_message = request.form['cv_message']

        conn.execute(
            "INSERT INTO applications (job_id, candidate_id, candidate_name, candidate_email, cv_message) VALUES (?, ?, ?, ?, ?)",
            (job_id, session['user_id'], candidate_name, candidate_email, cv_message)
        )
        conn.commit()
        conn.close()

        flash('Application submitted successfully!', 'success')
        return redirect(url_for('dashboard'))   # ✅ Redirects to main dashboard

    conn.close()
    return render_template('apply_job.html', job=job)



# --- Search and Filter (API Endpoint for AJAX) ---
@app.route('/api/jobs_search', methods=['GET'])
def jobs_search():
    query = request.args.get('query', '')
    location_filter = request.args.get('location', '')
    min_salary = request.args.get('min_salary', type=int)
    max_salary = request.args.get('max_salary', type=int)
    experience_filter = request.args.get('experience', '')

    conn = get_db_connection()
    sql_query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if query:
        search_term = f"%{query}%"
        sql_query += " AND (title LIKE ? OR skills LIKE ? OR description LIKE ?)"
        params.extend([search_term, search_term, search_term])

    if location_filter:
        sql_query += " AND location LIKE ?"
        params.append(f"%{location_filter}%")

    if experience_filter:
        sql_query += " AND experience LIKE ?"
        params.append(f"%{experience_filter}%")

    # Salary filtering - This is a bit simplistic as salary is TEXT.
    # For a robust solution, salary should be stored as numeric range (min_salary, max_salary)
    # For now, we'll do a simple text-based check, which might not be perfect.
    if min_salary:
        # This will try to match if the min_salary is mentioned in the text
        # or if the text indicates a higher value. This is a very crude approach.
        # A proper solution needs salary to be numeric in DB.
        sql_query += " AND (salary LIKE ? OR CAST(SUBSTR(salary, 1, INSTR(salary, 'k')-1) AS INTEGER) >= ?)"
        params.append(f"%{min_salary}%") # Tries to match '80k' for 80
        params.append(min_salary) # For salaries like '100k-150k' if we parse the first part.
                                # This casting assumes 'XXk' format. More complex for 'XX-YYk'

    if max_salary:
        # Similarly crude for max_salary
        sql_query += " AND (salary LIKE ? OR CAST(SUBSTR(salary, INSTR(salary, '-')+1, INSTR(salary, 'k') - INSTR(salary, '-')-1) AS INTEGER) <= ?)"
        params.append(f"%{max_salary}%") # Tries to match '120k' for 120
        params.append(max_salary) # Assumes 'XX-YYk' format for parsing the upper bound.

    jobs = conn.execute(sql_query + " ORDER BY created_at DESC", params).fetchall()
    conn.close()

    # Convert Row objects to dictionaries for JSON serialization
    jobs_dict = [dict(job) for job in jobs]
    return jsonify(jobs_dict)


if __name__ == '__main__':
    # Make sure to run seed_db.py first!
    app.run(debug=True)
