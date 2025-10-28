// Configuration
const API_BASE = '/';
let cart = [];
let menu = [];
let allToppings = [];
let selectedPizzaIndex = null; // Index de la pizza actuellement sélectionnée
let pizzasToppings = {}; // Objet pour tracker les toppings de chaque pizza {index: [topping1, topping2]}
let currentToppingPizzaIndex = null; // Index de la pizza en cours de modification des toppings

// DOM Elements
const navBtns = document.querySelectorAll('.nav-btn');
const menuContainer = document.getElementById('menu-container');
const customerForm = document.getElementById('customer-form');
const submitOrderBtn = document.getElementById('submit-order');
const trackBtn = document.getElementById('track-btn');
const trackingInput = document.getElementById('tracking-id');
const trackingResult = document.getElementById('tracking-result');
const trackingError = document.getElementById('tracking-error');
const floatingCart = document.getElementById('floating-cart');
const floatingCartItems = document.getElementById('floating-cart-items');
const cartCount = document.getElementById('cart-count');

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadToppings(); // Load toppings FIRST
    await loadMenu();     // Then load menu with toppings available
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
        pizzasToppings = {}; // Réinitialiser les toppings
        renderMenu();
    } catch (error) {
        showAlert('Erreur lors du chargement du menu: ' + error.message, 'error');
        console.error(error);
    }
}

// Load toppings
async function loadToppings() {
    try {
        const response = await fetch(API_BASE + 'topping/menu');
        if (!response.ok) throw new Error('Erreur lors du chargement des toppings');

        allToppings = await response.json();
    } catch (error) {
        console.error('Erreur chargement toppings:', error);
    }
}

// Render pizza menu
function renderMenu() {
    menuContainer.innerHTML = '';
    menu.forEach((pizza, pizzaIndex) => {
        const pizzaEl = document.createElement('div');
        pizzaEl.className = 'pizza-item';
        pizzaEl.id = `pizza-${pizzaIndex}`;

        // Initialiser les toppings pour cette pizza
        if (!pizzasToppings[pizzaIndex]) {
            pizzasToppings[pizzaIndex] = [];
        }

        pizzaEl.innerHTML = `
            <div class="pizza-header">
                <div class="pizza-name">${pizza.name}</div>
                <div class="pizza-toppings-base">
                    <strong>Inclus:</strong> ${pizza.base_toppings.join(', ')}
                </div>
            </div>

            <div class="pizza-selected-toppings" id="selected-toppings-${pizzaIndex}">
                ${pizzasToppings[pizzaIndex].length > 0 ?
                    `<div class="toppings-label">✨ Toppings sélectionnés:</div>
                     <div class="toppings-chips">${pizzasToppings[pizzaIndex].map(t => `<span class="chip">${t}</span>`).join('')}</div>`
                    : ''}
            </div>

            <div class="pizza-actions">
                <button type="button" class="btn btn-secondary btn-small" onclick="openToppingModal(${pizzaIndex})">
                    🍕 Ajouter toppings
                </button>
            </div>

            <div class="pizza-sizes">
                <button type="button" class="size-btn" data-pizza-index="${pizzaIndex}" data-size="small" data-price="${pizza.prices.small}">
                    S: ${pizza.prices.small}€
                </button>
                <button type="button" class="size-btn" data-pizza-index="${pizzaIndex}" data-size="medium" data-price="${pizza.prices.medium}">
                    M: ${pizza.prices.medium}€
                </button>
                <button type="button" class="size-btn" data-pizza-index="${pizzaIndex}" data-size="large" data-price="${pizza.prices.large}">
                    L: ${pizza.prices.large}€
                </button>
            </div>
        `;

        menuContainer.appendChild(pizzaEl);

        // Setup size buttons
        const sizeButtons = pizzaEl.querySelectorAll('.size-btn');
        sizeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const pizzaIdx = parseInt(btn.dataset.pizzaIndex);
                const size = btn.dataset.size;
                const price = parseFloat(btn.dataset.price);
                const selectedToppings = pizzasToppings[pizzaIdx] || [];

                addToCart(pizza.name, size, price, pizza.base_toppings, selectedToppings);
            });
        });
    });
}

// Update pizza toppings display
function updatePizzaToppings(pizzaIndex) {
    const checked = Array.from(
        document.querySelectorAll(`#toppings-${pizzaIndex} input[type="checkbox"]:checked`)
    ).map(cb => cb.value);

    pizzasToppings[pizzaIndex] = checked;

    // Update visual display
    const selectedDisplay = document.getElementById(`selected-toppings-${pizzaIndex}`);
    if (checked.length > 0) {
        selectedDisplay.innerHTML = `
            <div class="toppings-label">Toppings ajoutés:</div>
            <div class="toppings-chips">${checked.map(t => `<span class="chip">${t}</span>`).join('')}</div>
        `;
    } else {
        selectedDisplay.innerHTML = '';
    }
}

