# app.py (The New, Full-Featured Version)

import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import yaml
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. SETUP AND CONFIGURATION ---

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_change_this_asap'

try:
    db_config = yaml.safe_load(open('db.yaml'))
    app.config.update(db_config) # Update app config directly
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor' 
    mysql = MySQL(app)
    print("SUCCESS: db.yaml loaded and configured.")
except Exception as e:
    print(f"ERROR: Could not configure database. Details: {e}")
    exit()

# --- 2. RECOMMENDATION ENGINE (No changes needed here) ---

try:
    jobs_df = pd.read_csv('jobs.csv')
    jobs_df['description'] = jobs_df['description'].fillna('')
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(jobs_df['description'])
    print("SUCCESS: Recommendation model loaded.")
except Exception as e:
    print(f"ERROR: Could not load recommendation model. Details: {e}")
    jobs_df = None

def get_recommendations(user_skills_str):
    if jobs_df is None or not user_skills_str: return []
    try:
        user_vector = tfidf.transform([user_skills_str])
        sim_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()
        # Filter out jobs with very low similarity
        similar_jobs_indices = [i for i, score in enumerate(sim_scores) if score > 0.01]
        if not similar_jobs_indices: return []
        
        top_job_indices = sorted(similar_jobs_indices, key=lambda i: sim_scores[i], reverse=True)[:10]
        return jobs_df.iloc[top_job_indices].to_dict('records')
    except Exception as e:
        print(f"ERROR during recommendation: {e}")
        return []

# --- 3. AUTHENTICATION ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", [email])
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            flash('Logged in successfully!', 'success')
            if user['role'] == 'company':
                return redirect(url_for('company_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect email or password.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        hashed_password = generate_password_hash(password)
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", (name, email, hashed_password, role))
            mysql.connection.commit()
            cur.close()
            flash('You have successfully registered! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Account already exists or invalid data.', 'danger')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# --- 4. CORE STUDENT ROUTES ---

@app.route('/')
def home():
    if 'loggedin' in session:
        if session['role'] == 'company':
            return redirect(url_for('company_dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    # Fetch real-time stats
    cur.execute("SELECT COUNT(*) as count FROM applications WHERE user_id = %s", (session['id'],))
    total_apps = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) as count FROM applications WHERE user_id = %s AND status = 'Interviewing'", (session['id'],))
    interviews = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) as count FROM applications WHERE user_id = %s AND status = 'Offer'", (session['id'],))
    offers = cur.fetchone()['count']
    cur.close()
    
    stats = {'total': total_apps, 'interviews': interviews, 'offers': offers}
    
    return render_template('dashboard.html', user_name=session['name'], stats=stats)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'loggedin' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    user_id = session['id']
    if request.method == 'POST':
        # Update logic...
        name = request.form['name']
        email = request.form['email']
        skills = request.form['skills']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET name = %s, email = %s, skills = %s WHERE id = %s", (name, email, skills, user_id))
        mysql.connection.commit()
        cur.close()
        session['name'] = name # Update session name
        flash('Profile updated successfully!', 'success')

    cur = mysql.connection.cursor()
    cur.execute("SELECT name, email, skills FROM users WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    cur.close()
    
    return render_template('profile.html', **user_data)


@app.route('/recommend')
def recommend_page():
    if 'loggedin' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT skills FROM users WHERE id = %s", (session['id'],))
    user = cur.fetchone()
    user_skills = user['skills'] if user else ''
    
    # Get initial recommendations
    jobs = get_recommendations(user_skills)
    
    return render_template('recommend.html', user_skills=user_skills, jobs=jobs)


@app.route('/track')
def track():
    if 'loggedin' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    # Fetch real applications for the logged-in user
    cur.execute("""
        SELECT j.title, a.status, a.application_date 
        FROM applications a 
        JOIN jobs j ON a.job_id = j.id 
        WHERE a.user_id = %s 
        ORDER BY a.application_date DESC
    """, (session['id'],))
    applications = cur.fetchall()
    cur.close()
    
    return render_template('track.html', applications=applications)

@app.route('/apply/<int:job_id>')
def apply(job_id):
    if 'loggedin' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO applications (user_id, job_id) VALUES (%s, %s)", (session['id'], job_id))
        mysql.connection.commit()
        cur.close()
        flash('Successfully applied for the job!', 'success')
    except Exception as e:
        flash('You have already applied for this job.', 'warning')
    
    return redirect(url_for('track'))


# --- 5. COMPANY ROUTES ---

@app.route('/company/dashboard')
def company_dashboard():
    if 'loggedin' not in session or session['role'] != 'company':
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    # Get jobs posted by this company
    cur.execute("SELECT * FROM jobs WHERE company_id = %s ORDER BY created_at DESC", (session['id'],))
    jobs = cur.fetchall()
    cur.close()

    return render_template('company_dashboard.html', jobs=jobs, company_name=session['name'])

@app.route('/company/add_job', methods=['GET', 'POST'])
def add_job():
    if 'loggedin' not in session or session['role'] != 'company':
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO jobs (company_id, title, description) VALUES (%s, %s, %s)", (session['id'], title, description))
        mysql.connection.commit()
        cur.close()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('company_dashboard'))

    return render_template('add_job.html')

@app.route('/company/applicants/<int:job_id>')
def view_applicants(job_id):
    if 'loggedin' not in session or session['role'] != 'company':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    # Fetch applicants for a specific job posted by this company
    cur.execute("""
        SELECT u.name, u.email, u.skills, a.application_date
        FROM applications a
        JOIN users u ON a.user_id = u.id
        WHERE a.job_id = %s AND a.job_id IN (SELECT id FROM jobs WHERE company_id = %s)
    """, (job_id, session['id']))
    applicants = cur.fetchall()
    
    # Also get job title for the page header
    cur.execute("SELECT title FROM jobs WHERE id = %s", (job_id,))
    job = cur.fetchone()
    cur.close()

    return render_template('view_applicants.html', applicants=applicants, job=job)


# --- API Endpoint (No Changes) ---
@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    data = request.get_json()
    if not data or 'skills' not in data:
        return jsonify({'error': 'Skills data is missing'}), 400
    recommended_jobs = get_recommendations(data['skills'])
    return jsonify(recommended_jobs)

if __name__ == '__main__':
    app.run(debug=True)