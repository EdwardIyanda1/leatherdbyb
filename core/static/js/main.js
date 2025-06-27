const quantity = parseInt(document.getElementById('productQty')?.textContent || "1");

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

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function addToCart(productId, productName, productPrice) {
    const quantity = parseInt(document.getElementById('productQty')?.textContent || "1");
    const size = document.getElementById('productSize')?.value;

    if (!size) {
        alert("Please select a size.");
        return;
    }

    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            size: size,
            quantity: quantity
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert(`${productName} added to cart successfully!`);
        } else {
            alert(data.error || "Something went wrong.");
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert("Something went wrong.");
    });
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