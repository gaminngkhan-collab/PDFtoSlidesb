document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('file');
    const uploadText = uploadBtn.querySelector('.upload-text');
    const uploadLoading = uploadBtn.querySelector('.upload-loading');

    // File size validation
    function validateFileSize(file) {
        const maxSize = 20 * 1024 * 1024; // 20MB in bytes
        return file.size <= maxSize;
    }

    // File type validation
    function validateFileType(file) {
        return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    }

    // Show loading state
    function showLoadingState() {
        uploadBtn.disabled = true;
        uploadText.classList.add('d-none');
        uploadLoading.classList.remove('d-none');
    }

    // Hide loading state
    function hideLoadingState() {
        uploadBtn.disabled = false;
        uploadText.classList.remove('d-none');
        uploadLoading.classList.add('d-none');
    }

    // Show error message
    function showError(message) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create new error alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
            <i data-feather="alert-circle" class="me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert alert before the upload form
        const container = document.querySelector('.container .col-lg-8');
        const flashContainer = container.querySelector('.alert') || container.children[1];
        container.insertBefore(alertDiv, flashContainer);
        
        // Re-initialize feather icons for the new alert
        feather.replace();
    }

    // File input change event
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Validate file type
            if (!validateFileType(file)) {
                showError('Please select a valid PDF file.');
                fileInput.value = '';
                return;
            }

            // Validate file size
            if (!validateFileSize(file)) {
                showError('File size must be less than 20MB.');
                fileInput.value = '';
                return;
            }

            // Remove any existing error messages
            const existingAlerts = document.querySelectorAll('.alert-danger');
            existingAlerts.forEach(alert => alert.remove());
        }
    });

    // Form submit event
    uploadForm.addEventListener('submit', function(e) {
        const file = fileInput.files[0];
        
        if (!file) {
            e.preventDefault();
            showError('Please select a PDF file to convert.');
            return;
        }

        // Validate file type
        if (!validateFileType(file)) {
            e.preventDefault();
            showError('Please select a valid PDF file.');
            return;
        }

        // Validate file size
        if (!validateFileSize(file)) {
            e.preventDefault();
            showError('File size must be less than 20MB.');
            return;
        }

        // Show loading state
        showLoadingState();

        // Optional: Add timeout to hide loading state if something goes wrong
        setTimeout(function() {
            hideLoadingState();
        }, 300000); // 5 minutes timeout
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            setTimeout(() => {
                try {
                    bsAlert.close();
                } catch (e) {
                    // Alert might already be closed
                }
            }, 5000);
        });
    }, 1000);
});