// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const API_AUTH_URL = `${API_BASE_URL}/auth`;

// State
let currentUser = null;
let accessToken = null;
let refreshToken = null;
let currentPage = 1;
let totalPages = 1;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Приложение загружено');
    console.log('API URL:', API_AUTH_URL);
    loadTokensFromStorage();
    console.log('Access token:', accessToken ? 'Присутствует' : 'Отсутствует');
    console.log('Refresh token:', refreshToken ? 'Присутствует' : 'Отсутствует');

    if (accessToken) {
        console.log('Найдены токены, загрузка пользователя...');
        loadCurrentUser();
    } else {
        console.log('Токены не найдены, показываем экран авторизации');
        showAuthScreen();
    }
});

// Auth Functions
function showLoginForm() {
    document.getElementById('login-form').classList.remove('hidden');
    document.getElementById('register-form').classList.add('hidden');
}

function showRegisterForm() {
    document.getElementById('register-form').classList.remove('hidden');
    document.getElementById('login-form').classList.add('hidden');
}

async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        console.log('Попытка входа:', email);
        const response = await fetch(`${API_AUTH_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            const error = await response.json();
            console.error('Ошибка входа:', error);
            throw new Error(error.detail || 'Ошибка входа');
        }

        const data = await response.json();
        accessToken = data.access_token;
        refreshToken = data.refresh_token;

        console.log('Вход успешен, токены получены');
        saveTokensToStorage();
        await loadCurrentUser();

        showToast('Успешный вход!', 'success');
        event.target.reset();
    } catch (error) {
        console.error('Ошибка при входе:', error);
        showToast(error.message, 'error');
    }
}

async function handleRegister(event) {
    event.preventDefault();

    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await fetch(`${API_AUTH_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка регистрации');
        }

        showToast('Регистрация успешна! Теперь войдите', 'success');
        showLoginForm();
        event.target.reset();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function loadCurrentUser() {
    try {
        console.log('Загрузка пользователя...');
        const response = await fetchWithAuth(`${API_AUTH_URL}/users/me`);

        if (!response.ok) {
            console.error('Ошибка ответа:', response.status, response.statusText);
            if (response.status === 401 || response.status === 403) {
                // Try to refresh token
                console.log('Попытка обновления токена...');
                const refreshed = await tryRefreshToken();
                if (refreshed) {
                    console.log('Токен обновлен, повторная загрузка пользователя');
                    return loadCurrentUser();
                }
                console.log('Не удалось обновить токен');
                throw new Error('Сессия истекла');
            }
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Ошибка загрузки профиля');
        }

        currentUser = await response.json();
        console.log('Пользователь загружен:', currentUser.email);
        showProfileScreen();
        updateUIForUser();
    } catch (error) {
        console.error('Ошибка при загрузке пользователя:', error);
        showToast(error.message, 'error');
        logout();
    }
}

async function tryRefreshToken() {
    if (!refreshToken) {
        console.log('Refresh token отсутствует');
        return false;
    }

    try {
        console.log('Отправка запроса на обновление токена...');
        const response = await fetch(`${API_AUTH_URL}/refresh`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${refreshToken}`,
            },
        });

        if (!response.ok) {
            console.error('Не удалось обновить токен:', response.status);
            return false;
        }

        const data = await response.json();
        accessToken = data.access_token;
        refreshToken = data.refresh_token;
        saveTokensToStorage();
        console.log('Токен успешно обновлен');
        return true;
    } catch (error) {
        console.error('Ошибка при обновлении токена:', error);
        return false;
    }
}

function logout() {
    currentUser = null;
    accessToken = null;
    refreshToken = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    showAuthScreen();
}

// Token storage
function saveTokensToStorage() {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
}

function loadTokensFromStorage() {
    accessToken = localStorage.getItem('accessToken');
    refreshToken = localStorage.getItem('refreshToken');
}

// Fetch with auth
async function fetchWithAuth(url, options = {}) {
    return fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${accessToken}`,
        },
    });
}

// Screen management
function showAuthScreen() {
    hideAllScreens();
    document.getElementById('auth-screen').classList.remove('hidden');
    document.getElementById('navbar').classList.add('hidden');
}

function showProfileScreen() {
    hideAllScreens();
    document.getElementById('profile-screen').classList.remove('hidden');
    document.getElementById('navbar').classList.remove('hidden');
    renderProfile();
}

function showUsersScreen() {
    hideAllScreens();
    document.getElementById('users-screen').classList.remove('hidden');
    document.getElementById('navbar').classList.remove('hidden');
    loadUsers();
}

function hideAllScreens() {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.add('hidden');
    });
}

// UI Updates
function updateUIForUser() {
    const adminElements = document.querySelectorAll('.admin-only');
    if (currentUser && currentUser.role === 'admin') {
        adminElements.forEach(el => el.classList.remove('hidden'));
    } else {
        adminElements.forEach(el => el.classList.add('hidden'));
    }
}

function renderProfile() {
    if (!currentUser) return;

    const profileInfo = document.getElementById('profile-info');
    profileInfo.innerHTML = `
        <p><strong>ID:</strong> <span>${currentUser.id}</span></p>
        <p><strong>Имя пользователя:</strong> <span>${currentUser.username}</span></p>
        <p><strong>Email:</strong> <span>${currentUser.email}</span></p>
        <p><strong>Роль:</strong> <span class="badge badge-${currentUser.role}">${currentUser.role}</span></p>
        <p><strong>Статус:</strong> <span class="badge ${currentUser.is_active ? 'badge-active' : 'badge-inactive'}">${currentUser.is_active ? 'Активен' : 'Неактивен'}</span></p>
        <p><strong>Дата создания:</strong> <span>${new Date(currentUser.created_at).toLocaleString('ru-RU')}</span></p>
    `;
}

