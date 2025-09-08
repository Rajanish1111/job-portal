document.addEventListener('DOMContentLoaded', () => {
    // Fade out flash messages after a few seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.height = '0';
            message.style.padding = '0';
            message.style.margin = '0';
            message.style.border = 'none';
            message.style.transition = 'opacity 0.5s ease-out, height 0.5s ease-out 0.5s, padding 0.5s ease-out 0.5s, margin 0.5s ease-out 0.5s';
        }, 5000); // 5 seconds
    });

    // Simple hover effect for job cards (CSS handles most of it)
    const jobCards = document.querySelectorAll('.job-card');
    jobCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            // Add a class for more complex JS-driven hover effects if needed
            // For now, CSS handles transform and shadow
        });
        card.addEventListener('mouseleave', () => {
            // Remove class
        });
    });

    // You can add more general interactive elements here if needed
});