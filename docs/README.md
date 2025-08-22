# ClauseEase AI - Secure Authentication System

A modern, secure Flask authentication system with email/phone registration, password reset, and responsive UI.

## Features

✅ **Complete Authentication System**
- User registration with email and/or phone
- Login with email or phone + password
- Secure logout functionality
- Password reset via email
- **OTP verification for email and phone**
- Unique email and phone validation

✅ **Security Features**
- Bcrypt password hashing
- CSRF protection on all forms
- Rate limiting (5 attempts per minute for login/register, 3 for password reset)
- **OTP verification with configurable expiry**
- Secure session management
- Input validation and sanitization

✅ **Modern UI**
- Responsive Bootstrap 5 design
- Beautiful gradient backgrounds
- Glassmorphism effects
- Mobile-friendly interface
- Bootstrap Icons integration

✅ **Database Integration**
- PostgreSQL support (Neon, Supabase, Railway)
- SQLAlchemy 2 ORM
- Automatic database migrations

## Tech Stack

- **Backend**: Flask 3, Flask-Login, Flask-WTF, SQLAlchemy 2
- **Security**: passlib[bcrypt], itsdangerous, Flask-Limiter
- **Email**: Flask-Mail (Gmail App Password or Mailtrap)
- **Database**: PostgreSQL (Neon free tier recommended)
- **Frontend**: Jinja2 + Bootstrap 5 (CDN)
- **Validation**: email-validator, phonenumbers

## Quick Setup

### 1. Clone and Setup Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

#### Option A: Neon (Recommended - Free)
1. Go to [Neon](https://neon.tech) and create a free account
2. Create a new project
3. Copy the connection string (SQLAlchemy format)
4. Add to `.env` file

#### Option B: Supabase
1. Go to [Supabase](https://supabase.com) and create a free project
2. Go to Settings → Database → Connection string
3. Copy the connection string
4. Add to `.env` file

### 3. Email Setup

#### Option A: Gmail (Personal)
1. Enable 2FA on your Google account
2. Create an App Password for "Mail"
3. Use these settings in `.env`:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER="Your App <your@gmail.com>"
```

#### Option B: Mailtrap (Development)
1. Create a [Mailtrap](https://mailtrap.io) account
2. Go to Inboxes → SMTP settings
3. Copy the SMTP values to `.env`

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
FLASK_SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST/DBNAME

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER="Your App <your@gmail.com>"

# Rate Limiting
RATELIMIT_STORAGE_URI=memory://
```

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### Registration
- Users can register with email, phone, or both
- Phone numbers are automatically normalized to E.164 format
- At least one identifier (email or phone) is required
- Passwords must be at least 8 characters

### Login
- Users can login with either email or phone
- The system automatically detects the identifier type
- Rate limiting prevents brute force attacks

### Password Reset
- Users can request password reset via email or phone
- Reset links are sent to the associated email address
- Links expire after 1 hour
- Secure token generation using itsdangerous

### Dashboard
- Secure dashboard for authenticated users
- Displays account information
- Shows security status
- Responsive design with Bootstrap 5

## Security Features

### Password Security
- Bcrypt hashing with salt
- Minimum 8 character requirement
- Secure password verification

### Session Security
- Flask-Login session management
- Secure session cookies
- Automatic logout on session expiry

### Form Security
- CSRF protection on all forms
- Input validation and sanitization
- Rate limiting on authentication endpoints

### Database Security
- SQLAlchemy ORM prevents SQL injection
- Unique constraints on email and phone
- Proper error handling

## Project Structure

```
flask_auth_app/
├── app.py                 # Main application file
├── models.py              # Database models
├── forms.py               # WTForms definitions
├── extensions.py          # Flask extensions
├── email_utils.py         # Email utilities
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── templates/            # Jinja2 templates
│   ├── base.html         # Base template
│   ├── register.html     # Registration page
│   ├── login.html        # Login page
│   ├── forgot_password.html
│   ├── reset_password.html
│   └── dashboard.html    # User dashboard
└── static/               # Static files
    ├── css/              # Custom CSS
    └── js/               # JavaScript files
```

## Deployment

### Production Considerations
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up a reverse proxy (Nginx)
3. Use environment variables for all secrets
4. Enable HTTPS with SSL certificates
5. Set up proper logging
6. Use a production database
7. Configure email service for production

### Example Gunicorn Command
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

---

**Note**: This is a secure authentication system designed for production use. Always follow security best practices when deploying to production environments. 