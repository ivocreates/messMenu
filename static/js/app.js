// Mess Menu Rater JavaScript Functions

// Global variables
let orderItems = [];
let currentRatings = {};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    console.log('Mess Menu Rater App Initialized');
    
    // Initialize rating functionality
    initializeRatingStars();
    
    // Initialize order functionality
    initializeOrderSystem();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Add fade-in animation to cards
    addFadeInAnimation();
}

// Rating System Functions
function initializeRatingStars() {
    const ratingStars = document.querySelectorAll('.rating-stars');
    
    ratingStars.forEach(starsContainer => {
        const itemId = starsContainer.dataset.itemId;
        const stars = starsContainer.querySelectorAll('.rating-star');
        let selectedRating = 0;
        
        stars.forEach((star, index) => {
            star.addEventListener('mouseenter', () => {
                highlightStars(stars, index + 1);
            });
            
            star.addEventListener('mouseleave', () => {
                highlightStars(stars, selectedRating);
            });
            
            star.addEventListener('click', () => {
                selectedRating = index + 1;
                highlightStars(stars, selectedRating);
                starsContainer.dataset.selectedRating = selectedRating;
                currentRatings[itemId] = selectedRating;
            });
        });
    });
    
    // Submit rating buttons
    document.querySelectorAll('.submit-rating').forEach(button => {
        button.addEventListener('click', handleRatingSubmission);
    });
}

function highlightStars(stars, rating) {
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('text-warning');
            star.classList.remove('text-muted');
        } else {
            star.classList.add('text-muted');
            star.classList.remove('text-warning');
        }
    });
}

function handleRatingSubmission(event) {
    const button = event.target;
    const itemId = button.dataset.itemId;
    const starsContainer = document.querySelector(`.rating-stars[data-item-id="${itemId}"]`);
    const rating = starsContainer?.dataset.selectedRating;
    const comment = document.getElementById(`comment-${itemId}`)?.value || '';
    
    if (!rating) {
        showAlert('Please select a rating!', 'warning');
        return;
    }
    
    // Show loading state
    button.innerHTML = '<span class="spinner"></span>Submitting...';
    button.disabled = true;
    
    submitRating(itemId, rating, comment, button);
}

function submitRating(itemId, rating, comment, button) {
    fetch('/rate_item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            menu_item_id: itemId,
            rating: parseInt(rating),
            comment: comment
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            // Reset button
            button.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Rating';
            button.disabled = false;
            
            // Optionally reload to show updated ratings
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showAlert(data.message, 'danger');
            button.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Rating';
            button.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('An error occurred while submitting your rating.', 'danger');
        button.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Rating';
        button.disabled = false;
    });
}

// Order System Functions
function initializeOrderSystem() {
    // Add to order buttons
    document.querySelectorAll('.add-to-order').forEach(button => {
        button.addEventListener('click', handleAddToOrder);
    });
    
    // Order action buttons
    const clearOrderBtn = document.getElementById('clear-order');
    const placeOrderBtn = document.getElementById('place-order');
    
    if (clearOrderBtn) {
        clearOrderBtn.addEventListener('click', clearOrder);
    }
    
    if (placeOrderBtn) {
        placeOrderBtn.addEventListener('click', placeOrder);
    }
}

function handleAddToOrder(event) {
    const button = event.target;
    const itemId = button.dataset.itemId;
    const itemName = button.dataset.itemName;
    const price = parseFloat(button.dataset.price);
    
    addToOrder(itemId, itemName, price);
    
    // Visual feedback
    button.classList.add('pulse');
    setTimeout(() => {
        button.classList.remove('pulse');
    }, 1000);
}

function addToOrder(itemId, itemName, price) {
    const existingItem = orderItems.find(item => item.id === itemId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        orderItems.push({
            id: itemId,
            name: itemName,
            price: price,
            quantity: 1
        });
    }
    
    updateOrderDisplay();
    showAlert(`${itemName} added to order!`, 'success', 2000);
}

function updateOrderDisplay() {
    const orderSummary = document.getElementById('order-summary');
    const orderItemsContainer = document.getElementById('order-items');
    const orderTotal = document.getElementById('order-total');
    
    if (!orderSummary) return;
    
    if (orderItems.length === 0) {
        orderSummary.style.display = 'none';
        return;
    }
    
    orderSummary.style.display = 'block';
    orderSummary.classList.add('fade-in');
    
    let html = '';
    let total = 0;
    
    orderItems.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        html += `
            <div class="d-flex justify-content-between align-items-center mb-2 order-item">
                <div>
                    <strong>${item.name}</strong><br>
                    <small>₹${item.price.toFixed(2)} × ${item.quantity}</small>
                </div>
                <div>
                    <span class="me-2">₹${itemTotal.toFixed(2)}</span>
                    <button class="btn btn-sm btn-outline-danger" 
                           onclick="removeFromOrder('${item.id}')">
                        <i class="fas fa-minus"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    if (orderItemsContainer) {
        orderItemsContainer.innerHTML = html;
    }
    
    if (orderTotal) {
        orderTotal.textContent = total.toFixed(2);
    }
}

function removeFromOrder(itemId) {
    const itemIndex = orderItems.findIndex(item => item.id === itemId);
    if (itemIndex > -1) {
        if (orderItems[itemIndex].quantity > 1) {
            orderItems[itemIndex].quantity -= 1;
        } else {
            orderItems.splice(itemIndex, 1);
        }
        updateOrderDisplay();
    }
}

function clearOrder() {
    if (orderItems.length === 0) {
        showAlert('Order is already empty!', 'info');
        return;
    }
    
    if (confirm('Are you sure you want to clear your order?')) {
        orderItems = [];
        updateOrderDisplay();
        showAlert('Order cleared!', 'info');
    }
}

function placeOrder() {
    if (orderItems.length === 0) {
        showAlert('Your order is empty!', 'warning');
        return;
    }
    
    const total = orderItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    if (confirm(`Place order for ₹${total.toFixed(2)}?`)) {
        // Here you would typically send the order to the server
        showAlert('Order placed successfully! (Feature in development)', 'success');
        orderItems = [];
        updateOrderDisplay();
    }
}

// Form Validation Functions
function initializeFormValidations() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showAlert('Please fill in all required fields correctly.', 'warning');
            }
            form.classList.add('was-validated');
        });
    });
}

// Utility Functions
function showAlert(message, type = 'info', duration = 4000) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.style.position = 'fixed';
    alertContainer.style.top = '20px';
    alertContainer.style.right = '20px';
    alertContainer.style.zIndex = '9999';
    alertContainer.style.minWidth = '300px';
    
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    // Auto remove after duration
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.remove();
        }
    }, duration);
}

function addFadeInAnimation() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// Admin Functions
function deleteMenuItem(itemId) {
    if (confirm('Are you sure you want to delete this menu item?')) {
        // Here you would typically make an AJAX call to delete the item
        showAlert('Delete functionality will be implemented in the next version.', 'info');
    }
}

// Export functions for global access
window.removeFromOrder = removeFromOrder;
window.deleteMenuItem = deleteMenuItem;
