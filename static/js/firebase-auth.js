// Firebase Authentication for ClauseEase AI
class FirebasePhoneAuth {
    constructor() {
        this.confirmationResult = null;
        this.recaptchaVerifier = null;
        this.init();
    }

    init() {
        // Firebase configuration (will be replaced by server-side config)
        const firebaseConfig = {
            apiKey: window.firebaseConfig?.apiKey || "your-api-key",
            authDomain: window.firebaseConfig?.authDomain || "your-project.firebaseapp.com",
            projectId: window.firebaseConfig?.projectId || "your-project-id",
            storageBucket: window.firebaseConfig?.storageBucket || "your-project.appspot.com",
            messagingSenderId: window.firebaseConfig?.messagingSenderId || "123456789",
            appId: window.firebaseConfig?.appId || "your-app-id"
        };

        // Initialize Firebase
        if (typeof firebase !== 'undefined') {
            firebase.initializeApp(firebaseConfig);
            this.auth = firebase.auth();
        } else {
            console.error('Firebase SDK not loaded');
        }
    }

    // Set up reCAPTCHA verifier
    setUpRecaptcha(containerId, phoneNumber) {
        return new Promise((resolve, reject) => {
            try {
                // Clear any existing reCAPTCHA
                if (this.recaptchaVerifier) {
                    this.recaptchaVerifier.clear();
                }

                // Create new reCAPTCHA verifier
                this.recaptchaVerifier = new firebase.auth.RecaptchaVerifier(containerId, {
                    'size': 'normal',
                    'callback': (response) => {
                        // reCAPTCHA solved, proceed with OTP sending
                        this.sendOTP(phoneNumber).then(resolve).catch(reject);
                    },
                    'expired-callback': () => {
                        reject(new Error('reCAPTCHA expired'));
                    }
                }, this.auth);

                // Render reCAPTCHA
                this.recaptchaVerifier.render().then((widgetId) => {
                    this.recaptchaWidgetId = widgetId;
                }).catch(reject);

            } catch (error) {
                reject(error);
            }
        });
    }

    // Send OTP
    async sendOTP(phoneNumber) {
        try {
            if (!this.recaptchaVerifier) {
                throw new Error('reCAPTCHA not set up');
            }

            const result = await this.auth.signInWithPhoneNumber(phoneNumber, this.recaptchaVerifier);
            this.confirmationResult = result;
            return result;
        } catch (error) {
            console.error('Error sending OTP:', error);
            throw error;
        }
    }

    // Verify OTP
    async verifyOTP(otp) {
        try {
            if (!this.confirmationResult) {
                throw new Error('No confirmation result available');
            }

            const result = await this.confirmationResult.confirm(otp);
            return result;
        } catch (error) {
            console.error('Error verifying OTP:', error);
            throw error;
        }
    }

    // Get current user's ID token
    async getIdToken() {
        try {
            const user = this.auth.currentUser;
            if (user) {
                return await user.getIdToken();
            }
            throw new Error('No authenticated user');
        } catch (error) {
            console.error('Error getting ID token:', error);
            throw error;
        }
    }

    // Sign out
    async signOut() {
        try {
            await this.auth.signOut();
            this.confirmationResult = null;
            if (this.recaptchaVerifier) {
                this.recaptchaVerifier.clear();
                this.recaptchaVerifier = null;
            }
        } catch (error) {
            console.error('Error signing out:', error);
            throw error;
        }
    }

    // Check if user is authenticated
    isAuthenticated() {
        return this.auth.currentUser !== null;
    }

    // Get current user
    getCurrentUser() {
        return this.auth.currentUser;
    }
}

// Initialize Firebase Auth when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.firebaseAuth = new FirebasePhoneAuth();
    
    // Initialize phone auth UI if elements exist
    initializePhoneAuthUI();
});

// Initialize Phone Auth UI
function initializePhoneAuthUI() {
    const sendOtpBtn = document.getElementById('send-otp-btn');
    const verifyOtpBtn = document.getElementById('verify-otp-btn');
    const phoneInput = document.getElementById('phone-number');
    const otpInput = document.getElementById('otp-input');
    const otpContainer = document.getElementById('otp-container');
    const recaptchaContainer = document.getElementById('recaptcha-container');
    const fallbackForm = document.getElementById('fallback-otp-form');

    if (!sendOtpBtn || !verifyOtpBtn) return;

    // Send OTP button click handler
    sendOtpBtn.addEventListener('click', async function() {
        const phoneNumber = phoneInput.value;
        if (!phoneNumber) {
            showAlert('Please enter a phone number', 'error');
            return;
        }

        try {
            sendOtpBtn.disabled = true;
            sendOtpBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Sending...';
            
            await window.firebaseAuth.setUpRecaptcha('recaptcha-container', phoneNumber);
            
            // OTP sent successfully
            otpContainer.style.display = 'block';
            verifyOtpBtn.style.display = 'block';
            sendOtpBtn.style.display = 'none';
            
            showAlert('OTP sent successfully!', 'success');
            
        } catch (error) {
            console.error('Error sending OTP:', error);
            showAlert('Failed to send OTP: ' + error.message, 'error');
            
            // Show fallback form
            if (fallbackForm) {
                fallbackForm.style.display = 'block';
            }
        } finally {
            sendOtpBtn.disabled = false;
            sendOtpBtn.innerHTML = '<i class="bi bi-send"></i> Send Verification Code';
        }
    });

    // Verify OTP button click handler
    verifyOtpBtn.addEventListener('click', async function() {
        const otp = otpInput.value;
        if (!otp) {
            showAlert('Please enter the OTP', 'error');
            return;
        }

        try {
            verifyOtpBtn.disabled = true;
            verifyOtpBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Verifying...';
            
            const result = await window.firebaseAuth.verifyOTP(otp);
            const idToken = await result.user.getIdToken();
            
            // Send verification to backend
            const response = await fetch('/firebase/verify-phone', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    idToken: idToken,
                    userId: window.currentUserId || ''
                })
            });

            const data = await response.json();
            
            if (data.success) {
                showAlert('Phone verified successfully!', 'success');
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                showAlert('Verification failed: ' + data.error, 'error');
            }
            
        } catch (error) {
            console.error('Error verifying OTP:', error);
            showAlert('Invalid OTP: ' + error.message, 'error');
        } finally {
            verifyOtpBtn.disabled = false;
            verifyOtpBtn.innerHTML = '<i class="bi bi-check-circle"></i> Verify Code';
        }
    });
}

// Utility functions
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the page
    const container = document.querySelector('.auth-container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

// Export for use in other scripts
window.FirebasePhoneAuth = FirebasePhoneAuth; 