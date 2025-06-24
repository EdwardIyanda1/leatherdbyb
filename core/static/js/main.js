// Cart functionality
function addToCart(productId, productName, price) {
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(`${productName} added to cart!`);
            updateCartCount(data.total_items);
        }
    });
}

function updateCartCount(count) {
    const cartCount = document.getElementById('cartCount');
    cartCount.textContent = count;
    
    if (count === 0) {
        cartCount.style.display = 'none';
    } else {
        cartCount.style.display = 'flex';
    }
}

// Wishlist functionality
function toggleWishlist(productId) {
    const wishlistBtn = document.querySelector(`.wishlist-btn[data-product-id="${productId}"]`);
    const isInWishlist = wishlistBtn.classList.contains('in-wishlist');
    
    if (isInWishlist) {
        fetch(`/account/wishlist/remove/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                wishlistBtn.classList.remove('in-wishlist');
                wishlistBtn.innerHTML = '<i class="far fa-heart"></i>';
                showToast('Removed from wishlist');
            }
        });
    } else {
        fetch(`/account/wishlist/add/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                wishlistBtn.classList.add('in-wishlist');
                wishlistBtn.innerHTML = '<i class="fas fa-heart"></i>';
                showToast('Added to wishlist!');
            }
        });
    }
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Toast notifications
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const productId = this.dataset.productId;
            const productName = this.dataset.productName;
            const price = parseFloat(this.dataset.productPrice);
            addToCart(productId, productName, price);
        });
    });
    
    document.querySelectorAll('.wishlist-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const productId = this.dataset.productId;
            toggleWishlist(productId);
        });
    });
    
    // Page navigation
    document.querySelectorAll('[data-page]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            window.location.href = `/${page}/`;
        });
    });
});