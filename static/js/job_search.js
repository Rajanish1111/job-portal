document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('job-search-form');
    const jobListingsContainer = document.getElementById('job-listings-container');
    const resetFiltersButton = document.getElementById('reset-filters');

    const fetchJobs = async () => {
        const query = document.getElementById('search-query').value;
        const location = document.getElementById('filter-location').value;
        const min_salary = document.getElementById('filter-min-salary').value;
        const max_salary = document.getElementById('filter-max-salary').value;
        const experience = document.getElementById('filter-experience').value;

        const params = new URLSearchParams();
        if (query) params.append('query', query);
        if (location) params.append('location', location);
        if (min_salary) params.append('min_salary', min_salary);
        if (max_salary) params.append('max_salary', max_salary);
        if (experience) params.append('experience', experience);

        const response = await fetch(`/api/jobs_search?${params.toString()}`);
        const jobs = await response.json();
        renderJobs(jobs);
    };

    const renderJobs = (jobs) => {
        jobListingsContainer.innerHTML = ''; // Clear current jobs

        if (jobs.length === 0) {
            jobListingsContainer.innerHTML = '<p style="text-align: center; margin-top: 30px;">No jobs found matching your criteria. Try broadening your search!</p>';
            return;
        }

        jobs.forEach(job => {
            const jobCard = document.createElement('div');
            jobCard.classList.add('card', 'job-card', 'fade-in'); // Add fade-in class

            const truncatedDescription = job.description.length > 150 ? 
                                         job.description.substring(0, 150) + '...' : 
                                         job.description;

            jobCard.innerHTML = `
                <h3>${job.title}</h3>
                <p class="job-description">${truncatedDescription}</p>
                <div class="job-meta">
                    <span><strong>Location:</strong> ${job.location || 'N/A'}</span>
                    <span><strong>Salary:</strong> ${job.salary || 'N/A'}</span>
                    <span><strong>Experience:</strong> ${job.experience || 'N/A'}</span>
                </div>
                <p class="job-skills"><strong>Skills:</strong> ${job.skills || 'N/A'}</p>
                <a href="/apply_job/${job.id}" class="btn apply-btn">Apply Now</a>
            `;
            jobListingsContainer.appendChild(jobCard);
        });
    };

    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        fetchJobs();
    });

    resetFiltersButton.addEventListener('click', () => {
        searchForm.reset(); // Clear all form fields
        fetchJobs(); // Fetch all jobs again
    });

    // Initial load of jobs when the page loads
    fetchJobs();
});