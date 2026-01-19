// script.js
const API_BASE_URL = 'http://localhost:5000/api'; // Flask backend

// ---------- MODALS ----------
function openModal(modalId) {
    document.getElementById(modalId).classList.remove("hidden");
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add("hidden");
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modals = document.getElementsByClassName('modal');
    for (let modal of modals) {
        if (event.target === modal) {
            modal.classList.add("hidden");
        }
    }
};

// ---------- API HELPER ----------
async function apiRequest(url, method = 'GET', data = null) {
    const config = {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include' // allow Flask session cookies
    };

    if (data) config.body = JSON.stringify(data);

    try {
        const response = await fetch(API_BASE_URL + url, config);
        const result = await response.json();
        if (!response.ok) throw new Error(result.message || 'Error');
        return result;
    } catch (err) {
        console.error('API Error:', err);
        throw err;
    }
}

// ---------- BOOKING ----------
const bookingForm = document.getElementById("bookingForm");
if (bookingForm) {
    bookingForm.addEventListener("submit", async e => {
        e.preventDefault();
        const formData = {
            serviceType: document.getElementById('serviceType').value,
            items: parseInt(document.getElementById('items').value),
            expressService: document.getElementById('express').value === 'true',
            pickupDate: document.getElementById('pickupDate').value,
            pickupTime: document.getElementById('pickupTime').value,
            address: document.getElementById('address').value,
            phone: document.getElementById('phone').value,
            paymentMethod: document.getElementById('payment').value
        };

        try {
            const res = await apiRequest('/bookings', 'POST', formData);
            showNotification(`Order booked! ID: ${res.orderId}`, 'success');
            bookingForm.reset();
        } catch (err) {
            showNotification('Booking failed: ' + err.message, 'error');
        }
    });
}

// ---------- TRACK ORDER ----------
async function trackOrder() {
    const orderId = document.getElementById('orderId').value;
    if (!orderId) return showNotification("Enter order ID", "error");

    try {
        const res = await apiRequest(`/bookings/${orderId}`);
        updateOrderStatus(res.status);
        updateOrderDetails(res);
        document.getElementById('orderStatus').style.display = 'block';
    } catch (err) {
        showNotification("Tracking failed: " + err.message, "error");
        document.getElementById('orderStatus').style.display = 'none';
    }
}

function updateOrderStatus(status) {
    const steps = document.querySelectorAll('.step');
    steps.forEach(s => s.classList.remove('active'));

    if (status === 'PICKED_UP') document.getElementById('step1').classList.add('active');
    if (status === 'IN_PROCESS') ['step1','step2'].forEach(id => document.getElementById(id).classList.add('active'));
    if (status === 'OUT_FOR_DELIVERY') ['step1','step2','step3'].forEach(id => document.getElementById(id).classList.add('active'));
    if (status === 'DELIVERED') steps.forEach(s => s.classList.add('active'));
}

function updateOrderDetails(order) {
    document.getElementById('orderDetails').innerHTML = `
        <div>
            <strong>Order ID:</strong> ${order.orderId}<br>
            <strong>Service:</strong> ${order.serviceType}<br>
            <strong>Items:</strong> ${order.items}<br>
            <strong>Pickup Date:</strong> ${order.pickupDate}<br>
            <strong>Status:</strong> ${order.status}
        </div>
    `;
}

// ---------- LOGIN ----------
const loginForm = document.getElementById("loginForm");
if (loginForm) {
    loginForm.addEventListener("submit", async e => {
        e.preventDefault();
        const data = {
            email: document.getElementById("loginEmail").value,
            password: document.getElementById("loginPassword").value
        };

        try {
            const res = await apiRequest('/auth/login', 'POST', data);
            localStorage.setItem("user", JSON.stringify(res.user));
            updateAuthButtons(true);
            closeModal('loginModal');
            showNotification("Login successful", "success");
        } catch (err) {
            showNotification("Login failed: " + err.message, "error");
        }
    });
}

// ---------- SIGNUP ----------
const signupForm = document.getElementById("signupForm");
if (signupForm) {
    signupForm.addEventListener("submit", async e => {
        e.preventDefault();
        const data = {
            name: document.getElementById("signupName").value,
            email: document.getElementById("signupEmail").value,
            phone: document.getElementById("signupPhone").value,
            password: document.getElementById("signupPassword").value
        };

        try {
            const res = await apiRequest('/auth/register', 'POST', data);
            localStorage.setItem("user", JSON.stringify(res.user));
            updateAuthButtons(true);
            closeModal('signupModal');
            showNotification("Account created successfully", "success");
        } catch (err) {
            showNotification("Signup failed: " + err.message, "error");
        }
    });
}

// ---------- AUTH BUTTONS ----------
function updateAuthButtons(isLoggedIn) {
    const authButtons = document.querySelector('.auth-buttons');
    if (!authButtons) return;

    if (isLoggedIn) {
        const user = JSON.parse(localStorage.getItem("user"));
        authButtons.innerHTML = `
            <span>Welcome, ${user.name}</span>
            <button onclick="logout()">Logout</button>
        `;
    } else {
        authButtons.innerHTML = `
            <a href="#" onclick="openModal('loginModal')">Login</a>
            <a href="#" onclick="openModal('signupModal')">Sign Up</a>
        `;
    }
}

function logout() {
    localStorage.removeItem("user");
    updateAuthButtons(false);
    showNotification("Logged out", "success");
}

// ---------- NOTIFICATION ----------
function showNotification(message, type = "success") {
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// ---------- INIT ----------
document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("user")) {
        updateAuthButtons(true);
    } else {
        updateAuthButtons(false);
    }
});
