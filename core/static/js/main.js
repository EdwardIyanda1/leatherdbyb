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
    
    toast.innerHTML = `<i class="fas fa-check-circle" style="margin-right: 8px;"></i>${message}`;

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
    const size = document.getElementById('productSize')?.value;
    const quantity = parseInt(document.getElementById('productQty')?.textContent || "1");

    if (!size) {
        showToast("Please select a size.");
        return;
    }

    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ size, quantity })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast(`${data.product_name} added to cart!`);
            updateCartCount(data.cart_total_items);
            updateCartModal(data);  // this is the new function
        } else {
            showToast(data.error || "Failed to add to cart.");
        }
    })
    .catch(err => {
        console.error(err);
        showToast("Something went wrong.");
    });
}

function updateCartModal(data) {
    const cartItemsContainer = document.getElementById('cartItems');
    const existingItem = cartItemsContainer.querySelector(`.cart-item[data-product-id="${data.product_id}"]`);
    
    if (existingItem) {
        const qtyDisplay = existingItem.querySelector('.qty-display');
        const totalPrice = existingItem.querySelector('.cart-item-total');
        qtyDisplay.textContent = data.quantity;
        totalPrice.textContent = `₦${data.item_total.toFixed(2)}`;
    } else {
        const itemHTML = `
            <div class="cart-item" data-product-id="${data.product_id}">
                <div class="cart-item-name">${data.product_name}</div>
                <div class="cart-item-price">₦${data.product_price.toFixed(2)}</div>
                <div class="quantity-controls">
                    <button class="qty-btn" onclick="updateCartItem(${data.product_id}, 'decrement')">
                        <i class="fas fa-minus"></i>
                    </button>
                    <span class="qty-display">${data.quantity}</span>
                    <button class="qty-btn" onclick="updateCartItem(${data.product_id}, 'increment')">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
                <div class="cart-item-total">₦${data.item_total.toFixed(2)}</div>
            </div>
        `;
        cartItemsContainer.insertAdjacentHTML('beforeend', itemHTML);
    }

    // Update subtotal and total
    const summarySubtotal = document.querySelector('.summary-value-subtotal');
    const summaryTotal = document.querySelector('.summary-total span:last-child');
    if (summarySubtotal) summarySubtotal.textContent = `₦${data.cart_subtotal.toFixed(2)}`;
    if (summaryTotal) summaryTotal.textContent = `₦${data.cart_total.toFixed(2)}`;
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