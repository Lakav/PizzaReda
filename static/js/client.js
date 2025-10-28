// Configuration
const API_BASE = '/';
let cart = [];
let menu = [];

// DOM Elements
const navBtns = document.querySelectorAll('.nav-btn');
const tabContents = document.querySelectorAll('.tab-content');
const menuContainer = document.getElementById('menu-container');
const cartItemsContainer = document.getElementById('cart-items');
const customerForm = document.getElementById('customer-form');
const submitOrderBtn = document.getElementById('submit-order');
const trackBtn = document.getElementById('track-btn');
const trackingInput = document.getElementById('tracking-id');
const trackingResult = document.getElementById('tracking-result');
const trackingError = document.getElementById('tracking-error');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadMenu();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Tab navigation
    navBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            switchTab(tabName);
        });
    });

    // Cart and order
    customerForm.addEventListener('submit', placeOrder);
    submitOrderBtn.addEventListener('click', (e) => {
        e.preventDefault();
        placeOrder();
    });

    // Tracking
    trackBtn.addEventListener('click', trackOrder);
    trackingInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') trackOrder();
    });
}

// Load pizza menu
async function loadMenu() {
    try {
        const response = await fetch(API_BASE + 'pizzas/menu');
        if (!response.ok) throw new Error('Erreur lors du chargement du menu');

        menu = await response.json();
        renderMenu();
    } catch (error) {
        showAlert('Erreur lors du chargement du menu: ' + error.message, 'error');
        console.error(error);
    }
}

// Render pizza menu
function renderMenu() {
    menuContainer.innerHTML = '';
    menu.forEach(pizza => {
        const pizzaEl = document.createElement('div');
        pizzaEl.className = 'pizza-item';
        pizzaEl.innerHTML = `
            <div class="pizza-name">${pizza.name}</div>
            <div class="pizza-toppings">
                ${pizza.base_toppings.join(', ')}
            </div>
            <div class="pizza-sizes">
                <button type="button" class="size-btn" data-size="small" data-price="${pizza.prices.small}">
                    S: ${pizza.prices.small}€
                </button>
                <button type="button" class="size-btn" data-size="medium" data-price="${pizza.prices.medium}">
                    M: ${pizza.prices.medium}€
                </button>
                <button type="button" class="size-btn" data-size="large" data-price="${pizza.prices.large}">
                    L: ${pizza.prices.large}€
                </button>
            </div>
        `;

        // Size selection
        const sizeButtons = pizzaEl.querySelectorAll('.size-btn');
        sizeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                sizeButtons.forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');

                // Add to cart
                const size = btn.dataset.size;
                const price = parseFloat(btn.dataset.price);
                addToCart(pizza.name, size, price, pizza.base_toppings);
            });
        });

        menuContainer.appendChild(pizzaEl);
    });
}

// Add to cart
function addToCart(name, size, price, toppings) {
    cart.push({
        name: name,
        size: size,
        price: price,
        toppings: toppings
    });
    updateCart();
    showAlert(`${name} (${size.toUpperCase()}) ajoutée au panier`, 'success');
}

// Update cart display
function updateCart() {
    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p style="color: #999;">Aucune pizza sélectionnée</p>';
        return;
    }

    let html = '';
    let total = 0;

    cart.forEach((item, index) => {
        total += item.price;
        html += `
            <div class="cart-item">
                <div>
                    <div style="font-weight: bold;">${item.name}</div>
                    <div style="font-size: 0.9em; color: #666;">${item.size.toUpperCase()} - ${item.price.toFixed(2)}€</div>
                </div>
                <button type="button" class="btn btn-danger btn-small" onclick="removeFromCart(${index})">×</button>
            </div>
        `;
    });

    // Frais de livraison
    const deliveryFee = total >= 30 ? 0 : 5;
    const totalWithDelivery = total + deliveryFee;

    html += `
        <div style="padding-top: 15px; border-top: 2px solid var(--primary-color); margin-top: 15px;">
            <div class="cart-item">
                <span>Sous-total</span>
                <span>${total.toFixed(2)}€</span>
            </div>
            <div class="cart-item">
                <span>Frais de livraison</span>
                <span>${deliveryFee === 0 ? 'GRATUIT' : deliveryFee.toFixed(2) + '€'}</span>
            </div>
            <div class="cart-total">
                <div style="display: flex; justify-content: space-between;">
                    <span>TOTAL:</span>
                    <span>${totalWithDelivery.toFixed(2)}€</span>
                </div>
            </div>
        </div>
    `;

    cartItemsContainer.innerHTML = html;
}

// Remove from cart
function removeFromCart(index) {
    cart.splice(index, 1);
    updateCart();
}

