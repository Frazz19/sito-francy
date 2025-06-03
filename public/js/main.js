// This file contains JavaScript code for handling form submissions, validating inputs, and displaying success messages. 
// It also manages the transition effects for the main page.

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('dedicationForm');
    const successMessage = document.getElementById('successMessage');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);

        fetch('/submit', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                form.style.display = 'none';
                successMessage.style.display = 'block';
            }
        });
    });
});