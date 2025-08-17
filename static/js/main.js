// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {

    // --- Feature 1: Smooth Scroll Animations ---
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.animate-on-scroll').forEach(element => {
        observer.observe(element);
    });


    // --- Feature 2: Job Recommendation Fetching ---
    const recommendForm = document.getElementById('recommendForm');
    if (recommendForm) {
        const jobContainer = document.getElementById('job-container');
        const skillsInput = document.getElementById('skillsInput');
        const submitButton = recommendForm.querySelector('button[type="submit"]');

        recommendForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            // Disable button and show loading spinner
            submitButton.disabled = true;
            jobContainer.innerHTML = '<div class="loading-spinner"></div>';

            try {
                const response = await fetch('/api/recommend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ skills: skillsInput.value })
                });

                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }

                const jobs = await response.json();
                displayJobs(jobs, jobContainer);

            } catch (error) {
                console.error('Fetch error:', error);
                jobContainer.innerHTML = '<p class="error">Could not fetch recommendations. Please try again.</p>';
            } finally {
                // Re-enable button
                submitButton.disabled = false;
            }
        });
    }
});

function displayJobs(jobs, container) {
    container.innerHTML = '';

    if (jobs.length === 0) {
        container.innerHTML = '<p class="placeholder-text">No matching jobs found. Try different skill keywords!</p>';
        return;
    }

    jobs.forEach(job => {
        const jobCard = document.createElement('div');
        jobCard.className = 'job-card animate-on-scroll'; // Add animation class
        jobCard.innerHTML = `
            <h3>${job.title}</h3>
            <p>${job.description.substring(0, 150)}...</p>
            <a href="#" class="button">Apply Now</a>
        `;
        container.appendChild(jobCard);
    });

    // Re-observe the new cards for the scroll animation
    const newObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
            }
        });
    }, { threshold: 0.1 });

    container.querySelectorAll('.animate-on-scroll').forEach(element => {
        newObserver.observe(element);
    });
}