// Profile actions
function showMyProfile() {
    showProfileScreen();
}

function showChangePassword() {
    document.getElementById('change-password-modal').classList.remove('hidden');
}

function hideChangePassword() {
    document.getElementById('change-password-modal').classList.add('hidden');
    document.getElementById('current-password').value = '';
    document.getElementById('new-password').value = '';
}

async function handleChangePassword(event) {
    event.preventDefault();

    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;

    try {
        const response = await fetchWithAuth(`${API_AUTH_URL}/users/password`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: currentUser.email,
                password: currentPassword,
                new_password: newPassword,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка изменения пароля');
        }

        showToast('Пароль успешно изменен', 'success');
        hideChangePassword();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Users management
async function loadUsers(page = 1) {
    if (!currentUser || currentUser.role !== 'admin') {
        showToast('Недостаточно прав', 'error');
        return;
    }

    const roleFilter = document.getElementById('role-filter').value;
    const sortBy = document.getElementById('sort-by').value;
    const sortOrder = document.getElementById('sort-order').value;

    try {
        let url = `${API_AUTH_URL}/users?page_number=${page}&page_size=10`;
        if (roleFilter) url += `&role=${roleFilter}`;
        if (sortBy) url += `&sort_by=${sortBy}`;
        if (sortOrder) url += `&sort_order=${sortOrder}`;

        const response = await fetchWithAuth(url);

        if (!response.ok) {
            throw new Error('Ошибка загрузки пользователей');
        }

        const data = await response.json();
        currentPage = page;
        totalPages = data.pages;
        renderUsersTable(data.results);
        renderPagination(data);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function renderUsersTable(users) {
    const tableContainer = document.getElementById('users-table');

    if (users.length === 0) {
        tableContainer.innerHTML = '<p style="text-align: center; padding: 2rem;">Пользователи не найдены</p>';
        return;
    }

    const table = `
        <table>
            <thead>
                <tr>
                    <th>Имя пользователя</th>
                    <th>Email</th>
                    <th>Роль</th>
                    <th>Статус</th>
                    <th>Дата создания</th>
                    <th>Действия</th>
                </tr>
            </thead>
            <tbody>
                ${users.map(user => `
                    <tr>
                        <td>${user.username}</td>
                        <td>${user.email}</td>
                        <td><span class="badge badge-${user.role}">${user.role}</span></td>
                        <td><span class="badge ${user.is_active ? 'badge-active' : 'badge-inactive'}">${user.is_active ? 'Активен' : 'Неактивен'}</span></td>
                        <td>${new Date(user.created_at).toLocaleString('ru-RU')}</td>
                        <td class="actions">
                            <button class="btn btn-small btn-secondary" onclick="editUser('${user.id}')">Изменить</button>
                            <button class="btn btn-small btn-danger" onclick="deleteUser('${user.id}')">Удалить</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    tableContainer.innerHTML = table;
}

function renderPagination(data) {
    const paginationContainer = document.getElementById('pagination');

    const buttons = [];

    // Previous button
    buttons.push(`
        <button onclick="loadUsers(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>
            ← Предыдущая
        </button>
    `);

    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            buttons.push(`
                <button onclick="loadUsers(${i})" class="${i === currentPage ? 'active' : ''}">
                    ${i}
                </button>
            `);
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            buttons.push('<button disabled>...</button>');
        }
    }

    // Next button
    buttons.push(`
        <button onclick="loadUsers(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>
            Следующая →
        </button>
    `);

    paginationContainer.innerHTML = buttons.join('');
}

function showUsers() {
    currentPage = 1;
    showUsersScreen();
}

async function editUser(userId) {
    try {
        const response = await fetchWithAuth(`${API_AUTH_URL}/users/${userId}`);

        if (!response.ok) {
            throw new Error('Ошибка загрузки пользователя');
        }

        const user = await response.json();

        document.getElementById('edit-user-id').value = user.id;
        document.getElementById('edit-username').value = user.username;
        document.getElementById('edit-email').value = user.email;
        document.getElementById('edit-role').value = user.role;
        document.getElementById('edit-is-active').checked = user.is_active;

        document.getElementById('edit-user-modal').classList.remove('hidden');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function hideEditUserModal() {
    document.getElementById('edit-user-modal').classList.add('hidden');
}

async function handleUpdateUser(event) {
    event.preventDefault();

    const userId = document.getElementById('edit-user-id').value;
    const username = document.getElementById('edit-username').value;
    const email = document.getElementById('edit-email').value;
    const role = document.getElementById('edit-role').value;
    const isActive = document.getElementById('edit-is-active').checked;

    try {
        const response = await fetchWithAuth(`${API_AUTH_URL}/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                email,
                role,
                is_active: isActive,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка обновления пользователя');
        }

        showToast('Пользователь успешно обновлен', 'success');
        hideEditUserModal();
        loadUsers(currentPage);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteUser(userId) {
    if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) {
        return;
    }

    try {
        const response = await fetchWithAuth(`${API_AUTH_URL}/users/${userId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка удаления пользователя');
        }

        showToast('Пользователь успешно удален', 'success');
        loadUsers(currentPage);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Toast notifications
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-message">${message}</div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 5000);
}