// Place order
async function placeOrder() {
    if (cart.length === 0) {
        showAlert('Veuillez sélectionner au moins une pizza', 'error');
        return;
    }

    const customerName = document.getElementById('customer-name').value.trim();
    const streetNumber = document.getElementById('street-number').value.trim();
    const streetName = document.getElementById('street-name').value.trim();
    const postalCode = document.getElementById('postal-code').value.trim();
    const city = document.getElementById('city').value.trim();

    if (!customerName || !streetNumber || !streetName) {
        showAlert('Veuillez remplir tous les champs requis', 'error');
        return;
    }

    submitOrderBtn.disabled = true;
    submitOrderBtn.innerHTML = '<span class="loading"></span> Traitement...';

    try {
        const orderData = {
            customer_name: customerName,
            pizzas: cart,
            customer_address: {
                street_number: streetNumber,
                street: streetName,
                city: city,
                postal_code: postalCode
            }
        };

        const response = await fetch(API_BASE + 'orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erreur lors de la création de la commande');
        }

        const result = await response.json();

        showAlert(
            `Commande créée avec succès! Numéro: ${result.order_id}\n` +
            `Total: ${result.total}€\n` +
            `Votre commande sera livrée à: ${result.customer_address}`,
            'success'
        );

        // Reset form and cart
        cart = [];
        customerForm.reset();
        document.getElementById('postal-code').value = '31000';
        document.getElementById('city').value = 'Toulouse';
        updateCart();

        // Auto-switch to tracking tab
        setTimeout(() => {
            switchTab('tracking-tab');
            trackingInput.value = result.order_id;
            trackOrder();
        }, 1500);

    } catch (error) {
        showAlert('Erreur: ' + error.message, 'error');
    } finally {
        submitOrderBtn.disabled = false;
        submitOrderBtn.innerHTML = 'Valider la commande';
    }
}

// Track order
async function trackOrder() {
    const orderId = trackingInput.value.trim();

    if (!orderId) {
        showAlert('Veuillez entrer un numéro de commande', 'error');
        return;
    }

    trackingError.classList.add('hidden');
    trackingResult.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE}orders/${orderId}/status`);

        if (!response.ok) {
            throw new Error('Commande non trouvée');
        }

        const order = await response.json();
        displayOrderTracking(order);
        trackingResult.classList.remove('hidden');

    } catch (error) {
        showTrackingError(error.message);
    }
}

// Display order tracking info
function displayOrderTracking(order) {
    document.getElementById('track-order-id').textContent = order.order_id;
    document.getElementById('track-customer-name').textContent = order.customer_name;
    document.getElementById('track-address').textContent = order.customer_address;
    document.getElementById('track-subtotal').textContent = order.subtotal.toFixed(2) + '€';
    document.getElementById('track-delivery-fee').textContent =
        order.delivery_fee === 0 ? 'GRATUIT' : order.delivery_fee.toFixed(2) + '€';
    document.getElementById('track-total').textContent = order.total.toFixed(2) + '€';
    document.getElementById('track-time').textContent = order.estimated_delivery_minutes + ' minutes';

    // Status badge and label
    const statusBadge = document.getElementById('track-status-badge');
    const statusLabel = document.getElementById('track-status-label');
    statusBadge.textContent = order.status_label;
    statusBadge.className = `badge badge-${order.status.replace('_', '-')}`;
    statusLabel.textContent = order.status_label;

    // Progress bar
    const progressBar = document.getElementById('track-progress');
    progressBar.style.width = order.progress_percent + '%';
    progressBar.textContent = order.progress_percent + '%';

    // Pizzas
    const pizzasHtml = order.pizzas.map(pizza => `
        <div style="margin-bottom: 15px; padding: 10px; background: var(--light-bg); border-radius: 4px;">
            <div style="font-weight: bold;">${pizza.name} <span style="color: #999; font-weight: normal;">(${pizza.size.toUpperCase()})</span></div>
            <div style="font-size: 0.9em; color: #666;">
                Toppings: ${pizza.toppings.join(', ')}
            </div>
            <div style="font-weight: bold; color: var(--primary-color); margin-top: 5px;">
                ${pizza.price.toFixed(2)}€
            </div>
        </div>
    `).join('');
    document.getElementById('track-pizzas').innerHTML = pizzasHtml;

    // Timestamps
    document.getElementById('track-created').textContent = formatDateTime(order.created_at);

    if (order.started_at) {
        document.getElementById('track-started-row').classList.remove('hidden');
        document.getElementById('track-started').textContent = formatDateTime(order.started_at);
    }

    if (order.ready_at) {
        document.getElementById('track-ready-row').classList.remove('hidden');
        document.getElementById('track-ready').textContent = formatDateTime(order.ready_at);
    }

    if (order.delivered_at) {
        document.getElementById('track-delivered-row').classList.remove('hidden');
        document.getElementById('track-delivered').textContent = formatDateTime(order.delivered_at);
    }
}

// Show tracking error
function showTrackingError(message) {
    trackingError.classList.remove('hidden');
    document.getElementById('tracking-error-msg').textContent = message;
}

// Switch tabs
function switchTab(tabName) {
    navBtns.forEach(btn => btn.classList.remove('active'));
    tabContents.forEach(tab => tab.classList.add('hidden'));

    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(tabName).classList.remove('hidden');
}

// Show alert
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${type}`;
    alertEl.textContent = message;
    alertContainer.appendChild(alertEl);

    setTimeout(() => {
        alertEl.remove();
    }, 5000);
}

// Format date time
function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('fr-FR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}
