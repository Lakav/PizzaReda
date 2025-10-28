// Configuration
const API_BASE = '/';
let currentStatus = 'pending';
let allOrders = {};

// Mapping des statuts
const statusMap = {
    'pending': 'En attente',
    'preparing': 'En préparation',
    'ready_for_delivery': 'Prête pour livraison',
    'in_delivery': 'En cours de livraison',
    'delivered': 'Livrée',
    'cancelled': 'Annulée'
};

const nextStatus = {
    'pending': 'start',
    'preparing': 'ready',
    'ready_for_delivery': 'deliver',
    'in_delivery': 'delivered'
};

// DOM Elements
const ordersContainer = document.getElementById('orders-container');
const noOrdersMsg = document.getElementById('no-orders');
const totalOrdersEl = document.getElementById('total-orders');
const refreshBtn = document.getElementById('refresh-btn');
const navBtns = document.querySelectorAll('.nav-btn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadOrders();
    // Auto-refresh every 5 seconds
    setInterval(loadOrders, 5000);
});

// Setup event listeners
function setupEventListeners() {
    refreshBtn.addEventListener('click', loadOrders);

    navBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const status = e.currentTarget.dataset.status;
            switchStatus(status);
        });
    });
}

// Load all orders
async function loadOrders() {
    try {
        const response = await fetch(API_BASE + 'admin/orders');
        if (!response.ok) throw new Error('Erreur lors du chargement des commandes');

        const data = await response.json();
        allOrders = data.orders_by_status;

        updateCounts();
        displayOrders();

    } catch (error) {
        showAlert('Erreur: ' + error.message, 'error');
        console.error(error);
    }
}

// Update status counts
function updateCounts() {
    totalOrdersEl.textContent = Object.values(allOrders).flat().length;

    document.querySelectorAll('.status-count').forEach(el => {
        const status = el.dataset.status;
        const count = allOrders[status] ? allOrders[status].length : 0;
        el.textContent = count;
    });
}

// Display orders for current status
function displayOrders() {
    const orders = allOrders[currentStatus] || [];

    if (orders.length === 0) {
        ordersContainer.innerHTML = '';
        noOrdersMsg.classList.remove('hidden');
        return;
    }

    noOrdersMsg.classList.add('hidden');
    ordersContainer.innerHTML = '';

    orders.forEach(order => {
        const orderEl = createOrderElement(order);
        ordersContainer.appendChild(orderEl);
    });
}

// Create order card element
function createOrderElement(order) {
    const card = document.createElement('div');
    card.className = 'order-card';

    const statusBadgeClass = order.status.replace('_', '-');
    const pizzasHtml = order.pizzas.map(pizza => `
        <div style="margin: 10px 0; padding: 10px; background: var(--light-bg); border-radius: 4px;">
            <div style="font-weight: bold;">${pizza.name}</div>
            <div style="font-size: 0.9em; color: #666;">
                ${pizza.size.toUpperCase()} - Toppings: ${pizza.toppings.join(', ')}
            </div>
            <div style="font-weight: bold; color: var(--primary-color);">${pizza.price.toFixed(2)}€</div>
        </div>
    `).join('');

    const nextStatusKey = nextStatus[order.status];
    let actionButtons = '';

    if (nextStatusKey) {
        const statusLabels = {
            'start': 'Commencer la préparation',
            'ready': 'Marquer prête',
            'deliver': 'Envoyer en livraison',
            'delivered': 'Confirmer livraison'
        };

        actionButtons = `
            <button type="button" class="btn btn-success" onclick="updateOrderStatus(${order.order_id}, '${nextStatusKey}')">
                ✓ ${statusLabels[nextStatusKey]}
            </button>
        `;
    }

    if (order.status === 'delivered') {
        actionButtons += `
            <button type="button" class="btn btn-info" onclick="viewOrderDetails(${order.order_id})">
                👁️ Voir détails
            </button>
        `;
    }

    card.innerHTML = `
        <div class="order-header">
            <div>
                <div class="order-id">Commande #${order.order_id}</div>
                <div class="order-customer">👤 ${order.customer_name}</div>
            </div>
            <span class="badge badge-${statusBadgeClass}">${statusMap[order.status]}</span>
        </div>

        <div class="order-details">
            <div class="detail-item">
                <div class="detail-label">Adresse</div>
                <div class="detail-value">${order.customer_address}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Total</div>
                <div class="detail-value">${order.total.toFixed(2)}€</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Temps estimé</div>
                <div class="detail-value">${order.estimated_delivery_minutes} min</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Créée à</div>
                <div class="detail-value" style="font-size: 0.9em;">${formatTime(order.created_at)}</div>
            </div>
        </div>

        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border-color);">
            <div style="font-weight: bold; margin-bottom: 10px;">Pizzas:</div>
            ${pizzasHtml}
        </div>

        <div class="order-actions">
            ${actionButtons}
        </div>
    `;

    return card;
}

// Update order status
async function updateOrderStatus(orderId, action) {
    const statusActions = {
        'start': 'start',
        'ready': 'ready',
        'deliver': 'deliver',
        'delivered': 'delivered'
    };

    const endpoint = statusActions[action];

    try {
        const response = await fetch(`${API_BASE}admin/orders/${orderId}/${endpoint}`, {
            method: 'POST'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }

        showAlert('Commande mise à jour avec succès', 'success');
        await loadOrders();

    } catch (error) {
        showAlert('Erreur: ' + error.message, 'error');
    }
}

// Switch status filter
function switchStatus(status) {
    currentStatus = status;

    navBtns.forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-status="${status}"]`).classList.add('active');

    displayOrders();
}

// View order details
function viewOrderDetails(orderId) {
    // This could open a modal or detailed view
    alert(`Détails de la commande #${orderId}`);
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
    }, 4000);
}

// Format time
function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('fr-FR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}
