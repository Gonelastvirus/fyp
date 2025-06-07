/**
 * Main JavaScript file for FYP Marketplace
 * Handles client-side interactions and enhancements
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Main initialization function
 */
function initializeApp() {
    initializeTooltips();
    initializeFormValidation();
    initializeSearchFilters();
    initializeMilestoneTracking();
    initializeNotifications();
    initializeProgressBars();
    initializeTableSorting();
    initializeAutoSave();
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Enhanced form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
        
        // Form submission validation
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
                event.stopPropagation();
            }
        });
    });
}

/**
 * Validate individual form field
 */
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required.';
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address.';
        }
    }
    
    // Budget validation
    if (fieldName === 'budget_min' || fieldName === 'budget_max') {
        const budget = parseFloat(value);
        if (value && (isNaN(budget) || budget < 50)) {
            isValid = false;
            errorMessage = 'Budget must be at least $50.';
        }
        
        // Cross-field validation for budget range
        if (fieldName === 'budget_max') {
            const minField = document.querySelector('[name="budget_min"]');
            if (minField && minField.value) {
                const minBudget = parseFloat(minField.value);
                if (budget < minBudget) {
                    isValid = false;
                    errorMessage = 'Maximum budget must be greater than minimum budget.';
                }
            }
        }
    }
    
    // Phone validation
    if (fieldName === 'phone' && value) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        if (!phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''))) {
            isValid = false;
            errorMessage = 'Please enter a valid phone number.';
        }
    }
    
    // Password strength validation
    if (fieldName === 'password' && value) {
        if (value.length < 6) {
            isValid = false;
            errorMessage = 'Password must be at least 6 characters long.';
        }
    }
    
    showFieldValidation(field, isValid, errorMessage);
    return isValid;
}

/**
 * Validate entire form
 */
function validateForm(form) {
    const fields = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isFormValid = true;
    
    fields.forEach(field => {
        if (!validateField(field)) {
            isFormValid = false;
        }
    });
    
    return isFormValid;
}

/**
 * Show field validation state
 */
function showFieldValidation(field, isValid, errorMessage) {
    const fieldContainer = field.closest('.mb-3') || field.closest('.col');
    const existingError = fieldContainer.querySelector('.validation-error');
    
    // Remove existing error
    if (existingError) {
        existingError.remove();
    }
    
    // Remove validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    if (isValid) {
        field.classList.add('is-valid');
    } else {
        field.classList.add('is-invalid');
        
        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'validation-error text-danger small mt-1';
        errorDiv.textContent = errorMessage;
        fieldContainer.appendChild(errorDiv);
    }
}

/**
 * Clear field error
 */
function clearFieldError(field) {
    const fieldContainer = field.closest('.mb-3') || field.closest('.col');
    const existingError = fieldContainer.querySelector('.validation-error');
    
    if (existingError) {
        existingError.remove();
    }
    
    field.classList.remove('is-invalid');
}

/**
 * Initialize search and filter functionality
 */
function initializeSearchFilters() {
    const searchInput = document.querySelector('input[name="search"]');
    const categorySelect = document.querySelector('select[name="category"]');
    
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterProjects();
            }, 300);
        });
    }
    
    if (categorySelect) {
        categorySelect.addEventListener('change', filterProjects);
    }
}

/**
 * Filter projects based on search criteria
 */
function filterProjects() {
    const searchValue = document.querySelector('input[name="search"]')?.value.toLowerCase() || '';
    const categoryValue = document.querySelector('select[name="category"]')?.value || '';
    const projectCards = document.querySelectorAll('.project-card');
    
    projectCards.forEach(card => {
        const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
        const description = card.querySelector('.card-text')?.textContent.toLowerCase() || '';
        const category = card.querySelector('.badge')?.textContent.toLowerCase() || '';
        
        const matchesSearch = !searchValue || title.includes(searchValue) || description.includes(searchValue);
        const matchesCategory = !categoryValue || category.includes(categoryValue.replace('_', ' '));
        
        if (matchesSearch && matchesCategory) {
            card.style.display = 'block';
            card.style.animation = 'fadeInUp 0.3s ease';
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show/hide empty state
    const visibleCards = Array.from(projectCards).filter(card => card.style.display !== 'none');
    const emptyState = document.querySelector('.empty-state');
    
    if (visibleCards.length === 0 && !emptyState) {
        showEmptyState();
    } else if (visibleCards.length > 0 && emptyState) {
        emptyState.remove();
    }
}

/**
 * Show empty state for search results
 */
function showEmptyState() {
    const container = document.querySelector('.row');
    if (container) {
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'col-12 empty-state';
        emptyDiv.innerHTML = `
            <i class="fas fa-search fa-5x text-muted mb-3"></i>
            <h4>No projects found</h4>
            <p class="text-muted">Try adjusting your search criteria or browse all projects.</p>
        `;
        container.appendChild(emptyDiv);
    }
}

/**
 * Initialize milestone tracking functionality
 */
function initializeMilestoneTracking() {
    const milestoneCards = document.querySelectorAll('.milestone-card');
    
    milestoneCards.forEach(card => {
        const status = card.dataset.status;
        
        // Add visual indicators based on status
        if (status === 'completed') {
            card.classList.add('milestone-completed');
        } else if (status === 'in_progress') {
            card.classList.add('milestone-progress');
        }
    });
    
    // Auto-update progress bars
    updateProgressBars();
}

/**
 * Initialize notification system
 */
function initializeNotifications() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Check for new notifications (if WebSocket or polling is implemented)
    checkForNotifications();
}

/**
 * Check for new notifications
 */
function checkForNotifications() {
    // This would typically connect to a WebSocket or poll an API
    // For now, we'll just implement a placeholder
    
    // Example: Poll for new proposals every 30 seconds
    setInterval(() => {
        if (window.location.pathname.includes('/dashboard')) {
            // Could fetch notification count and update UI
            updateNotificationBadge();
        }
    }, 30000);
}

/**
 * Update notification badge
 */
function updateNotificationBadge() {
    // Placeholder for notification badge updates
    // This would typically fetch from an API endpoint
}

/**
 * Initialize and update progress bars
 */
function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.width = targetWidth;
        }, 100);
    });
}

