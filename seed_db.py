import sqlite3
from werkzeug.security import generate_password_hash

def seed_db():
    conn = sqlite3.connect('job_portal.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recruiter_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            skills TEXT NOT NULL,
            salary TEXT,
            location TEXT,
            experience TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recruiter_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            candidate_name TEXT NOT NULL,
            candidate_email TEXT NOT NULL,
            cv_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (candidate_id) REFERENCES users(id)
        )
    ''')

    # Add example users (recruiter and candidate)
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                   ('recruiter1', generate_password_hash('password123'), 'recruiter'))
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                   ('candidate1', generate_password_hash('password123'), 'candidate'))
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                   ('recruiter2', generate_password_hash('securepass'), 'recruiter'))
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                   ('candidate2', generate_password_hash('mypassword'), 'candidate'))

    # Get recruiter IDs for job posting
    cursor.execute("SELECT id FROM users WHERE username='recruiter1'")
    recruiter1_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM users WHERE username='recruiter2'")
    recruiter2_id = cursor.fetchone()[0]

    # Add 25+ jobs (ECE & CSE focus)
    jobs_data = [
        # ECE Jobs
        (recruiter1_id, 'Embedded Software Engineer', 'Develop firmware for IoT devices. Experience with C/C++ and RTOS.', 'C, C++, RTOS, Microcontrollers, IoT', '80k-120k USD', 'Bangalore, India', '3-5 Years'),
        (recruiter1_id, 'FPGA Design Engineer', 'Design and verify FPGA logic for high-speed communication systems.', 'VHDL, Verilog, FPGA, RTL, Xilinx, Altera', '90k-130k USD', 'Hyderabad, India', '5-8 Years'),
        (recruiter1_id, 'VLSI Design Engineer', 'Work on ASIC design and verification flows.', 'Verilog, SystemVerilog, UVM, ASIC, Physical Design', '100k-150k USD', 'Pune, India', '6-10 Years'),
        (recruiter1_id, 'RF Engineer', 'Design and test RF circuits for wireless communication.', 'RF, Circuit Design, Antenna, MATLAB, Simulink', '75k-110k USD', 'Chennai, India', '4-7 Years'),
        (recruiter1_id, 'Power Electronics Engineer', 'Develop power conversion systems and motor control.', 'Power Electronics, DC-DC, AC-DC, Motor Control, Altium', '85k-125k USD', 'Mumbai, India', '3-6 Years'),
        (recruiter1_id, 'Hardware Design Engineer', 'Develop schematics and layouts for complex PCBs.', 'PCB Design, Altium, KiCAD, Analog, Digital', '80k-120k USD', 'Delhi, India', '4-6 Years'),
        (recruiter1_id, 'Signal Processing Engineer', 'Implement algorithms for real-time signal processing.', 'DSP, MATLAB, Python, C++, Algorithm Development', '90k-135k USD', 'Bangalore, India', '5-8 Years'),
        (recruiter1_id, 'Firmware Engineer (Automotive)', 'Develop and test automotive embedded software.', 'AUTOSAR, CAN, LIN, C, Embedded Systems', '95k-140k USD', 'Hyderabad, India', '5-9 Years'),
        (recruiter1_id, 'IoT Solutions Architect', 'Design end-to-end IoT solutions from sensor to cloud.', 'IoT, Cloud, AWS IoT, Azure IoT, MQTT, Edge Computing', '110k-160k USD', 'Pune, India', '7-12 Years'),
        (recruiter1_id, 'Mixed-Signal IC Design Engineer', 'Design and verify mixed-signal integrated circuits.', 'CMOS, Analog, Digital, Cadence, Spectre', '105k-155k USD', 'Bangalore, India', '6-10 Years'),
        (recruiter1_id, 'Optical Engineer', 'Develop and test optical systems for various applications.', 'Optics, Lasers, Photonics, ZEMAX, MATLAB', '80k-120k USD', 'Chennai, India', '4-7 Years'),
        (recruiter1_id, 'EMI/EMC Engineer', 'Perform EMI/EMC testing and design for compliance.', 'EMI, EMC, FCC, CE, Anechoic Chamber', '70k-100k USD', 'Mumbai, India', '3-5 Years'),

        # CSE Jobs
        (recruiter2_id, 'AI/ML Engineer', 'Develop and deploy machine learning models for various applications.', 'Python, TensorFlow, PyTorch, Scikit-learn, AWS SageMaker', '100k-150k USD', 'Bangalore, India', '4-7 Years'),
        (recruiter2_id, 'Software Development Engineer', 'Build scalable backend services using Python/Flask.', 'Python, Flask, REST API, PostgreSQL, Docker', '90k-130k USD', 'Hyderabad, India', '3-6 Years'),
        (recruiter2_id, 'Cloud Engineer (AWS)', 'Design and implement cloud infrastructure on AWS.', 'AWS, EC2, S3, Lambda, CloudFormation, Terraform', '110k-160k USD', 'Pune, India', '5-8 Years'),
        (recruiter2_id, 'Frontend Developer (React)', 'Develop interactive user interfaces using React and Redux.', 'React, Redux, JavaScript, HTML, CSS, SASS', '85k-125k USD', 'Chennai, India', '3-5 Years'),
        (recruiter2_id, 'DevOps Engineer', 'Automate CI/CD pipelines and manage infrastructure.', 'CI/CD, Jenkins, GitLab CI, Kubernetes, Ansible, Linux', '95k-140k USD', 'Mumbai, India', '4-7 Years'),
        (recruiter2_id, 'Full Stack Developer', 'Work on both frontend and backend development with modern frameworks.', 'Python, Django, React, PostgreSQL, Docker, AWS', '100k-150k USD', 'Delhi, India', '5-8 Years'),
        (recruiter2_id, 'Data Scientist', 'Analyze large datasets, build predictive models, and visualize results.', 'Python, R, SQL, Pandas, NumPy, Machine Learning, Tableau', '105k-155k USD', 'Bangalore, India', '5-9 Years'),
        (recruiter2_id, 'Cybersecurity Engineer', 'Protect systems and data from cyber threats, implement security measures.', 'Security, Penetration Testing, SIEM, Firewalls, Network Security', '90k-130k USD', 'Hyderabad, India', '4-6 Years'),
        (recruiter2_id, 'Mobile App Developer (Android)', 'Develop native Android applications.', 'Java, Kotlin, Android Studio, REST APIs, UI/UX', '80k-120k USD', 'Pune, India', '3-5 Years'),
        (recruiter2_id, 'Game Developer', 'Develop games using Unity or Unreal Engine.', 'C#, Unity, C++, Unreal Engine, Game Design', '75k-110k USD', 'Bangalore, India', '3-6 Years'),
        (recruiter2_id, 'Database Administrator', 'Manage and optimize relational databases.', 'SQL, MySQL, PostgreSQL, Oracle, Database Optimization', '85k-125k USD', 'Chennai, India', '4-7 Years'),
        (recruiter2_id, 'UX/UI Designer', 'Design intuitive and engaging user experiences.', 'Figma, Sketch, Adobe XD, User Research, Wireframing', '70k-100k USD', 'Mumbai, India', '3-5 Years'),
        (recruiter2_id, 'Backend Engineer (Go)', 'Build high-performance backend services using Go.', 'Go, Microservices, Docker, Kubernetes, gRPC', '110k-160k USD', 'Delhi, India', '5-8 Years'),
    ]

    cursor.executemany("INSERT INTO jobs (recruiter_id, title, description, skills, salary, location, experience) VALUES (?, ?, ?, ?, ?, ?, ?)", jobs_data)

    conn.commit()
    conn.close()
    print("Database seeded successfully with users and jobs.")

if __name__ == '__main__':
    seed_db()