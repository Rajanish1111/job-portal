-- schema.sql (The New Version)

-- Drop tables in reverse order of dependency to avoid errors
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS users;

-- Create a new users table with password and role fields
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, -- Will store hashed passwords
    name VARCHAR(100) NOT NULL,      -- Can be a person's name or a company's name
    role ENUM('student', 'company') NOT NULL,
    skills TEXT, -- Primarily for students
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a new jobs table linked to the company that posted it
CREATE TABLE jobs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES users(id)
);

-- Create the applications table to link students to jobs
CREATE TABLE applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL, -- The student who applied
    job_id INT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Applied',
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_hash VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    UNIQUE(user_id, job_id) -- A user can only apply to the same job once
);