/**
 * Update progress bars with animation
 */
function updateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar[data-progress]');
    
    progressBars.forEach(bar => {
        const progress = bar.dataset.progress;
        animateProgressBar(bar, progress);
    });
}

/**
 * Animate progress bar to target value
 */
function animateProgressBar(bar, targetProgress) {
    let currentProgress = 0;
    const increment = targetProgress / 50; // 50 steps
    
    const timer = setInterval(() => {
        currentProgress += increment;
        if (currentProgress >= targetProgress) {
            currentProgress = targetProgress;
            clearInterval(timer);
        }
        
        bar.style.width = currentProgress + '%';
        bar.setAttribute('aria-valuenow', currentProgress);
        bar.textContent = Math.round(currentProgress) + '%';
    }, 20);
}

/**
 * Initialize table sorting
 */
function initializeTableSorting() {
    const tables = document.querySelectorAll('table.sortable');
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => sortTable(table, header));
        });
    });
}

/**
 * Sort table by column
 */
function sortTable(table, header) {
    const column = header.dataset.sort;
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const isAscending = header.classList.contains('sort-asc');
    
    // Remove sort classes from all headers
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Add appropriate sort class
    header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.querySelector(`td:nth-child(${getColumnIndex(header) + 1})`).textContent.trim();
        const bValue = b.querySelector(`td:nth-child(${getColumnIndex(header) + 1})`).textContent.trim();
        
        if (isAscending) {
            return bValue.localeCompare(aValue, undefined, { numeric: true });
        } else {
            return aValue.localeCompare(bValue, undefined, { numeric: true });
        }
    });
    
    // Reorder rows in table
    rows.forEach(row => tbody.appendChild(row));
}

/**
 * Get column index of header
 */
function getColumnIndex(header) {
    return Array.from(header.parentNode.children).indexOf(header);
}

/**
 * Initialize auto-save functionality
 */
function initializeAutoSave() {
    const textareas = document.querySelectorAll('textarea[data-autosave]');
    
    textareas.forEach(textarea => {
        let saveTimeout;
        textarea.addEventListener('input', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                autoSaveContent(textarea);
            }, 2000);
        });
        
        // Load saved content on page load
        loadSavedContent(textarea);
    });
}

/**
 * Auto-save textarea content to localStorage
 */
function autoSaveContent(textarea) {
    const key = `autosave_${textarea.name}_${window.location.pathname}`;
    localStorage.setItem(key, textarea.value);
    
    // Show save indicator
    showSaveIndicator(textarea, 'Saved');
}

/**
 * Load saved content from localStorage
 */
function loadSavedContent(textarea) {
    const key = `autosave_${textarea.name}_${window.location.pathname}`;
    const savedContent = localStorage.getItem(key);
    
    if (savedContent && !textarea.value) {
        textarea.value = savedContent;
        showSaveIndicator(textarea, 'Draft restored');
    }
}

/**
 * Show save indicator
 */
function showSaveIndicator(textarea, message) {
    let indicator = textarea.parentNode.querySelector('.save-indicator');
    
    if (!indicator) {
        indicator = document.createElement('small');
        indicator.className = 'save-indicator text-muted';
        textarea.parentNode.appendChild(indicator);
    }
    
    indicator.textContent = message;
    indicator.style.opacity = '1';
    
    setTimeout(() => {
        indicator.style.opacity = '0';
    }, 2000);
}

/**
 * Utility function to debounce function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility function to format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

/**
 * Utility function to format date
 */
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Copied to clipboard!', 'success');
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(notification);
        bsAlert.close();
    }, 3000);
}

/**
 * Initialize keyboard shortcuts
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to submit forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeForm = document.activeElement.closest('form');
            if (activeForm) {
                const submitButton = activeForm.querySelector('button[type="submit"], input[type="submit"]');
                if (submitButton) {
                    submitButton.click();
                }
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const bsModal = bootstrap.Modal.getInstance(openModal);
                if (bsModal) {
                    bsModal.hide();
                }
            }
        }
    });
}

// Initialize keyboard shortcuts
initializeKeyboardShortcuts();

// Export functions for use in other scripts
window.FYPMarketplace = {
    formatCurrency,
    formatDate,
    copyToClipboard,
    showNotification,
    validateField,
    updateProgressBars
};