// Add to cart
function addToCart(name, size, price, baseToppings, selectedExtraToppings) {
    // Calculer le prix avec les toppings supplémentaires
    const extraPrice = selectedExtraToppings.reduce((sum, topping) => {
        const toppingObj = allToppings.find(t => t.name === topping);
        return sum + (toppingObj ? toppingObj.price : 0);
    }, 0);

    const finalPrice = price + extraPrice;

    cart.push({
        name: name,
        size: size,
        price: finalPrice,
        toppings: [...baseToppings, ...selectedExtraToppings]
    });

    updateCart();
    showAlert(`${name} (${size.toUpperCase()}) ajoutée au panier avec ${selectedExtraToppings.length} topping(s)`, 'success');
}

// Update cart display
function updateCart() {
    // Update floating cart
    floatingCartItems.innerHTML = '';
    cartCount.textContent = cart.length;

    if (cart.length === 0) {
        floatingCartItems.innerHTML = '<p style="color: #999; text-align: center; padding: 10px;">Vide</p>';
    } else {
        cart.forEach((item, index) => {
            const itemEl = document.createElement('div');
            itemEl.className = 'floating-cart-item';
            itemEl.innerHTML = `
                <div style="flex: 1;">
                    <div>${item.name} (${item.size[0].toUpperCase()})</div>
                    <small style="color: #999;">${item.toppings.join(', ')}</small>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <span class="floating-cart-item-price">${item.price.toFixed(2)}€</span>
                    <button onclick="removeFromCart(${index})" style="background: none; border: none; color: #e74c3c; cursor: pointer; font-size: 18px; padding: 0;">×</button>
                </div>
            `;
            floatingCartItems.appendChild(itemEl);
        });
    }

    // Update totals
    const subtotal = cart.reduce((sum, item) => sum + item.price, 0);
    const deliveryFee = subtotal >= 30 ? 0 : 5;
    const total = subtotal + deliveryFee;

    document.getElementById('floating-subtotal').textContent = subtotal.toFixed(2) + '€';
    document.getElementById('floating-delivery').textContent = (deliveryFee === 0 ? 'GRATUIT ✓' : deliveryFee.toFixed(2) + '€');
    document.getElementById('floating-total').textContent = total.toFixed(2) + '€';
}

// Remove from cart
function removeFromCart(index) {
    const item = cart[index];
    cart.splice(index, 1);
    updateCart();
    showAlert(`${item.name} supprimée du panier`, 'info');
}

// Place order
async function placeOrder(e) {
    if (e) e.preventDefault();

    if (cart.length === 0) {
        showAlert('Veuillez sélectionner au moins une pizza', 'error');
        return;
    }

    const customerName = document.getElementById('customer-name').value;
    const streetNumber = document.getElementById('street-number').value;
    const streetName = document.getElementById('street-name').value;
    const postalCode = document.getElementById('postal-code').value;
    const city = document.getElementById('city').value;

    if (!customerName || !streetNumber || !streetName) {
        showAlert('Veuillez remplir tous les champs obligatoires', 'error');
        return;
    }

    const pizzas = cart.map(item => ({
        name: item.name,
        size: item.size,
        toppings: item.toppings
    }));

    const orderData = {
        pizzas: pizzas,
        customer_name: customerName,
        customer_address: {
            street_number: streetNumber,
            street: streetName,
            city: city,
            postal_code: postalCode
        }
    };

    try {
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
        showAlert(`✓ Commande créée ! Numéro: #${result.order_id}`, 'success');

        // Clear form and cart
        cart = [];
        pizzasToppings = {};
        updateCart();
        customerForm.reset();

        // Redirect to tracking after 2 seconds
        setTimeout(() => {
            switchTab('tracking-tab');
            document.getElementById('tracking-id').value = result.order_id;
            trackOrder();
        }, 2000);

    } catch (error) {
        showAlert('Erreur: ' + error.message, 'error');
        console.error(error);
    }
}

// Track order
async function trackOrder() {
    const orderId = parseInt(document.getElementById('tracking-id').value);

    if (!orderId) {
        showAlert('Veuillez entrer un numéro de commande', 'error');
        return;
    }

    try {
        const response = await fetch(API_BASE + `orders/${orderId}/status`);

        if (!response.ok) {
            throw new Error('Commande non trouvée');
        }

        const order = await response.json();
        displayOrderStatus(order);

    } catch (error) {
        document.getElementById('tracking-result').classList.add('hidden');
        document.getElementById('tracking-error').classList.remove('hidden');
        document.getElementById('tracking-error-msg').textContent = error.message;
    }
}

