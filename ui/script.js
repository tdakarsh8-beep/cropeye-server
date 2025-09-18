document.addEventListener('DOMContentLoaded', function() {
    // API Endpoints
    const API_BASE_URL = 'http://localhost:8000/api';
    const API_LOGIN_URL = `${API_BASE_URL}/token/`;
    const API_OTP_REQUEST = `${API_BASE_URL}/otp/`;
    const API_OTP_VERIFY = `${API_BASE_URL}/verify-otp/`;
    const API_USERS_ME = `${API_BASE_URL}/users/me/`;
    
    // DOM Elements
    const loginSection = document.getElementById('login-section');
    const dashboardSection = document.getElementById('dashboard-section');
    const tasksSection = document.getElementById('tasks-section');
    const usersSection = document.getElementById('users-section');
    const equipmentSection = document.getElementById('equipment-section');
    const bookingsSection = document.getElementById('bookings-section');
    
    const emailForm = document.getElementById('email-form');
    const otpForm = document.getElementById('otp-form');
    const sendOtpBtn = document.getElementById('send-otp-btn');
    const verifyOtpBtn = document.getElementById('verify-otp-btn');
    const backBtn = document.getElementById('back-btn');
    const logoutBtn = document.getElementById('logout-btn');
    
    const usernameInput = document.getElementById('username-input');
    const passwordInput = document.getElementById('password-input');
    const otpInput = document.getElementById('otp');
    const usernameDisplay = document.getElementById('username');
    const userGreeting = document.getElementById('user-greeting');
    
    // User credentials
    let currentUsername = '';
    let userEmail = '';
    let tempToken = '';
    
    // Navigation links
    const navLinks = document.querySelectorAll('nav ul li a');
    
    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
        // Fetch user data and show app
        fetchUserProfile(token);
    } else {
        showLogin();
    }
    
    // Event Listeners
    sendOtpBtn.addEventListener('click', function() {
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();
        
        console.log('Attempting login with username:', username);
        
        if (!username || !password) {
            alert('Please enter both username and password');
            return;
        }
        
        // Show loading state
        sendOtpBtn.disabled = true;
        sendOtpBtn.textContent = 'Authenticating...';
        
        console.log('Sending authentication request to:', API_LOGIN_URL);
        
        // First authenticate with username and password
        fetch(API_LOGIN_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                username: username,
                password: password
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    console.error('Authentication error details:', errorData);
                    if (response.status === 401) {
                        throw new Error('Invalid username or password');
                    }
                    throw new Error(`Authentication failed: ${errorData.detail || errorData.error || 'Unknown error'}`);
                }).catch(e => {
                    if (e.message === 'Invalid username or password') {
                        throw e;
                    }
                    if (response.status === 401) {
                        throw new Error('Invalid username or password');
                    }
                    throw new Error(`Authentication failed. Status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            // Store username and token
            currentUsername = username;
            tempToken = data.access;
            console.log('Authentication successful, token received');
            
            // Fetch user profile to get email
            return fetch(API_USERS_ME, {
                headers: {
                    'Authorization': `Bearer ${tempToken}`
                }
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to get user details. Status: ${response.status}`);
            }
            return response.json();
        })
        .then(userData => {
            // Store user email
            userEmail = userData.email;
            console.log('User profile retrieved, email:', userEmail);
            
            if (!userEmail) {
                throw new Error('No email address found for this user. Please contact administrator.');
            }
            
            // Now request OTP
            sendOtpBtn.textContent = 'Sending OTP...';
            
            return fetch(API_OTP_REQUEST, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: userEmail })
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`OTP request failed. Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Show OTP input form
            emailForm.style.display = 'none';
            otpForm.style.display = 'block';
            console.log('OTP requested successfully and sent to registered email: ' + userEmail);
        })
        .catch(error => {
            console.error('Error in authentication process:', error);
            if (error.message.includes('Invalid username or password')) {
                alert('Invalid username or password. Please try again.');
            } else if (error.message.includes('No email address found')) {
                alert('No email address registered for this account. Please contact your administrator.');
            } else if (error.message.includes('OTP request failed')) {
                alert('Failed to send OTP. Please try again later.');
            } else {
                alert('Authentication failed: ' + error.message);
            }
        })
        .finally(() => {
            // Reset button state
            sendOtpBtn.disabled = false;
            sendOtpBtn.textContent = 'Send OTP';
        });
    });
    
    backBtn.addEventListener('click', function() {
        emailForm.style.display = 'block';
        otpForm.style.display = 'none';
        
        // Clear credentials
        currentUsername = '';
        userEmail = '';
        tempToken = '';
    });
    
    verifyOtpBtn.addEventListener('click', function() {
        const otp = otpInput.value.trim();
        
        if (!otp) {
            alert('Please enter the OTP');
            return;
        }
        
        if (!userEmail) {
            alert('Session expired. Please try logging in again.');
            showLogin();
            return;
        }
        
        // Show loading state
        verifyOtpBtn.disabled = true;
        verifyOtpBtn.textContent = 'Verifying...';
        
        console.log('Verifying OTP:', otp, 'for email:', userEmail);
        
        // Verify OTP with API
        fetch(API_OTP_VERIFY, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                email: userEmail,
                otp: otp
            })
        })
        .then(response => {
            console.log('OTP verification response status:', response.status);
            
            if (!response.ok) {
                return response.json().then(errorData => {
                    console.error('OTP verification error details:', errorData);
                    throw new Error(errorData.detail || 'OTP verification failed');
                }).catch(e => {
                    if (e.message) {
                        throw e;
                    }
                    throw new Error(`OTP verification failed. Status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('OTP verification successful, tokens received');
            
            // Store tokens
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            
            // Show app with current username
            showApp(currentUsername);
        })
        .catch(error => {
            console.error('Error verifying OTP:', error);
            if (error.message.includes('Invalid OTP')) {
                alert('Invalid OTP. Please check and try again.');
            } else if (error.message.includes('OTP has expired')) {
                alert('Your OTP has expired. Please request a new one.');
            } else if (error.message.includes('No OTP found')) {
                alert('No valid OTP found. Please request a new one.');
            } else {
                alert('OTP verification failed: ' + error.message);
            }
        })
        .finally(() => {
            // Reset button state
            verifyOtpBtn.disabled = false;
            verifyOtpBtn.textContent = 'Verify OTP';
        });
    });
    
    logoutBtn.addEventListener('click', function() {
        // Clear tokens and credentials
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        currentUsername = '';
        userEmail = '';
        tempToken = '';
        
        showLogin();
    });
    
    // Navigation handling
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Hide all sections
            hideAllSections();
            
            // Show the appropriate section based on the href
            const href = this.getAttribute('href');
            if (href === '#' || href === '#dashboard') {
                dashboardSection.classList.remove('hidden');
            } else if (href === '#tasks') {
                tasksSection.classList.remove('hidden');
            } else if (href === '#users') {
                usersSection.classList.remove('hidden');
            } else if (href === '#equipment') {
                equipmentSection.classList.remove('hidden');
            } else if (href === '#bookings') {
                bookingsSection.classList.remove('hidden');
            } else if (href === '#farms') {
                // Redirect to the farms page
                window.location.href = 'farms/index.html';
            }
        });
    });
    
    // Initialize search functionality
    initializeSearch('task-search', 'tasks-section');
    initializeSearch('user-search', 'users-section');
    initializeSearch('equipment-search', 'equipment-section');
    initializeSearch('booking-search', 'bookings-section');
    
    // Add event listeners for add/create buttons
    document.getElementById('create-task-btn').addEventListener('click', function() {
        hideAllSections();
        tasksSection.classList.remove('hidden');
        navLinks.forEach(l => l.classList.remove('active'));
        document.querySelector('a[href="#tasks"]').classList.add('active');
    });
    
    document.getElementById('create-booking-btn').addEventListener('click', function() {
        hideAllSections();
        bookingsSection.classList.remove('hidden');
        navLinks.forEach(l => l.classList.remove('active'));
        document.querySelector('a[href="#bookings"]').classList.add('active');
    });
    
    document.getElementById('manage-equipment-btn').addEventListener('click', function() {
        hideAllSections();
        equipmentSection.classList.remove('hidden');
        navLinks.forEach(l => l.classList.remove('active'));
        document.querySelector('a[href="#equipment"]').classList.add('active');
    });
    
    // Utility Functions
    function fetchUserProfile(token) {
        fetch(API_USERS_ME, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(userData => {
            const username = userData.username || userData.email.split('@')[0];
            currentUsername = username;
            userEmail = userData.email;
            showApp(username);
        })
        .catch(error => {
            console.error('Error fetching user profile:', error);
            // Token might be invalid, clear it and show login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            currentUsername = '';
            userEmail = '';
            showLogin();
        });
    }
    
    function showLogin() {
        loginSection.classList.remove('hidden');
        dashboardSection.classList.add('hidden');
        document.querySelector('header').style.display = 'none';
        document.querySelector('footer').style.display = 'none';
        
        emailForm.style.display = 'block';
        otpForm.style.display = 'none';
        usernameInput.value = '';
        passwordInput.value = '';
        otpInput.value = '';
    }
    
    function showApp(username) {
        loginSection.classList.add('hidden');
        dashboardSection.classList.remove('hidden');
        document.querySelector('header').style.display = 'block';
        document.querySelector('footer').style.display = 'block';
        
        // Update username displays
        usernameDisplay.textContent = username;
        userGreeting.textContent = username;
    }
    
    function hideAllSections() {
        dashboardSection.classList.add('hidden');
        tasksSection.classList.add('hidden');
        usersSection.classList.add('hidden');
        equipmentSection.classList.add('hidden');
        bookingsSection.classList.add('hidden');
    }
    
    function initializeSearch(inputId, sectionId) {
        const searchInput = document.getElementById(inputId);
        if (!searchInput) return;
        
        searchInput.addEventListener('keyup', function() {
            const searchValue = this.value.toLowerCase();
            const section = document.getElementById(sectionId);
            const rows = section.querySelectorAll('table tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchValue)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
    
    // Add event listeners for edit and delete buttons
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const id = this.closest('tr').cells[0].textContent;
            alert('Edit item with ID: ' + id + '\nThis would open an edit form in a real application.');
        });
    });
    
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function() {
            const id = this.closest('tr').cells[0].textContent;
            if (confirm('Are you sure you want to delete this item?')) {
                alert('Item with ID: ' + id + ' would be deleted in a real application.');
                // In a real app, this would make an API call and then remove the row
            }
        });
    });
}); 