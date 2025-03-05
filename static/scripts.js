// Store the token in localStorage
let token = localStorage.getItem('token');
let isAdmin = false;

// API Base URL
const API_BASE_URL = 'https://key-db.onrender.com';

// Utility function to make API requests
async function makeRequest(endpoint, method = 'GET', body = null, auth = true, customHeaders = {}) {
    const headers = {};
    if (auth && token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    // Merge custom headers (e.g., Content-Type) with default headers
    Object.assign(headers, customHeaders);

    const config = {
        method,
        headers,
    };
    if (body) {
        config.body = body; // Let the caller handle body serialization
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    if (!response.ok) {
        const errorData = await response.json();
        // Handle FastAPI error responses with a "detail" field
        if (errorData.detail) {
            if (Array.isArray(errorData.detail)) {
                // If detail is an array (e.g., validation errors), join the messages
                throw new Error(errorData.detail.map(err => err.msg).join(', '));
            } else {
                throw new Error(errorData.detail);
            }
        }
        throw new Error(response.statusText);
    }
    return response.json();
}

// Show/hide sections based on login status
function updateUI() {
    const loginSection = document.getElementById('login-section');
    const createKeySection = document.getElementById('create-key-section');
    const validateKeySection = document.getElementById('validate-key-section');
    const manageKeysSection = document.getElementById('manage-keys-section');
    const logoutBtn = document.getElementById('logout-btn');

    if (token) {
        loginSection.style.display = 'none';
        validateKeySection.style.display = 'block';
        logoutBtn.style.display = 'block';
        if (isAdmin) {
            createKeySection.style.display = 'block';
            manageKeysSection.style.display = 'block';
            loadKeys();
        }
    } else {
        loginSection.style.display = 'block';
        createKeySection.style.display = 'none';
        validateKeySection.style.display = 'none';
        manageKeysSection.style.display = 'none';
        logoutBtn.style.display = 'none';
    }
}

// Load keys for the admin table
async function loadKeys() {
    try {
        const keys = await makeRequest('/api/keys/');
        const tableBody = document.getElementById('keys-table-body');
        tableBody.innerHTML = '';
        keys.forEach(key => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${key.key}</td>
                <td>${key.created_at}</td>
                <td>${key.expires_at || 'N/A'}</td>
                <td>${key.max_uses || 'Unlimited'}</td>
                <td>${key.current_uses}</td>
                <td>${key.hwid || 'N/A'}</td>
                <td>
                    <button class="action-btn" onclick="blacklistKey('${key.key}')">Blacklist</button>
                    <button class="action-btn" onclick="removeFromBlacklist('${key.key}')">Unblacklist</button>
                    <button class="action-btn" onclick="resetHWID('${key.key}')">Reset HWID</button>
                    <button class="action-btn delete-btn" onclick="deleteKey('${key.key}')">Delete</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading keys:', error.message);
    }
}

// Login form submission
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const message = document.getElementById('login-message');

    try {
        const data = await makeRequest('/token/non-expiring', 'POST', `username=${username}&password=${password}`, false, {
            'Content-Type': 'application/x-www-form-urlencoded'
        });
        token = data.access_token;
        localStorage.setItem('token', token);

        // Check if the user is an admin by attempting to access /api/keys/
        try {
            await makeRequest('/api/keys/');
            isAdmin = true;
        } catch (error) {
            if (error.message.includes('Not authorized')) {
                isAdmin = false;
            } else {
                throw error;
            }
        }

        message.textContent = 'Login successful!';
        message.style.color = 'green';
        updateUI();
    } catch (error) {
        message.textContent = `Login failed: ${error.message}`;
        message.style.color = 'red';
    }
});

// Create key form submission
document.getElementById('create-key-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const maxUses = document.getElementById('max_uses').value;
    const expiresAt = document.getElementById('expires_at').value;
    const message = document.getElementById('create-key-message');

    try {
        const data = await makeRequest('/api/keys/', 'POST', {
            max_uses: parseInt(maxUses),
            expires_at: expiresAt
        }, true, {
            'Content-Type': 'application/json'
        });
        message.textContent = `Key created: ${data.key}`;
        message.style.color = 'green';
        loadKeys();
    } catch (error) {
        message.textContent = `Error creating key: ${error.message}`;
        message.style.color = 'red';
    }
});

// Validate key form submission
document.getElementById('validate-key-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const key = document.getElementById('validate-key').value;
    const hwid = document.getElementById('hwid').value;
    const message = document.getElementById('validate-key-message');

    try {
        const data = await makeRequest('/api/keys/validate', 'POST', { key, hwid }, false, {
            'Content-Type': 'application/json'
        });
        message.textContent = data.message;
        message.style.color = 'green';
        if (isAdmin) loadKeys();
    } catch (error) {
        message.textContent = `Error validating key: ${error.message}`;
        message.style.color = 'red';
    }
});

// Blacklist a key
async function blacklistKey(key) {
    try {
        const data = await makeRequest('/blacklist/', 'POST', { key, reason: 'Blacklisted via UI' }, true, {
            'Content-Type': 'application/json'
        });
        alert(`Key blacklisted: ${key}`);
        loadKeys();
    } catch (error) {
        alert(`Error blacklisting key: ${error.message}`);
    }
}

// Remove from blacklist
async function removeFromBlacklist(key) {
    try {
        const data = await makeRequest('/blacklist/', 'DELETE', { key }, true, {
            'Content-Type': 'application/json'
        });
        alert(`Key removed from blacklist: ${key}`);
        loadKeys();
    } catch (error) {
        alert(`Error removing from blacklist: ${error.message}`);
    }
}

// Reset HWID
async function resetHWID(key) {
    try {
        const data = await makeRequest(`/api/keys/${key}/reset-hwid`, 'POST', null, true);
        alert(`HWID reset for key: ${key}`);
        loadKeys();
    } catch (error) {
        alert(`Error resetting HWID: ${error.message}`);
    }
}

// Delete a key
async function deleteKey(key) {
    if (confirm(`Are you sure you want to delete key: ${key}?`)) {
        try {
            const data = await makeRequest(`/api/keys/${key}`, 'DELETE', null, true);
            alert(`Key deleted: ${key}`);
            loadKeys();
        } catch (error) {
            alert(`Error deleting key: ${error.message}`);
        }
    }
}

// Logout functionality
document.getElementById('logout-btn').addEventListener('click', () => {
    token = null;
    isAdmin = false;
    localStorage.removeItem('token');
    updateUI();
    document.getElementById('login-message').textContent = 'Logged out.';
});

// Initialize UI on page load
updateUI();