// Display order status
function displayOrderStatus(order) {
    document.getElementById('tracking-error').classList.add('hidden');
    document.getElementById('tracking-result').classList.remove('hidden');

    document.getElementById('track-order-id').textContent = order.order_id;
    document.getElementById('track-customer-name').textContent = order.customer_name;
    document.getElementById('track-address').textContent = order.customer_address;
    document.getElementById('track-subtotal').textContent = order.subtotal + '€';
    document.getElementById('track-delivery-fee').textContent = (order.delivery_fee === 0 ? 'GRATUIT ✓' : order.delivery_fee + '€');
    document.getElementById('track-total').textContent = order.total + '€';
    document.getElementById('track-time').textContent = order.estimated_delivery_minutes + ' min environ';
    document.getElementById('track-progress').style.width = order.progress_percent + '%';
    document.getElementById('track-status-label').textContent = order.status_label;

    // Status badge
    const badge = document.getElementById('track-status-badge');
    const statusColor = {
        'pending': '#f39c12',
        'preparing': '#e67e22',
        'ready_for_delivery': '#3498db',
        'in_delivery': '#e74c3c',
        'delivered': '#27ae60',
        'cancelled': '#95a5a6'
    };
    badge.style.backgroundColor = statusColor[order.status] || '#999';
    badge.textContent = order.status_label;

    // Pizzas
    const pizzasEl = document.getElementById('track-pizzas');
    pizzasEl.innerHTML = order.pizzas.map(p => `
        <div style="padding: 8px 0; border-bottom: 1px solid var(--border-color);">
            <strong>${p.name}</strong> (${p.size})
            ${p.toppings.length > 0 ? `<div style="font-size: 0.9em; color: #666;">Toppings: ${p.toppings.join(', ')}</div>` : ''}
            <div style="color: var(--primary-color); font-weight: bold;">${p.price}€</div>
        </div>
    `).join('');

    // Timestamps
    document.getElementById('track-created').textContent = new Date(order.created_at).toLocaleString('fr-FR');

    if (order.started_at) {
        document.getElementById('track-started-row').classList.remove('hidden');
        document.getElementById('track-started').textContent = new Date(order.started_at).toLocaleString('fr-FR');
    }
    if (order.ready_at) {
        document.getElementById('track-ready-row').classList.remove('hidden');
        document.getElementById('track-ready').textContent = new Date(order.ready_at).toLocaleString('fr-FR');
    }
    if (order.delivered_at) {
        document.getElementById('track-delivered-row').classList.remove('hidden');
        document.getElementById('track-delivered').textContent = new Date(order.delivered_at).toLocaleString('fr-FR');
    }
}

// Switch tab
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });

    // Remove active from all buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.remove('hidden');

    // Activate button
    document.querySelector(`.nav-btn[data-tab="${tabName}"]`).classList.add('active');
}

// Show alert
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alertContainer.appendChild(alert);

    setTimeout(() => {
        alert.remove();
    }, 4000);
}

// Open topping modal for a specific pizza
function openToppingModal(pizzaIndex) {
    currentToppingPizzaIndex = pizzaIndex;
    const pizza = menu[pizzaIndex];

    // Set modal title
    document.getElementById('modal-pizza-name').textContent = pizza.name;

    // Populate toppings grid
    const toppingGrid = document.getElementById('toppings-modal-grid');
    toppingGrid.innerHTML = '';

    allToppings.forEach(topping => {
        const div = document.createElement('div');
        div.className = 'topping-option';
        div.innerHTML = `
            <input type="checkbox" id="modal-topping-${topping.name}"
                   value="${topping.name}" data-price="${topping.price}"
                   ${pizzasToppings[pizzaIndex].includes(topping.name) ? 'checked' : ''}>
            <label for="modal-topping-${topping.name}" style="margin: 0; cursor: pointer;">
                ${topping.name} (+${topping.price}€)
            </label>
        `;

        div.addEventListener('click', () => {
            const checkbox = div.querySelector('input[type="checkbox"]');
            checkbox.checked = !checkbox.checked;
        });

        toppingGrid.appendChild(div);
    });

    // Show modal
    document.getElementById('toppings-modal').classList.remove('hidden');
}

// Close topping modal
function closeToppingModal() {
    document.getElementById('toppings-modal').classList.add('hidden');
    currentToppingPizzaIndex = null;
}

// Confirm topping selection
function confirmToppingSelection() {
    if (currentToppingPizzaIndex === null) {
        showAlert('Erreur: aucune pizza sélectionnée', 'error');
        return;
    }

    // Get selected toppings from modal
    const checked = Array.from(
        document.querySelectorAll('#toppings-modal-grid input[type="checkbox"]:checked')
    ).map(cb => cb.value);

    // Update the pizza's toppings
    pizzasToppings[currentToppingPizzaIndex] = checked;

    // Update the pizza card's display
    const selectedDisplay = document.getElementById(`selected-toppings-${currentToppingPizzaIndex}`);
    if (checked.length > 0) {
        selectedDisplay.innerHTML = `
            <div class="toppings-label">✨ Toppings sélectionnés:</div>
            <div class="toppings-chips">${checked.map(t => `<span class="chip">${t}</span>`).join('')}</div>
        `;
    } else {
        selectedDisplay.innerHTML = '';
    }

    // Close modal and show success message
    closeToppingModal();
    showAlert(`✓ Toppings ajoutés à ${menu[currentToppingPizzaIndex].name}`, 'success');
}
