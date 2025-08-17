# recommendation_model.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- 1.  Load Data from a CSV or Database (Placeholder) ---
def load_data():
    """Loads the job data.  Replace this with a database query."""
    try:
        # Sample DataFrame - replace with your database
        # Option 1: From a CSV file (easy for testing).  Replace with your database.
        jobs_df = pd.read_csv('jobs.csv')  # Create a 'jobs.csv' file.

    except FileNotFoundError:
        print("Warning: jobs.csv not found. Using dummy data.")
        jobs_df = pd.DataFrame({
            'title': ['Software Engineer', 'Data Scientist', 'Project Manager', 'Web Developer'],
            'description': [
                'Develop software applications.',
                'Analyze data and build models.',
                'Manage projects and teams.',
                'Create websites and web applications.'
            ],
            'skills': ['Python, Java, Agile', 'Python, R, Machine Learning', 'Project Management, Leadership', 'HTML, CSS, JavaScript']
        })

    # --- 2. Text Vectorization  ---
    #  Prepare the text data for the model.
    vectorizer = TfidfVectorizer()
    jobs_df['description'] = jobs_df['description'].fillna('').astype(str) # Handle missing values
    tfidf_matrix = vectorizer.fit_transform(jobs_df['description']) # Fit on job descriptions

    return jobs_df, vectorizer, tfidf_matrix

# --- 3. Recommend Jobs Function  ---
def recommend_jobs(user_skills, jobs_df, vectorizer, tfidf_matrix, top_n=5):
    """Recommends jobs based on user skills.
    Replace the dummy logic below with your ML model's code."""
    try:
        # --- 4. Vectorize User Skills ---
        skills_vector = vectorizer.transform([user_skills])
        # --- 5. Calculate Cosine Similarity ---
        cosine_similarities = cosine_similarity(skills_vector, tfidf_matrix).flatten()

        # --- 6. Get Top N Job Indices ---
        job_indices = cosine_similarities.argsort()[:-top_n-1:-1] # Get top N indices

        # --- 7. Return Recommended Jobs  ---
        recommended_jobs = jobs_df.iloc[job_indices].to_dict(orient='records') # Convert to list of dicts
        return recommended_jobs
    except Exception as e:
        print(f"Recommendation error: {e}")
        return [] # Return empty list in case of errors