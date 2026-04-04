/**
 * main.js - Client Side Javascript
 * Handles interactions, DOM manipulation, and API requests to Flask backend.
 * Uses vanilla Javascript and standard Fetch API for beginner friendliness.
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // --- State Management ---
    let currentUser = null;
    let products = [];
    let cart = [];

    // --- DOM Elements ---
    const productGrid = document.getElementById('productGrid');
    
    // Search Elements
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.querySelector('.search-btn');
    
    // Auth Elements
    const authContainer = document.getElementById('authContainer');
    const authModal = document.getElementById('authModal');
    const closeAuthModal = document.getElementById('closeAuthModal');
    
    // Login Form Elements
    const loginBox = document.getElementById('loginBox');
    const loginForm = document.getElementById('loginForm');
    const showRegisterBtn = document.getElementById('showRegisterBtn');
    const loginError = document.getElementById('loginError');
    
    // Register Form Elements
    const registerBox = document.getElementById('registerBox');
    const registerForm = document.getElementById('registerForm');
    const showLoginBtn = document.getElementById('showLoginBtn');
    const registerError = document.getElementById('registerError');
    
    // Cart Elements
    const cartCountBadge = document.getElementById('cartCountBadge');
    const openCartBtn = document.getElementById('openCartBtn');
    const closeCartBtn = document.getElementById('closeCartBtn');
    const cartSidebar = document.getElementById('cartSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const cartContent = document.getElementById('cartContent');
    const cartTotalAmount = document.getElementById('cartTotalAmount');
    const checkoutBtn = document.getElementById('checkoutBtn');
    const checkoutMessage = document.getElementById('checkoutMessage');

    // --- Initialize Application ---
    checkAuthState();
    loadProducts();

    // ==========================================
    // API CALLS (Using simple Fetch)
    // ==========================================

    /**
     * Fetch products from API
     */
    async function loadProducts() {
        if (!productGrid) return;
        
        // Use custom endpoint if specified, otherwise default to all products
        let endpoint = productGrid.dataset.endpoint || '/api/products';
        
        // Handle search query from URL across pages
        const urlParams = new URLSearchParams(window.location.search);
        const searchQuery = urlParams.get('search');
        if (searchQuery) {
            if (endpoint.includes('?')) {
                endpoint += `&search=${encodeURIComponent(searchQuery)}`;
            } else {
                endpoint += `?search=${encodeURIComponent(searchQuery)}`;
            }
            if (searchInput) {
                searchInput.value = searchQuery;
            }
        }
        
        try {
            const response = await fetch(endpoint);
            products = await response.json();
            renderProducts();
        } catch (error) {
            console.error('Error fetching products:', error);
            productGrid.innerHTML = '<div class="auth-error">Failed to load products. Please check if backend is running.</div>';
        }
    }

    /**
     * Check if user is logged in
     */
    async function checkAuthState() {
        try {
            const response = await fetch('/api/user');
            const data = await response.json();
            
            if (data.loggedIn) {
                currentUser = data.username;
                updateAuthUI();
                loadCart(); // Load cart data if logged in
            } else {
                currentUser = null;
                updateAuthUI();
            }
        } catch (error) {
            console.error('Auth state check failed:', error);
        }
    }

    /**
     * Fetch user's cart from API
     */
    async function loadCart() {
        if (!currentUser) return;
        
        try {
            const response = await fetch('/api/cart');
            if (response.ok) {
                cart = await response.json();
                renderCart();
            }
        } catch (error) {
            console.error('Error loading cart:', error);
        }
    }

    /**
     * Add a product to cart via API
     */
    async function addToCart(productId, event) {
        if (!currentUser) {
            openModal(loginBox, registerBox); // Require login first
            return;
        }

        try {
            const response = await fetch('/api/cart/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_id: productId })
            });

            if (response.ok) {
                // Show message
                if (event && event.target) {
                    const button = event.target;
                    const originalText = button.innerHTML;
                    button.innerHTML = "Product is added to cart";
                    button.style.backgroundColor = "#28a745"; // Success green text briefly
                    button.style.color = "white";
                    
                    setTimeout(() => {
                        button.innerHTML = originalText;
                        button.style.backgroundColor = "";
                        button.style.color = "";
                    }, 2000);
                } else {
                    alert("Product is added to cart");
                }

                await loadCart();
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
        }
    }

    /**
     * Update quantity of a cart item or remove it
     */
    async function updateCartItem(cartId, action) {
        try {
            const response = await fetch('/api/cart/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cart_id: cartId, action: action })
            });

            if (response.ok) {
                await loadCart();
            }
        } catch (error) {
            console.error('Error updating cart:', error);
        }
    }

    // ==========================================
    // UI RENDERING
    // ==========================================

    /**
     * Render the product grid dynamically
     */
    function renderProducts(productsToRender = products) {
        productGrid.innerHTML = '';
        
        if (productsToRender.length === 0) {
            productGrid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 2rem;">No products found matching your search.</div>';
            return;
        }
        
        productsToRender.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';
            
            // Format price
            const formattedPrice = `₹${product.price.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            
            card.innerHTML = `
                <img src="${product.image_url}" alt="${product.name}" class="product-image" onerror="this.onerror=null; this.src='https://via.placeholder.com/400?text=Product';">
                <h3 class="product-title">${product.name}</h3>
                <div class="product-price">${formattedPrice}</div>
                <div class="product-desc">${product.description}</div>
                <button class="btn btn-primary btn-block" onclick="window.addToCart(${product.id}, event)">
                    Add to Cart
                </button>
                <button class="btn btn-secondary btn-block" style="margin-top: 5px; background: #ffe4e1; color: #d00000; border: none; padding: 5px; cursor: pointer; height: 40px; border-radius: 8px;" onclick="window.addToWishlist(${product.id}, event)">
                    <i class="fa-solid fa-heart"></i> Add to Wishlist
                </button>
            `;
            productGrid.appendChild(card);
        });
    }

    /**
     * Render cart items in the sidebar
     */
    function renderCart() {
        let total = 0;
        let totalItems = 0;
        cartContent.innerHTML = '';

        if (cart.length === 0) {
            cartContent.innerHTML = '<div class="empty-cart">Your cart is empty. Start shopping!</div>';
            checkoutBtn.disabled = true;
        } else {
            checkoutBtn.disabled = false;
            
            cart.forEach(item => {
                total += item.price * item.quantity;
                totalItems += item.quantity;
                
                const itemEl = document.createElement('div');
                itemEl.className = 'cart-item';
                itemEl.innerHTML = `
                    <img src="${item.image_url}" class="cart-item-img" alt="${item.name}" onerror="this.onerror=null; this.src='https://via.placeholder.com/400?text=Product';">
                    <div class="cart-item-details">
                        <div class="cart-item-title">${item.name}</div>
                        <div class="cart-item-price">₹${item.price.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                        <div class="cart-item-actions">
                            <button class="qty-btn" onclick="window.updateCartItem(${item.cart_id}, 'decrease')">-</button>
                            <span>${item.quantity}</span>
                            <button class="qty-btn" onclick="window.updateCartItem(${item.cart_id}, 'increase')">+</button>
                            <button class="remove-btn" onclick="window.updateCartItem(${item.cart_id}, 'remove')">Remove</button>
                        </div>
                    </div>
                `;
                cartContent.appendChild(itemEl);
            });
        }

        // Update total and badge
        cartTotalAmount.textContent = `₹${total.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        cartCountBadge.textContent = totalItems;
    }

    /**
     * Update Navigation depending on auth state
     */
    function updateAuthUI() {
        if (currentUser) {
            authContainer.innerHTML = `
                <div class="nav-btn">
                    <span class="small-text">Hello, ${currentUser}</span>
                    <span class="bold-text">Account & Lists</span>
                </div>
                <button id="logoutBtn" class="btn-link" style="margin-left: 10px;">Sign Out</button>
            `;
            // Add logout listener
            document.getElementById('logoutBtn').addEventListener('click', handleLogout);
        } else {
            authContainer.innerHTML = `
                <button id="loginBtnTrigger" class="nav-btn auth-btn">
                    <span class="small-text">Hello, sign in</span>
                    <span class="bold-text">Account & Lists</span>
                </button>
            `;
            // Add login listener
            document.getElementById('loginBtnTrigger').addEventListener('click', () => openModal(loginBox, registerBox));
            
            // Reset cart
            cart = [];
            renderCart();
        }
    }

    // ==========================================
    // EVENT LISTENERS & HANDLERS
    // ==========================================

    // Expose functions to window so inline onclick handlers in HTML work
    window.addToCart = addToCart;
    window.updateCartItem = updateCartItem;
    window.addToWishlist = addToWishlist;

    /**
     * Add a product to wishlist via API
     */
    async function addToWishlist(productId, event) {
        if (!currentUser) {
            openModal(loginBox, registerBox); // Require login first
            return;
        }

        try {
            const response = await fetch('/api/wishlist/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_id: productId })
            });

            if (response.ok) {
                if (event && event.target) {
                    let button = event.target;
                    // In case we clicked the icon inside the button
                    if(button.tagName === 'I') button = button.parentElement;
                    const originalText = button.innerHTML;
                    button.innerHTML = "Added to wishlist!";
                    button.style.backgroundColor = "#ffc0cb";
                    
                    setTimeout(() => {
                        button.innerHTML = originalText;
                        button.style.backgroundColor = "#ffe4e1";
                    }, 2000);
                } else {
                    alert("Added to wishlist!");
                }
            }
        } catch (error) {
            console.error('Error adding to wishlist:', error);
        }
    }

    /**
     * Login Submit
     */
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        loginError.textContent = '';

        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            
            if (res.ok) {
                closeModal();
                checkAuthState(); // Refreshes UI and fetches cart
            } else {
                loginError.textContent = data.error || 'Login failed';
            }
        } catch (err) {
            loginError.textContent = 'Network error. Please try again.';
        }
    });

    /**
     * Register Submit
     */
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const password = document.getElementById('registerPassword').value;
        registerError.textContent = '';

        try {
            const res = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            
            if (res.ok) {
                // Auto login after register
                await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                closeModal();
                checkAuthState();
            } else {
                registerError.textContent = data.error || 'Registration failed';
            }
        } catch (err) {
            registerError.textContent = 'Network error. Please try again.';
        }
    });

    /**
     * Logout Handler
     */
    async function handleLogout() {
        try {
            await fetch('/api/logout', { method: 'POST' });
            checkAuthState();
        } catch (err) {
            console.error(err);
        }
    }

    /**
     * Checkout Submision
     */
    checkoutBtn.addEventListener('click', async () => {
        if (!currentUser) return;
        
        try {
            const res = await fetch('/api/checkout', { method: 'POST' });
            const data = await res.json();
            
            if (res.ok) {
                cart = []; // Empty cart locally
                cartContent.innerHTML = '<div class="empty-cart" style="color: #28a745; font-weight: bold; font-size: 1.2rem;">Your order is placed successfully!</div>';
                cartTotalAmount.textContent = '₹0.00';
                cartCountBadge.textContent = '0';
                checkoutBtn.disabled = true;
                checkoutMessage.textContent = '';
            } else {
                checkoutMessage.textContent = data.error || 'Checkout failed';
                checkoutMessage.style.color = "red";
            }
        } catch (err) {
            console.error('Checkout error:', err);
            checkoutMessage.textContent = 'Network error. Please try again.';
            checkoutMessage.style.color = "red";
        }
    });

    /**
     * Search Functionality
     */
    async function performSearch() {
        if (!searchInput) return;
        const query = searchInput.value.trim();
        
        if (!productGrid) {
            // If on a page without product grid, redirect to home with search param
            window.location.href = `/?search=${encodeURIComponent(query)}`;
            return;
        }

        let endpoint = productGrid.dataset.endpoint || '/api/products';
        
        if (query !== '') {
            if (endpoint.includes('?')) {
                endpoint += `&search=${encodeURIComponent(query)}`;
            } else {
                endpoint += `?search=${encodeURIComponent(query)}`;
            }
        }
        
        try {
            productGrid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 2rem;">Searching...</div>';
            const response = await fetch(endpoint);
            const searchResults = await response.json();
            renderProducts(searchResults);
        } catch (error) {
            console.error('Error searching products:', error);
            productGrid.innerHTML = '<div class="auth-error">Search failed.</div>';
        }
    }

    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', performSearch);
        searchInput.addEventListener('keyup', (e) => {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        // We'll remove real-time input filtering to avoid spamming the backend
    }

    // --- Modal and Sidebar Toggles ---

    function openModal(showBox, hideBox) {
        authModal.classList.add('active');
        showBox.classList.remove('hidden');
        hideBox.classList.add('hidden');
        // Clear forms
        loginForm.reset();
        registerForm.reset();
        loginError.textContent = '';
        registerError.textContent = '';
    }

    function closeModal() {
        authModal.classList.remove('active');
    }

    // Open/Close Auth Modal
    if (closeAuthModal) closeAuthModal.addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        if (e.target === authModal) closeModal();
    });

    // Switch between Login and Register views
    showRegisterBtn.addEventListener('click', () => {
        loginBox.classList.add('hidden');
        registerBox.classList.remove('hidden');
    });
    showLoginBtn.addEventListener('click', (e) => {
        e.preventDefault();
        registerBox.classList.add('hidden');
        loginBox.classList.remove('hidden');
    });

    // Cart Sidebar Toggles
    openCartBtn.addEventListener('click', () => {
        cartSidebar.classList.add('active');
        sidebarOverlay.classList.add('active');
    });

    function closeSidebar() {
        cartSidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
    }

    closeCartBtn.addEventListener('click', closeSidebar);
    sidebarOverlay.addEventListener('click', closeSidebar);

});
