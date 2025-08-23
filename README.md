# ClauseEase AI 🔐

A robust Flask-based web application with comprehensive user authentication, OTP verification, and modern UI design.

## ✨ Features

### 🔐 **Authentication System**
- **User Registration** with mandatory email and phone number
- **Secure Login** using email/phone + password
- **OTP Verification** for account activation
- **Password Reset** functionality
- **Session Management** with Flask-Login

### 📱 **Phone & Email Integration**
- **Phone Number Validation** using `phonenumbers` library
- **Country Code Selection** for international numbers
- **Email OTP Delivery** with Flask-Mail
- **Terminal OTP Display** for development/testing

### 🎨 **Modern UI/UX**
- **Responsive Design** with Bootstrap 5
- **Gradient Backgrounds** and modern styling
- **Interactive OTP Input** with auto-focus
- **Password Policy Indicators** with real-time validation
- **Clean Card-based Layout**

### 🗄️ **Database & Security**
- **Neon PostgreSQL** cloud database integration
- **SQLAlchemy ORM** for database operations
- **CSRF Protection** with Flask-WTF
- **Rate Limiting** on authentication routes
- **Secure Password Hashing**

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL database (Neon recommended)
- SMTP email service (Gmail, Outlook, etc.)

### 1. Clone & Setup
```bash
git clone <your-repo-url>
cd ClauseEaseAI
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
# Flask Configuration
FLASK_SECRET_KEY=your-super-secret-key-here

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+psycopg2://user:password@host/database

# Email Configuration (Gmail Example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### 4. Database Setup
```bash
# The app will automatically create tables on first run
# Make sure your Neon database is accessible
```

### 5. Run the Application
```bash
python src/app.py
```

Visit `http://localhost:5000` in your browser!

## 📁 Project Structure

```
ClauseEaseAI/
├── src/                    # Main application code
│   ├── app.py             # Flask app & routes
│   ├── models.py          # Database models
│   ├── forms.py           # Flask-WTF forms
│   ├── extensions.py      # Flask extensions
│   ├── email_utils.py     # Email utilities
│   └── otp_utils.py       # OTP generation & validation
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── verify_account.html # OTP verification page
│   ├── dashboard.html     # User dashboard
│   ├── forgot_password.html # Password reset
│   └── reset_password.html # New password setup
├── static/                 # Static assets
│   ├── js/                # JavaScript files
│   ├── icon.png           # App icon
│   └── favicon.ico        # Favicon
├── scripts/                # Utility scripts
│   ├── setup.py           # Initial setup
│   ├── reset_demo_db.py   # Database reset
│   └── view_users.py      # User management
├── config/                 # Configuration files
│   └── env_template.txt   # Environment template
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
└── run.py                 # Application entry point
```

## 🔄 User Flow

### **New User Registration**
1. User fills registration form (email + phone mandatory)
2. OTP automatically generated and displayed in terminal
3. User redirected to verification page
4. User enters OTP from terminal
5. Account verified → Login access granted

### **Existing User Login**
1. User enters email/phone + password
2. If unverified → Redirected to verification page
3. If verified → Login successful → Dashboard access

### **Password Reset**
1. User requests password reset
2. Reset token sent to email
3. User clicks reset link
4. New password set

## 🛠️ Configuration

### **Email Setup**
- **Gmail**: Use App Password (2FA required)
- **Outlook**: Use App Password or enable "Less secure apps"
- **Custom SMTP**: Configure server, port, and credentials

### **Database Setup**
- **Neon PostgreSQL**: Recommended for production
- **Local PostgreSQL**: For development
- **No SQLite**: Application exclusively uses PostgreSQL

### **Security Settings**
- **SECRET_KEY**: Change in production
- **Rate Limiting**: 5 attempts per minute for auth routes
- **CSRF Protection**: Enabled by default

## 🧪 Testing

### **OTP Testing**
- OTP codes are displayed in terminal during development
- Use these codes for testing verification
- Email delivery happens in background

### **User Management**
```bash
# View all users
python scripts/view_users.py

# Reset demo database
python scripts/reset_demo_db.py
```

## 🚨 Troubleshooting

### **Common Issues**

#### **Database Connection Error**
```
❌ ERROR: DATABASE_URL not found in .env file!
```
**Solution**: Check your `.env` file and ensure `DATABASE_URL` is set correctly.

#### **Email Not Sending**
```
❌ Email sending failed: [Errno 11001] getaddrinfo failed
```
**Solution**: Verify SMTP settings and check internet connection.

#### **OTP Not Showing in Terminal**
```
🚨 OTP GENERATED FOR NEW USER 🚨
```
**Solution**: Check terminal output during registration - OTP should display prominently.

#### **Phone Number Format Issues**
```
📱 COMBINED PHONE: +911234567890
```
**Solution**: Phone numbers are automatically formatted to E.164 standard.

### **Debug Mode**
Enable debug logging by checking terminal output for:
- 🔍 Form validation details
- 📱 Phone number processing
- 🚨 OTP generation
- 🔄 Redirect information

## 🔧 Development

### **Adding New Features**
1. Create models in `src/models.py`
2. Add forms in `src/forms.py`
3. Create routes in `src/app.py`
4. Add templates in `templates/`
5. Update static files in `static/`

### **Database Migrations**
```bash
# The app uses Flask-SQLAlchemy with auto-creation
# Tables are created automatically on first run
```

### **Code Style**
- Follow PEP 8 guidelines
- Use descriptive variable names
- Add comments for complex logic
- Keep functions focused and small

## 📚 Dependencies

### **Core Dependencies**
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling & CSRF protection
- **Flask-Mail**: Email functionality
- **Flask-Limiter**: Rate limiting

### **Utility Libraries**
- **python-dotenv**: Environment variable management
- **phonenumbers**: Phone number validation
- **psycopg2-binary**: PostgreSQL adapter
- **Werkzeug**: Password hashing

## 🌟 Features in Detail

### **Phone Number Handling**
- **International Support**: Country code selection
- **Validation**: Automatic phone number validation
- **Storage**: E.164 format in database
- **Login**: Accepts phone or email for authentication

### **OTP System**
- **Generation**: 6-digit numeric codes
- **Expiry**: 10-minute validity period
- **Delivery**: Email-based delivery
- **Verification**: Real-time validation
- **Resend**: User-triggered code regeneration

### **Security Features**
- **Password Policy**: 8+ chars, uppercase, lowercase, numbers, special chars
- **Session Security**: Secure session management
- **Rate Limiting**: Prevents brute force attacks
- **CSRF Protection**: Cross-site request forgery prevention

## 📱 Mobile Responsiveness

The application is fully responsive and works on:
- **Desktop**: Full feature set
- **Tablet**: Optimized layout
- **Mobile**: Touch-friendly interface

## 🔒 Production Deployment

### **Security Checklist**
- [ ] Change `FLASK_SECRET_KEY`
- [ ] Use HTTPS
- [ ] Configure production database
- [ ] Set up proper email service
- [ ] Enable logging
- [ ] Configure rate limiting

### **Deployment Options**
- **Heroku**: Easy deployment with PostgreSQL addon
- **DigitalOcean**: App Platform with managed database
- **AWS**: EC2 + RDS setup
- **VPS**: Manual deployment with Nginx + Gunicorn

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the code comments
- Open an issue on GitHub

---

**Built with ❤️ using Flask and modern web technologies** 