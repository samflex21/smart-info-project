// Global variables
let currentProduct = null;
let currentRating = 0;
let cart = [];
let currentView = 'grid';
let currentPage = 1;
let itemsPerPage = 12;

// DOM Elements
const searchInput = document.getElementById('searchInput');
const categoryFilter = document.getElementById('categoryFilter');
const productList = document.getElementById('productList');
const ratingSection = document.getElementById('ratingSection');
const recommendationsSection = document.getElementById('recommendationsSection');
const recommendationsList = document.getElementById('recommendationsList');
const userRatings = document.getElementById('userRatings');
const ratingStars = document.querySelectorAll('.rating-stars i');
const submitRatingBtn = document.getElementById('submitRating');

// Event Listeners
searchInput.addEventListener('input', debounce(searchProducts, 300));
categoryFilter.addEventListener('change', handleCategoryChange);
sortOptions.addEventListener('change', handleSort);
priceRange.addEventListener('input', handlePriceRangeChange);
minPrice.addEventListener('input', handlePriceInput);
maxPrice.addEventListener('input', handlePriceInput);
cartButton.addEventListener('click', toggleCart);
closeCart.addEventListener('click', toggleCart);
viewButtons.forEach(btn => btn.addEventListener('click', () => switchView(btn.dataset.view)));

ratingStars.forEach(star => {
    star.addEventListener('mouseover', () => highlightStars(star.dataset.rating));
    star.addEventListener('mouseout', () => highlightStars(currentRating));
    star.addEventListener('click', () => setRating(star.dataset.rating));
});

// Initialize
loadUserRatings();
searchProducts();

// Cart Functions
function toggleCart() {
    cartSidebar.classList.toggle('active');
}

function addToCart(product, quantity = 1) {
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({ ...product, quantity });
    }
    
    updateCartUI();
    showAlert('Product added to cart', 'success');
}

function updateCartUI() {
    const cartItems = document.querySelector('.cart-items');
    const cartCount = document.querySelector('.cart-count');
    const totalAmount = document.querySelector('.total-amount');
    
    cartCount.textContent = cart.reduce((sum, item) => sum + item.quantity, 0);
    
    cartItems.innerHTML = cart.map(item => `
        <div class="cart-item">
            <img src="${item.image}" alt="${item.name}" class="cart-item-image">
            <div class="cart-item-details">
                <h6>${item.name}</h6>
                <div class="price">$${item.price}</div>
                <div class="quantity">
                    <button onclick="updateCartItemQuantity(${item.id}, ${item.quantity - 1})">-</button>
                    <span>${item.quantity}</span>
                    <button onclick="updateCartItemQuantity(${item.id}, ${item.quantity + 1})">+</button>
                </div>
            </div>
            <button onclick="removeFromCart(${item.id})" class="btn-close"></button>
        </div>
    `).join('');
    
    totalAmount.textContent = '$' + cart.reduce((sum, item) => sum + (item.price * item.quantity), 0).toFixed(2);
}

function updateCartItemQuantity(productId, newQuantity) {
    if (newQuantity < 1) {
        removeFromCart(productId);
        return;
    }
    
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity = newQuantity;
        updateCartUI();
    }
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCartUI();
}

// Product Display Functions
function displayProducts(products) {
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const paginatedProducts = products.slice(start, end);
    
    productCount.textContent = `${products.length} Products`;
    
    productGrid.innerHTML = paginatedProducts.map(product => `
        <div class="col">
            <div class="product-card">
                ${product.discount ? `<div class="product-badge">-${product.discount}%</div>` : ''}
                <button class="wishlist-button" onclick="toggleWishlist(${product.id})">
                    <i class="far fa-heart"></i>
                </button>
                <div class="product-image">
                    <img src="${product.image}" alt="${product.name}">
                </div>
                <h5 class="product-title">${product.name}</h5>
                <div class="product-category">${product.category}</div>
                <div class="rating">
                    ${'⭐'.repeat(Math.round(product.avg_rating))}
                    <span class="rating-count">(${product.total_ratings})</span>
                </div>
                <div class="mt-2">
                    ${product.original_price ? `
                        <span class="product-original-price">$${product.original_price}</span>
                    ` : ''}
                    <span class="product-price">$${product.price}</span>
                    ${product.discount ? `
                        <span class="product-discount">${product.discount}% OFF</span>
                    ` : ''}
                </div>
                <button class="btn btn-primary w-100 mt-2" onclick="addToCart(${JSON.stringify(product)})">
                    Add to Cart
                </button>
            </div>
        </div>
    `).join('');
    
    updatePagination(products.length);
}

function updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const pagination = document.querySelector('.pagination');
    
    let html = `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage - 1})">Previous</a>
        </li>
    `;
    
    for (let i = 1; i <= totalPages; i++) {
        html += `
            <li class="page-item ${currentPage === i ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
            </li>
        `;
    }
    
    html += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage + 1})">Next</a>
        </li>
    `;
    
    pagination.innerHTML = html;
}

function changePage(page) {
    currentPage = page;
    searchProducts();
}

function switchView(view) {
    currentView = view;
    productGrid.className = view === 'grid' 
        ? 'row row-cols-1 row-cols-md-3 g-4'
        : 'row row-cols-1 g-4';
    
    viewButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });
    
    searchProducts();
}

// Filter and Sort Functions
function handleCategoryChange() {
    currentPage = 1;
    currentCategory.textContent = categoryFilter.value || 'All Products';
    searchProducts();
}

function handleSort() {
    searchProducts();
}

function handlePriceRangeChange(e) {
    const value = e.target.value;
    minPrice.value = 0;
    maxPrice.value = value;
    searchProducts();
}

function handlePriceInput() {
    const min = parseInt(minPrice.value) || 0;
    const max = parseInt(maxPrice.value) || 1000;
    priceRange.value = max;
    searchProducts();
}

// Search and API Functions
async function searchProducts() {
    const query = searchInput.value;
    const category = categoryFilter.value;
    const sort = sortOptions.value;
    const min = parseInt(minPrice.value) || 0;
    const max = parseInt(maxPrice.value) || 1000;
    
    showLoading(productGrid);
    
    try {
        const response = await fetch(`/api/search?query=${encodeURIComponent(query)}
            &category=${encodeURIComponent(category)}
            &sort=${encodeURIComponent(sort)}
            &min_price=${min}&max_price=${max}`);
        const products = await response.json();
        
        displayProducts(products);
    } catch (error) {
        console.error('Error searching products:', error);
        productGrid.innerHTML = '<div class="alert alert-danger">Error loading products</div>';
    }
}

// Rating Functions
function highlightStars(rating) {
    ratingStars.forEach((star, index) => {
        if (index < rating) {
            star.classList.remove('far');
            star.classList.add('fas');
        } else {
            star.classList.remove('fas');
            star.classList.add('far');
        }
    });
}

function setRating(rating) {
    currentRating = rating;
    highlightStars(rating);
}

// Utility Functions
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

function showLoading(element) {
    element.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner"></i>
            <div>Loading...</div>
        </div>
    `;
}

function showAlert(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alert.style.zIndex = '1050';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 3000);
}
