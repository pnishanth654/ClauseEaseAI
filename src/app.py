import os
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from werkzeug.utils import secure_filename
from extensions import db, login_manager, mail, limiter
from models import User, Document, Chat, ChatMessage
from forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, EmailOTPForm, ResendOTPForm
from email_utils import generate_reset_token, verify_reset_token, send_password_reset
from otp_utils import generate_otp, get_otp_expiry_time, send_email_otp, is_otp_expired
import phonenumbers

load_dotenv()

# File upload configuration
# Get the project root directory by looking for the src folder
def find_project_root():
    """Find the project root directory by looking for src folder"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # If we're in src folder, go up one level
    if os.path.basename(current_dir) == 'src':
        return os.path.dirname(current_dir)
    
    # If we're already in project root, use current directory
    if os.path.exists(os.path.join(current_dir, 'src')):
        return current_dir
    
    # If we're somewhere else, try to find the project root
    # Look for src folder in parent directories
    parent_dir = current_dir
    for _ in range(5):  # Look up to 5 levels up
        if os.path.exists(os.path.join(parent_dir, 'src')):
            return parent_dir
        parent_dir = os.path.dirname(parent_dir)
    
    # Fallback: use current directory
    return current_dir

PROJECT_ROOT = find_project_root()
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')  # Store in project root
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'rtf', 'md', 'odt', 'ppt', 'pptx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')

    # Core config
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
    
    # Database configuration - EXCLUSIVELY use Neon PostgreSQL with connection pooling
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env file!")
        print("🔧 Please set DATABASE_URL in your .env file")
        print("📖 Example: DATABASE_URL=postgresql+psycopg2://user:pass@host/dbname")
        exit(1)
    
    # Clean and validate the database URL
    original_url = database_url
    database_url = database_url.strip()
    
    # Check if it's a valid PostgreSQL URL
    if not database_url.startswith(('postgresql://', 'postgresql+psycopg2://')):
        print("❌ ERROR: Invalid DATABASE_URL format!")
        print("🔧 DATABASE_URL must start with 'postgresql://' or 'postgresql+psycopg2://'")
        print(f"📖 Current value: {database_url}")
        exit(1)
    
    # Add connection pooling and SSL parameters to prevent connection drops
    # Use urllib.parse to properly handle URL parameters
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    
    try:
        parsed_url = urlparse(database_url)
        query_params = parse_qs(parsed_url.query)
        
        # Add our connection parameters
        query_params.update({
            'sslmode': ['require'],
            'connect_timeout': ['30'],
            'application_name': ['clauseease_ai'],
            'keepalives': ['1'],
            'keepalives_idle': ['30'],
            'keepalives_interval': ['10'],
            'keepalives_count': ['5']
        })
        
        # Rebuild the URL with parameters
        new_query = urlencode(query_params, doseq=True)
        database_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        print("✅ Database URL enhanced with connection parameters")
        
    except Exception as url_error:
        print(f"⚠️ URL parsing warning: {url_error}")
        # Fallback: add basic parameters
        if '?' in database_url:
            database_url += '&sslmode=require&connect_timeout=30'
        else:
            database_url += '?sslmode=require&connect_timeout=30'
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        'pool_size': 5,  # Reduced pool size for better stability
        'pool_timeout': 20,  # Reduced timeout
        'pool_recycle': 1800,  # Recycle connections every 30 minutes
        'pool_pre_ping': True,  # Test connections before use
        'max_overflow': 10,  # Reduced overflow
        'echo': False,
        'connect_args': {
            'connect_timeout': 30,
            'application_name': 'clauseease_ai'
        }
    }
    
    print(f"🗄️  Database: {original_url.split('@')[1] if '@' in original_url else 'Connected'}")
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Mail config
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "your-email@gmail.com")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "your-app-password")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", "your-email@gmail.com")
    
    # Add timeout to prevent hanging
    app.config["MAIL_TIMEOUT"] = 10  # 10 seconds timeout
    app.config["MAIL_USE_SSL"] = False

    # OTP configuration - using custom email and SMS verification

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    CSRFProtect(app)

    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")

    # Define database helper functions first
    def test_database_connection():
        """Test database connection and return status"""
        try:
            # Test basic connection with timeout
            db.session.execute(text("SELECT 1"))
            db.session.commit()
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)
    
    def wait_for_database(max_attempts=5, delay=2):
        """Wait for database to become available"""
        for attempt in range(max_attempts):
            try:
                print(f"🔄 Database connection attempt {attempt + 1}/{max_attempts}")
                db.session.execute(text("SELECT 1"))
                db.session.commit()
                print("✅ Database connection successful")
                return True
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {str(e)[:100]}")
                if attempt < max_attempts - 1:
                    print(f"⏳ Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                else:
                    print("❌ All database connection attempts failed")
                    return False
        return False

    def recover_database_connection():
        """Attempt to recover database connection"""
        try:
            # Close existing session
            db.session.close()
            
            # Try to create new connection
            db.session.execute(text("SELECT 1"))
            db.session.commit()
            
            return True
        except Exception as e:
            return False

    # Initialize database tables
    with app.app_context():
        try:
            # Wait a moment for database engine to fully initialize
            time.sleep(1)
            
            # Test connection with retry mechanism
            print("🔍 Testing database connection...")
            if not wait_for_database(max_attempts=5, delay=2):
                raise Exception("Database connection failed after multiple attempts")
            
            # Create all tables
            print("🔨 Creating database tables...")
            db.create_all()
            print("✅ Database tables created")
            
            # Final connection test
            db.session.execute(text("SELECT 1"))
            db.session.commit()
            print("✅ Database fully connected and ready")
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Database connection failed")
            print(f"   🔍 Error details: {error_msg}")
            
            # Provide specific error guidance
            if "authentication failed" in error_msg.lower():
                print("   🔧 Issue: Authentication failed - check username/password")
            elif "connection refused" in error_msg.lower():
                print("   🔧 Issue: Connection refused - check if database is running")
            elif "ssl" in error_msg.lower():
                print("   🔧 Issue: SSL connection problem - check network")
            elif "timeout" in error_msg.lower():
                print("   🔧 Issue: Connection timeout - check internet")
            elif "database" in error_msg.lower() and "does not exist" in error_msg.lower():
                print("   🔧 Issue: Database doesn't exist - check database name")
            elif "psycopg2" in error_msg.lower():
                print("   🔧 Issue: psycopg2 driver not installed")
                print("   💡 Install with: pip install psycopg2-binary")
            elif "no module named" in error_msg.lower():
                print("   🔧 Issue: Missing Python module")
                print("   💡 Install with: pip install -r requirements.txt")
            else:
                print(f"   🔧 Unknown error: {error_msg[:100]}...")
            
            print("💡 Check your DATABASE_URL in .env file")
            print("💡 Ensure your Neon database is running and accessible")
            print("💡 Run: python test_database.py for detailed diagnostics")
        
        print("🚀 App ready!")

    @login_manager.user_loader
    def load_user(user_email):
        try:
            return db.session.get(User, user_email)
        except Exception as e:
            print(f"❌ Database error in user loader: {e}")
            # Try to refresh the connection
            try:
                db.session.rollback()
                db.session.close()
                db.session.execute(text("SELECT 1"))  # Test connection
                return db.session.get(User, user_email)
            except:
                print(f"❌ Failed to recover database connection in user loader")
                return None

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global exception handler for database and other errors"""
        if "SSL connection has been closed unexpectedly" in str(e) or "connection" in str(e).lower():
            print(f"🚨 Database connection error detected: {e}")
            print("🔄 Attempting to refresh database connection...")
            
            try:
                db.session.rollback()
                db.session.close()
                db.session.execute(text("SELECT 1"))  # Test connection
                print("✅ Database connection refreshed successfully")
            except Exception as refresh_error:
                print(f"❌ Failed to refresh database connection: {refresh_error}")
            
            return "Database connection error. Please refresh the page and try again.", 500
        
        # Re-raise other exceptions
        raise e

    @app.route("/", methods=["GET", "POST"])
    def index():
        """Root route - always show login page first, regardless of authentication"""
        # Test database connection before proceeding
        db_connected, db_message = test_database_connection()
        if not db_connected:
            print(f"❌ Database not connected: {db_message}")
            # Try to recover connection
            if recover_database_connection():
                print("✅ Database connection recovered, proceeding...")
            else:
                print("❌ Database connection recovery failed")
                flash("Database connection error. Please check your internet connection and try again.", "error")
                return render_template("login.html", form=LoginForm())
        
        # If user is already authenticated, redirect to home
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        
        form = LoginForm()
        if form.validate_on_submit():
            identifier = form.identifier.data.strip()
            
            # Try to find user by email or phone with connection retry
            user = None
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    if "@" in identifier:
                        user = User.query.filter_by(email=identifier.lower()).first()
                    else:
                        # Try to parse as phone number
                        try:
                            parsed = phonenumbers.parse(identifier, None)
                            if phonenumbers.is_valid_number(parsed):
                                phone = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                                user = User.query.filter_by(phone=phone).first()
                        except:
                            pass
                    
                    # If we get here, the query was successful
                    break
                    
                except Exception as db_error:
                    print(f"❌ Database connection error (attempt {attempt + 1}/{max_retries}): {db_error}")
                    if attempt < max_retries - 1:
                        print(f"🔄 Retrying database connection...")
                        if recover_database_connection():
                            continue
                        else:
                            break
                    else:
                        print(f"❌ All database connection attempts failed")
                        flash("Database connection error. Please try again in a moment.", "error")
                        return render_template("login.html", form=form)
            
            # Flow 1: User not found - redirect to register
            if not user:
                flash("No user found with this email/phone. Please register first.", "error")
                return redirect(url_for("register"))
            
            # Flow 2: User exists but wrong password
            if not user.check_password(form.password.data):
                flash("Invalid password. Please try again.", "error")
                return render_template("login.html", form=form)
            
            # Flow 3: User exists, password correct, but not verified - redirect to verification
            if not user.email_verified:
                print(f"🔐 UNVERIFIED USER LOGIN ATTEMPT:")
                print(f"   📧 User: {user.email}")
                print(f"   📧 Email Verified: {user.email_verified}")
                
                # Generate new OTP for unverified user
                verification_otp = generate_otp()
                user.email_otp = verification_otp
                user.email_otp_expires = datetime.utcnow() + timedelta(minutes=10)
                
                try:
                    db.session.commit()
                except Exception as commit_error:
                    print(f"❌ Error committing OTP: {commit_error}")
                    db.session.rollback()
                    flash("Error generating verification code. Please try again.", "error")
                    return render_template("login.html", form=form)
                
                # Show OTP in terminal prominently
                print("🚨" * 20)
                print("🚨 LOGIN OTP FOR UNVERIFIED USER 🚨")
                print("🚨" * 20)
                print(f"📧 Email: {user.email}")
                print(f"🔐 OTP Code: {verification_otp}")
                print(f"⏰ Expires: {user.email_otp_expires}")
                print("🚨" * 20)
                
                # Try to send email OTP
                try:
                    print(f"📧 Attempting to send email to: {user.email}")
                    email_sent = send_email_otp(user.email, verification_otp)
                    if email_sent:
                        print(f"✅ Email sent successfully!")
                        flash("Account verification OTP sent to your email. Please verify your account.", "info")
                    else:
                        print(f"⚠️ Email delivery failed, but OTP is available above")
                        flash(f"Account verification OTP: {verification_otp} (Email delivery failed)", "warning")
                except Exception as e:
                    print(f"❌ Email sending error: {e}")
                    print(f"⚠️ Email failed, but OTP is available above")
                    flash(f"Account verification OTP: {verification_otp} (Email delivery failed)", "warning")
                
                return redirect(url_for("verify_account", user_email=user.email))
            
            # Flow 4: User exists, password correct, and verified - LOGIN SUCCESS
            login_user(user)
            flash("Login successful! Welcome back.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("home"))
        
        return render_template("login.html", form=form)

    @app.route("/home")
    @login_required
    def home():
        """Home page - requires authentication, redirects to login if not authenticated"""
        if not current_user.is_authenticated:
            return redirect(url_for("index"))
        return render_template("home.html")

    @app.route("/register", methods=["GET", "POST"])
    @limiter.limit("5 per minute")
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        
        form = RegisterForm()
        if form.validate_on_submit():
            print(f"🔍 REGISTRATION FORM VALIDATED:")
            print(f"   First Name: {form.first_name.data}")
            print(f"   Last Name: {form.last_name.data}")
            print(f"   Email: {form.email.data}")
            print(f"   Country Code: {form.country_code.data}")
            print(f"   Phone: {form.phone.data}")
            print(f"   Gender: {form.gender.data}")
            print(f"   Date of Birth: {form.date_of_birth.data}")
            
            user = User()
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data.lower()
            user.phone = form.country_code.data + form.phone.data
            user.gender = form.gender.data
            user.date_of_birth = datetime.strptime(form.date_of_birth.data, '%Y-%m-%d').date()
            user.set_password(form.password.data)
            
            print(f"📱 COMBINED PHONE: {user.phone}")
            print(f"📧 USER EMAIL: {user.email}")
            
            # Check if user already exists before trying to save
            existing_user = User.query.filter_by(email=user.email).first()
            if existing_user:
                if existing_user.email_verified:
                    # User exists and is verified - redirect to login
                    flash("An account with this email already exists and is verified. Please login instead.", "info")
                    return redirect(url_for("login"))
                else:
                    # User exists but not verified - redirect to verification
                    flash("An account with this email already exists but is not verified. Please check your email for verification.", "info")
                    return redirect(url_for("verify_account", user_email=existing_user.email))
            
            # Check if phone already exists
            existing_phone = User.query.filter_by(phone=user.phone).first()
            if existing_phone:
                flash("An account with this phone number already exists. Please use a different phone number.", "error")
                return render_template("register.html", form=form)
            
            try:
                # Auto-generate OTP for immediate verification
                email_otp = generate_otp()
                user.email_otp = email_otp
                user.email_otp_expires = get_otp_expiry_time()
                
                # Save the user to database with OTP
                db.session.add(user)
                db.session.commit()
                print(f"✅ User saved to database with email: {user.email}")
                
                # Show OTP in terminal prominently
                print("\n" + "🚨" * 30)
                print("🚨🚨🚨 REGISTRATION OTP GENERATED 🚨🚨🚨")
                print("🚨🚨🚨 FOR NEW USER REGISTRATION 🚨🚨🚨")
                print("🚨" * 30)
                print(f"📧 Email: {user.email}")
                print(f"🔐 OTP Code: {email_otp}")
                print(f"⏰ Expires: {user.email_otp_expires}")
                print("🚨" * 30)
                print("🚨🚨🚨 COPY THIS OTP TO VERIFY ACCOUNT 🚨🚨🚨")
                print("🚨" * 30 + "\n")
                
                # Try to send email OTP
                try:
                    print(f"📧 Attempting to send email to: {user.email}")
                    email_sent = send_email_otp(user.email, email_otp)
                    if email_sent:
                        print(f"✅ Email sent successfully!")
                    else:
                        print(f"⚠️ Email delivery failed, but OTP is available above")
                except Exception as e:
                    print(f"❌ Email sending error: {e}")
                    print(f"⚠️ Email failed, but OTP is available above")
                
                # Show success message and redirect to verification page
                flash("Registration successful! OTP sent to your email. Please verify your account.", "success")
                print(f"🔄 Redirecting to verification page for user: {user.email}")
                return redirect(url_for("verify_account", user_email=user.email))
            except IntegrityError:
                db.session.rollback()
                flash("An error occurred during registration. Please try again.", "error")
        
        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    @limiter.limit("5 per minute")
    def login():
        """Login route - redirects to root for consistent login handling"""
        # Redirect to root route for consistent login experience
        return redirect(url_for("index"))

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("index"))

    @app.route("/forgot-password", methods=["GET", "POST"])
    @limiter.limit("3 per minute")
    def forgot_password():
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        
        form = ForgotPasswordForm()
        if form.validate_on_submit():
            identifier = form.identifier.data.strip()
            
            # Find user by email or phone
            user = None
            if "@" in identifier:
                user = User.query.filter_by(email=identifier.lower()).first()
            else:
                try:
                    parsed = phonenumbers.parse(identifier, None)
                    if phonenumbers.is_valid_number(parsed):
                        phone = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                        user = User.query.filter_by(phone=phone).first()
                except:
                    pass
            
            # Flow 1: User not found
            if not user:
                flash("No user associated with this email. Please register first.", "error")
                return redirect(url_for("register"))
            
            # Flow 2: User found but not verified
            if not user.email_verified:
                flash("Please verify your account before resetting password.", "warning")
                return redirect(url_for("verify_account", user_email=user.email))
            
            # Flow 3: User found and verified, but no email associated
            if not user.email:
                flash("No email associated with this account. Cannot send password reset.", "error")
                return render_template("forgot_password.html", form=form)
            
            # Flow 4: User found, verified, and has email - SEND RESET LINK
            token = generate_reset_token(user.email)
            try:
                send_password_reset(user.email, token)
                flash("Password reset link sent to your email.", "success")
                return redirect(url_for("index"))  # Redirect to login page after sending reset
            except Exception as e:
                flash("Error sending email. Please try again.", "error")
        
        return render_template("forgot_password.html", form=form)

    @app.route("/reset-password/<token>", methods=["GET", "POST"])
    def reset_password(token):
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        
        user_email = verify_reset_token(token)
        if not user_email:
            flash("Invalid or expired reset link.", "error")
            return redirect(url_for("forgot_password"))
        
        user = User.query.get(user_email)
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("forgot_password"))
        
        form = ResetPasswordForm()
        if form.validate_on_submit():
            # Check if new password is the same as current password
            if user.is_same_password(form.password.data):
                flash("❌ Your new password cannot be the same as your current password! Please choose a different password.", "error")
                return render_template("reset_password.html", form=form)
            
            # Set new password if it's different
            user.set_password(form.password.data)
            db.session.commit()
            flash("✅ Password updated successfully! Please log in.", "success")
            return redirect(url_for("index"))
        
        return render_template("reset_password.html", form=form)

    @app.route("/verify-account/<user_email>", methods=["GET", "POST"])
    def verify_account(user_email):
        user = User.query.get_or_404(user_email)
        
        # Debug: Print user state
        print(f"\n🔍 VERIFICATION PAGE LOADED:")
        print(f"📧 User Email: {user.email}")
        print(f"📧 Email Verified: {user.email_verified}")
        print(f"📧 Has OTP: {user.email_otp is not None}")
        print(f"📧 OTP Value: {user.email_otp}")
        
        # Check if user is already verified
        if user.email_verified:
            flash("Account already verified!", "info")
            return redirect(url_for("login"))
        
        email_form = EmailOTPForm()
        resend_form = ResendOTPForm()
        
        if request.method == "POST":
            print(f"\n🔍 POST REQUEST RECEIVED:")
            print(f"   Form data: {dict(request.form)}")
            print(f"   Submit value: {request.form.get('submit')}")
            
            # Handle OTP verification
            if request.form.get('submit') == 'verify':
                submitted_otp = request.form.get('email_otp', '')
                print(f"🔍 OTP VERIFICATION ATTEMPT:")
                print(f"   📧 User: {user.email}")
                print(f"   🔑 Submitted OTP: '{submitted_otp}'")
                print(f"   🔑 Stored OTP: '{user.email_otp}'")
                print(f"   ⏰ OTP Expires: {user.email_otp_expires}")
                print(f"   ⏰ Current Time: {datetime.utcnow()}")
                
                # Check if OTP exists and is not expired
                if not user.email_otp:
                    flash("No OTP found. Please request a new one.", "error")
                    return render_template("verify_account.html", user=user, email_form=email_form, resend_form=resend_form)
                
                if user.email_otp_expires and datetime.utcnow() > user.email_otp_expires:
                    flash("OTP has expired. Please request a new one.", "error")
                    return render_template("verify_account.html", user=user, email_form=email_form, resend_form=resend_form)
                
                # Verify OTP
                if submitted_otp == user.email_otp:
                    print(f"✅ OTP VERIFICATION SUCCESSFUL!")
                    user.email_verified = True
                    user.email_otp = None
                    user.email_otp_expires = None
                    db.session.commit()
                    flash("Account verified successfully! You can now log in.", "success")
                    return redirect(url_for("login"))
                else:
                    print(f"❌ OTP VERIFICATION FAILED!")
                    flash("Invalid OTP. Please try again.", "error")
                    return render_template("verify_account.html", user=user, email_form=email_form, resend_form=resend_form)
            
            # Handle resend OTP
            elif request.form.get('submit') == 'resend':
                print(f"🔄 RESEND OTP REQUESTED:")
                print(f"   📧 User: {user.email}")
                
                # Generate new OTP
                new_otp = generate_otp()
                user.email_otp = new_otp
                user.email_otp_expires = datetime.utcnow() + timedelta(minutes=10)
                db.session.commit()
                
                # Send new OTP
                try:
                    email_sent = send_email_otp(user.email, new_otp)
                    if email_sent:
                        print(f"✅ New OTP email sent successfully!")
                        flash("New OTP sent to your email.", "success")
                    else:
                        print(f"⚠️ New OTP email failed, but OTP is available above")
                        flash(f"New OTP: {new_otp} (Email delivery failed)", "warning")
                except Exception as e:
                    print(f"❌ New OTP email error: {e}")
                    flash(f"New OTP: {new_otp} (Email delivery failed)", "warning")
                
                return render_template("verify_account.html", user=user, email_form=email_form, resend_form=resend_form)
        
        return render_template("verify_account.html", user=user, email_form=email_form, resend_form=resend_form)



    # OTP verification routes - using custom email and SMS verification


    
    @app.route("/upload-document", methods=["POST"])
    @login_required
    def upload_document():
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            accepted_types = ', '.join(ALLOWED_EXTENSIONS)
            return jsonify({
                'error': f'File type not allowed. Accepted formats: {accepted_types}',
                'accepted_formats': list(ALLOWED_EXTENSIONS)
            }), 400
        
        try:
            # Create user-specific directory
            user_email = current_user.email
            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_email)
            
            print(f"📁 ATTEMPTING TO CREATE USER DIRECTORY:")
            print(f"   📧 User: {user_email}")
            print(f"   📂 Base Upload Folder: {app.config['UPLOAD_FOLDER']}")
            print(f"   📂 User Directory: {user_dir}")
            print(f"   📂 Base folder exists: {os.path.exists(app.config['UPLOAD_FOLDER'])}")
            
            # Ensure base upload folder exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                print(f"⚠️ Base upload folder doesn't exist, creating it...")
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                print(f"✅ Base upload folder created: {os.path.exists(app.config['UPLOAD_FOLDER'])}")
            
            # Create user directory
            try:
                os.makedirs(user_dir, exist_ok=True)
                print(f"✅ User directory creation attempted")
            except Exception as dir_error:
                print(f"❌ Error creating user directory: {dir_error}")
                raise Exception(f"Failed to create user directory: {dir_error}")
            
            # Verify directory was created
            if not os.path.exists(user_dir):
                print(f"❌ User directory still doesn't exist after creation attempt")
                raise Exception("User directory creation failed")
            
            print(f"📁 USER DIRECTORY CREATED SUCCESSFULLY:")
            print(f"   📂 Directory: {user_dir}")
            print(f"   ✅ Directory exists: {os.path.exists(user_dir)}")
            print(f"   📂 Directory is writable: {os.access(user_dir, os.W_OK)}")
            print(f"   📂 Directory contents: {os.listdir(user_dir) if os.path.exists(user_dir) else 'N/A'}")
            
            # Secure filename and save file
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(user_dir, unique_filename)
            
            print(f"📄 ATTEMPTING TO SAVE FILE:")
            print(f"   📁 User Dir: {user_dir}")
            print(f"   📄 Original Name: {filename}")
            print(f"   🔐 Stored Name: {unique_filename}")
            print(f"   📍 Full Path: {file_path}")
            print(f"   📂 Target directory writable: {os.access(user_dir, os.W_OK)}")
            print(f"   📂 Current working directory: {os.getcwd()}")
            print(f"   📂 File object type: {type(file)}")
            
            # Save file with multiple attempts
            file_saved = False
            save_errors = []
            
            # Method 1: Direct save
            try:
                print(f"🔄 Attempting direct file save...")
                file.save(file_path)
                print(f"✅ Direct file save successful")
                file_saved = True
            except Exception as save_error:
                error_msg = f"Direct save failed: {save_error}"
                print(f"❌ {error_msg}")
                save_errors.append(error_msg)
            
            # Method 2: Copy file content if direct save failed
            if not file_saved:
                try:
                    print(f"🔄 Attempting file copy method...")
                    file.seek(0)  # Reset file pointer
                    with open(file_path, 'wb') as f:
                        f.write(file.read())
                    print(f"✅ File copy method successful")
                    file_saved = True
                except Exception as copy_error:
                    error_msg = f"File copy failed: {copy_error}"
                    print(f"❌ {error_msg}")
                    save_errors.append(error_msg)
            
            # Method 3: Stream copy if other methods failed
            if not file_saved:
                try:
                    print(f"🔄 Attempting stream copy method...")
                    file.seek(0)  # Reset file pointer
                    with open(file_path, 'wb') as f:
                        chunk = file.read(8192)  # 8KB chunks
                        while chunk:
                            f.write(chunk)
                            chunk = file.read(8192)
                    print(f"✅ Stream copy method successful")
                    file_saved = True
                except Exception as stream_error:
                    error_msg = f"Stream copy failed: {stream_error}"
                    print(f"❌ {error_msg}")
                    save_errors.append(error_msg)
            
            if not file_saved:
                print(f"❌ ALL FILE SAVE METHODS FAILED:")
                for error in save_errors:
                    print(f"   ❌ {error}")
                raise Exception(f"All file save methods failed: {'; '.join(save_errors)}")
            
            # Verify file was saved
            if not os.path.exists(file_path):
                print(f"❌ File doesn't exist after save operation")
                raise Exception("File save operation failed")
            
            # Get file size
            try:
                file_size = os.path.getsize(file_path)
                print(f"✅ File size retrieved: {file_size} bytes")
            except Exception as size_error:
                print(f"❌ Error getting file size: {size_error}")
                file_size = 0
            
            print(f"📄 FILE SAVED SUCCESSFULLY:")
            print(f"   📁 User Dir: {user_dir}")
            print(f"   📄 Original Name: {filename}")
            print(f"   🔐 Stored Name: {unique_filename}")
            print(f"   📍 Full Path: {file_path}")
            print(f"   ✅ File exists: {os.path.exists(file_path)}")
            print(f"   📏 File size: {file_size} bytes")
            print(f"   📂 Directory contents after save: {os.listdir(user_dir)}")
            
            # Save document to database
            document = Document(
                user_email=current_user.email,
                filename=unique_filename,
                original_filename=filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                file_type=file.content_type
            )
            db.session.add(document)
            
            # Create a new chat for this document
            chat = Chat(
                user_email=current_user.email,
                document_id=document.id,
                title=f"Chat about {filename}"
            )
            db.session.add(chat)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'document_id': document.id,
                'chat_id': chat.id,
                'filename': filename
            })
            
        except Exception as e:
            db.session.rollback()
            # Clean up uploaded file if database save fails
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': str(e)}), 500

    @app.route("/accepted-file-types", methods=["GET"])
    def accepted_file_types():
        """Get the list of accepted file types for uploads"""
        return jsonify({
            'accepted_formats': list(ALLOWED_EXTENSIONS),
            'max_file_size_mb': MAX_FILE_SIZE // (1024 * 1024),
            'file_types_description': {
                'pdf': 'Portable Document Format',
                'docx': 'Microsoft Word Document',
                'txt': 'Plain Text File',
                'rtf': 'Rich Text Format',
                'md': 'Markdown Document',
                'odt': 'OpenDocument Text'
            }
        })

    @app.route("/user-documents", methods=["GET"])
    @login_required
    def get_user_documents():
        """Get all documents for the current user"""
        try:
            documents = Document.query.filter_by(user_email=current_user.email).order_by(Document.uploaded_at.desc()).all()
            
            docs_list = []
            for doc in documents:
                # Check if file still exists on disk
                file_exists = os.path.exists(doc.file_path)
                
                docs_list.append({
                    'id': doc.id,
                    'filename': doc.original_filename,
                    'stored_filename': doc.filename,
                    'file_size': doc.file_size,
                    'file_type': doc.file_type,
                    'uploaded_at': doc.uploaded_at.isoformat(),
                    'file_exists': file_exists,
                    'file_path': doc.file_path
                })
            
            return jsonify({
                'success': True,
                'documents': docs_list,
                'total_count': len(docs_list)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route("/delete-document/<int:document_id>", methods=["DELETE"])
    @login_required
    def delete_document(document_id):
        """Delete a document and its associated files"""
        try:
            document = Document.query.filter_by(id=document_id, user_email=current_user.email).first()
            if not document:
                return jsonify({'error': 'Document not found'}), 404
            
            # Delete file from disk
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
                print(f"✅ File deleted from disk: {document.file_path}")
            
            # Delete associated chats and messages
            chats = Chat.query.filter_by(document_id=document_id).all()
            for chat in chats:
                ChatMessage.query.filter_by(chat_id=chat.id).delete()
                db.session.delete(chat)
            
            # Delete document from database
            db.session.delete(document)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Document deleted successfully'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route("/user-storage", methods=["GET"])
    @login_required
    def get_user_storage():
        """Get storage information for the current user"""
        try:
            user_email = current_user.email
            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_email)
            
            # Get user documents
            documents = Document.query.filter_by(user_email=user_email).all()
            
            # Calculate total storage used
            total_size = sum(doc.file_size for doc in documents)
            total_files = len(documents)
            
            # Check if user directory exists
            dir_exists = os.path.exists(user_dir)
            dir_size = 0
            
            if dir_exists:
                # Calculate actual directory size on disk
                for root, dirs, files in os.walk(user_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            dir_size += os.path.getsize(file_path)
                        except OSError:
                            pass
            
            return jsonify({
                'success': True,
                'user_email': user_email,
                'user_directory': user_dir,
                'directory_exists': dir_exists,
                'total_documents': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'actual_directory_size_bytes': dir_size,
                'actual_directory_size_mb': round(dir_size / (1024 * 1024), 2),
                'max_file_size_mb': MAX_FILE_SIZE // (1024 * 1024)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route("/cleanup-orphaned-files", methods=["POST"])
    @login_required
    def cleanup_orphaned_files():
        """Clean up orphaned files that exist on disk but not in database"""
        try:
            user_email = current_user.email
            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], user_email)
            
            if not os.path.exists(user_dir):
                return jsonify({'success': True, 'message': 'No user directory found', 'files_removed': 0})
            
            # Get all files in user directory
            files_on_disk = []
            for root, dirs, files in os.walk(user_dir):
                for file in files:
                    files_on_disk.append(os.path.join(root, file))
            
            # Get all files in database
            documents = Document.query.filter_by(user_email=user_email).all()
            db_files = [doc.file_path for doc in documents]
            
            # Find orphaned files
            orphaned_files = [f for f in files_on_disk if f not in db_files]
            
            # Remove orphaned files
            files_removed = 0
            for orphaned_file in orphaned_files:
                try:
                    os.remove(orphaned_file)
                    files_removed += 1
                    print(f"🗑️ Orphaned file removed: {orphaned_file}")
                except OSError as e:
                    print(f"❌ Failed to remove orphaned file {orphaned_file}: {e}")
            
            return jsonify({
                'success': True,
                'message': f'Cleanup completed. {files_removed} orphaned files removed.',
                'files_removed': files_removed,
                'total_files_on_disk': len(files_on_disk),
                'total_files_in_db': len(db_files),
                'orphaned_files_found': len(orphaned_files)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route("/chat-message", methods=["POST"])
    @login_required
    def chat_message():
        data = request.get_json()
        chat_id = data.get('chat_id')
        message_content = data.get('message')
        
        if not chat_id or not message_content:
            return jsonify({'error': 'Missing chat_id or message'}), 400
        
        # Verify chat belongs to current user
        chat = Chat.query.filter_by(id=chat_id, user_email=current_user.email).first()
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        try:
            # Save user message
            user_message = ChatMessage(
                chat_id=chat_id,
                role='user',
                content=message_content
            )
            db.session.add(user_message)
            
            # Generate AI response (placeholder for now)
            ai_response = generate_ai_response(message_content, chat.document_id)
            
            # Save AI response
            ai_message = ChatMessage(
                chat_id=chat_id,
                role='assistant',
                content=ai_response
            )
            db.session.add(ai_message)
            
            # Update chat timestamp
            chat.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'response': ai_response
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    def generate_ai_response(user_message, document_id):
        """Placeholder function for AI response generation"""
        # This would integrate with an actual AI service
        responses = [
            "Based on your document, I can see that this is an interesting topic. Could you be more specific about what you'd like to know?",
            "I've analyzed the content and found several key points. What aspect would you like me to focus on?",
            "The document contains valuable information about this subject. Let me know what specific questions you have.",
            "I can help you understand this better. What particular section or concept would you like me to explain?",
            "This is a comprehensive document with many insights. What specific area would you like to explore?"
        ]
        import random
        return random.choice(responses)

    @app.route("/get-chats")
    @login_required
    def get_chats():
        chats = Chat.query.filter_by(user_email=current_user.email).order_by(Chat.updated_at.desc()).all()
        chat_list = []
        for chat in chats:
            chat_data = {
                'id': chat.id,
                'title': chat.title,
                'document_name': chat.document.original_filename if chat.document else 'General Chat',
                'updated_at': chat.updated_at.strftime('%Y-%m-%d %H:%M'),
                'message_count': chat.messages.count()
            }
            chat_list.append(chat_data)
        return jsonify(chat_list)

    @app.route("/get-chat-messages/<int:chat_id>")
    @login_required
    def get_chat_messages(chat_id):
        chat = Chat.query.filter_by(id=chat_id, user_email=current_user.email).first()
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        messages = []
        for msg in chat.messages:
            message_data = {
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M')
            }
            messages.append(message_data)
        
        return jsonify(messages)

    # Test route to verify OTP generation works
    @app.route("/test-otp")
    def test_otp():
        print("\n🧪 TESTING OTP GENERATION...")
        from otp_utils import generate_otp, get_otp_expiry_time
        
        test_otp = generate_otp()
        expiry = get_otp_expiry_time()
        
        print("🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨")
        print("🧪 TEST OTP GENERATED!")
        print("🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨")
        print(f"🔐 Test OTP Code: {test_otp}")
        print(f"⏰ Expires: {expiry}")
        print("🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨")
        
        return f"Test OTP generated: {test_otp} - Check terminal for details!"

    @app.route("/db-health")
    def db_health():
        """Check database connection health"""
        try:
            # Test basic connection
            db.session.execute("SELECT 1")
            db.session.commit()
            
            # Test user table access
            user_count = User.query.count()
            
            return jsonify({
                'status': 'healthy',
                'message': 'Database connection is working',
                'user_count': user_count,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            print(f"❌ Database health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'message': 'Database connection failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    @app.route("/db-diagnostic")
    def db_diagnostic():
        """Comprehensive database diagnostic information"""
        try:
            # Get database configuration
            db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "Not set")
            db_options = app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
            
            # Test connection
            connection_test = test_database_connection()
            
            # Get environment info
            env_info = {
                'DATABASE_URL_set': bool(os.getenv("DATABASE_URL")),
                'DATABASE_URL_length': len(os.getenv("DATABASE_URL", "")) if os.getenv("DATABASE_URL") else 0,
                'DATABASE_URL_preview': os.getenv("DATABASE_URL", "")[:50] + "..." if os.getenv("DATABASE_URL") and len(os.getenv("DATABASE_URL", "")) > 50 else os.getenv("DATABASE_URL", "Not set"),
                'python_version': os.sys.version,
                'current_working_directory': os.getcwd(),
                'app_root': os.path.dirname(os.path.abspath(__file__))
            }
            
            # Test specific database operations
            tests = {}
            
            # Test 1: Basic connection
            try:
                db.session.execute(text("SELECT 1"))
                db.session.commit()
                tests['basic_connection'] = {'status': 'success', 'message': 'Basic connection test passed'}
            except Exception as e:
                tests['basic_connection'] = {'status': 'failed', 'error': str(e)}
            
            # Test 2: Table access
            try:
                user_count = User.query.count()
                tests['table_access'] = {'status': 'success', 'message': f'User table accessible, count: {user_count}'}
            except Exception as e:
                tests['table_access'] = {'status': 'failed', 'error': str(e)}
            
            # Test 3: Connection pool
            try:
                engine = db.engine
                pool = engine.pool
                tests['connection_pool'] = {
                    'status': 'success', 
                    'message': f'Pool size: {pool.size()}, checked out: {pool.checkedout()}, overflow: {pool.overflow()}'
                }
            except Exception as e:
                tests['connection_pool'] = {'status': 'failed', 'error': str(e)}
            
            return jsonify({
                'status': 'diagnostic_complete',
                'timestamp': datetime.utcnow().isoformat(),
                'connection_test': {
                    'success': connection_test[0],
                    'message': connection_test[1]
                },
                'database_config': {
                    'uri_preview': db_uri[:50] + "..." if len(db_uri) > 50 else db_uri,
                    'engine_options': db_options
                },
                'environment_info': env_info,
                'tests': tests
            })
            
        except Exception as e:
            return jsonify({
                'status': 'diagnostic_failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    @app.route("/db-simple-test")
    def db_simple_test():
        """Simple database connection test without complex operations"""
        try:
            # Just test if we can execute a simple query
            result = db.session.execute(text("SELECT 1 as test")).fetchone()
            if result and result[0] == 1:
                return jsonify({
                    'status': 'success',
                    'message': 'Database connection is working',
                    'test_result': result[0],
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Database query returned unexpected result',
                    'timestamp': datetime.utcnow().isoformat()
                }), 500
                
        except Exception as e:
            error_msg = str(e)
            
            # Provide helpful error information
            if "SSL connection has been closed unexpectedly" in error_msg:
                suggestion = "SSL connection issue - check your internet connection and Neon database status"
            elif "connection" in error_msg.lower():
                suggestion = "Connection issue - verify your DATABASE_URL and internet connection"
            elif "authentication" in error_msg.lower():
                suggestion = "Authentication issue - check your database credentials"
            elif "database" in error_msg.lower() and "does not exist" in error_msg.lower():
                suggestion = "Database doesn't exist - check the database name in your DATABASE_URL"
            elif "timeout" in error_msg.lower():
                suggestion = "Connection timeout - check your internet connection and firewall settings"
            elif "psycopg2" in error_msg.lower():
                suggestion = "psycopg2 driver not installed - run: pip install psycopg2-binary"
            elif "no module named" in error_msg.lower():
                suggestion = "Missing Python module - run: pip install -r requirements.txt"
            else:
                suggestion = f"Unknown database error: {error_msg[:100]}"
            
            return jsonify({
                'status': 'failed',
                'message': 'Database connection test failed',
                'error': error_msg,
                'suggestion': suggestion,
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    @app.route("/test-directory", methods=["GET"])
    @login_required
    def test_directory():
        """Test directory creation and file system access"""
        try:
            user_email = current_user.email
            base_upload = app.config['UPLOAD_FOLDER']
            user_dir = os.path.join(base_upload, user_email)
            
            # Test base directory
            base_exists = os.path.exists(base_upload)
            base_writable = os.access(base_upload, os.W_OK) if base_exists else False
            
            # Test user directory
            user_exists = os.path.exists(user_dir)
            user_writable = os.access(user_dir, os.W_OK) if user_exists else False
            
            # Try to create directories
            try:
                os.makedirs(base_upload, exist_ok=True)
                base_created = True
            except Exception as e:
                base_created = False
                base_error = str(e)
            
            try:
                os.makedirs(user_dir, exist_ok=True)
                user_created = True
            except Exception as e:
                user_created = False
                user_error = str(e)
            
            # Test file creation
            test_file_path = os.path.join(user_dir, 'test.txt')
            test_file_created = False
            try:
                with open(test_file_path, 'w') as f:
                    f.write('test')
                test_file_created = True
                os.remove(test_file_path)  # Clean up
            except Exception as e:
                test_file_error = str(e)
            
            return jsonify({
                'success': True,
                'user_email': user_email,
                'base_upload_folder': base_upload,
                'base_exists': base_exists,
                'base_writable': base_writable,
                'base_created': base_created,
                'base_error': base_error if not base_created else None,
                'user_directory': user_dir,
                'user_exists': user_exists,
                'user_writable': user_writable,
                'user_created': user_created,
                'user_error': user_error if not user_created else None,
                'test_file_created': test_file_created,
                'test_file_error': test_file_error if not test_file_created else None,
                'current_working_directory': os.getcwd(),
                'python_path': os.path.abspath('.'),
                'absolute_base_path': os.path.abspath(base_upload)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route("/create-directories", methods=["POST"])
    @login_required
    def create_directories():
        """Manually create directory structure for testing"""
        try:
            user_email = current_user.email
            base_upload = app.config['UPLOAD_FOLDER']
            user_dir = os.path.join(base_upload, user_email)
            
            print(f"🔧 MANUALLY CREATING DIRECTORY STRUCTURE:")
            print(f"   📧 User: {user_email}")
            print(f"   📂 Base: {base_upload}")
            print(f"   📂 User: {user_dir}")
            
            # Create base directory
            try:
                os.makedirs(base_upload, exist_ok=True)
                print(f"✅ Base directory created/exists: {os.path.exists(base_upload)}")
            except Exception as e:
                print(f"❌ Base directory creation failed: {e}")
                return jsonify({'error': f'Base directory creation failed: {e}'}), 500
            
            # Create user directory
            try:
                os.makedirs(user_dir, exist_ok=True)
                print(f"✅ User directory created/exists: {os.path.exists(user_dir)}")
            except Exception as e:
                print(f"❌ User directory creation failed: {e}")
                return jsonify({'error': f'User directory creation failed: {e}'}), 500
            
            # Test write access
            test_file = os.path.join(user_dir, 'test_write.txt')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"✅ Write access confirmed")
            except Exception as e:
                print(f"❌ Write access failed: {e}")
                return jsonify({'error': f'Write access test failed: {e}'}), 500
            
            return jsonify({
                'success': True,
                'message': 'Directories created successfully',
                'base_directory': base_upload,
                'user_directory': user_dir,
                'base_exists': os.path.exists(base_upload),
                'user_exists': os.path.exists(user_dir),
                'base_writable': os.access(base_upload, os.W_OK),
                'user_writable': os.access(user_dir, os.W_OK)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route("/upload-config", methods=["GET"])
    @login_required
    def upload_config():
        """Show current upload folder configuration (requires login)"""
        try:
            return jsonify({
                'success': True,
                'project_root': PROJECT_ROOT,
                'upload_folder': UPLOAD_FOLDER,
                'upload_folder_exists': os.path.exists(UPLOAD_FOLDER),
                'upload_folder_absolute': os.path.abspath(UPLOAD_FOLDER),
                'current_working_directory': os.getcwd(),
                'src_directory': os.path.dirname(os.path.abspath(__file__)),
                'parent_of_src': os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'script_location': os.path.abspath(__file__),
                'src_folder_in_project_root': os.path.exists(os.path.join(PROJECT_ROOT, 'src')),
                'project_root_contents': os.listdir(PROJECT_ROOT) if os.path.exists(PROJECT_ROOT) else []
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500



    @app.route("/migrate-uploads", methods=["POST"])
    @login_required
    def migrate_uploads():
        """Migrate existing uploads from src/uploads to root uploads directory"""
        try:
            # Get the old upload directory (src/uploads)
            old_upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
            new_upload_dir = UPLOAD_FOLDER
            
            print(f"🔄 MIGRATING UPLOADS:")
            print(f"   📂 From: {old_upload_dir}")
            print(f"   📂 To: {new_upload_dir}")
            
            if not os.path.exists(old_upload_dir):
                return jsonify({
                    'success': False,
                    'message': 'No old upload directory found to migrate',
                    'old_directory': old_upload_dir
                }), 404
            
            # Ensure new directory exists
            os.makedirs(new_upload_dir, exist_ok=True)
            
            migrated_files = []
            failed_files = []
            
            # Walk through old directory structure
            for root, dirs, files in os.walk(old_upload_dir):
                # Calculate relative path from old upload dir
                rel_path = os.path.relpath(root, old_upload_dir)
                if rel_path == '.':
                    rel_path = ''
                
                # Create corresponding directory in new location
                new_root = os.path.join(new_upload_dir, rel_path) if rel_path else new_upload_dir
                os.makedirs(new_root, exist_ok=True)
                
                # Move files
                for file in files:
                    old_file_path = os.path.join(root, file)
                    new_file_path = os.path.join(new_root, file)
                    
                    try:
                        # Check if file already exists in new location
                        if os.path.exists(new_file_path):
                            # Generate unique name with timestamp
                            name, ext = os.path.splitext(file)
                            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                            new_file_path = os.path.join(new_root, f"{name}_{timestamp}{ext}")
                        
                        # Move file
                        import shutil
                        shutil.move(old_file_path, new_file_path)
                        migrated_files.append({
                            'old_path': old_file_path,
                            'new_path': new_file_path,
                            'size': os.path.getsize(new_file_path)
                        })
                        print(f"✅ Migrated: {file} -> {os.path.relpath(new_file_path, new_upload_dir)}")
                        
                    except Exception as e:
                        failed_files.append({
                            'file': file,
                            'error': str(e)
                        })
                        print(f"❌ Failed to migrate {file}: {e}")
            
            # Remove old directory if all files migrated successfully
            if failed_files:
                print(f"⚠️ Some files failed to migrate, keeping old directory")
            else:
                try:
                    shutil.rmtree(old_upload_dir)
                    print(f"🗑️ Old upload directory removed: {old_upload_dir}")
                except Exception as e:
                    print(f"⚠️ Could not remove old directory: {e}")
            
            return jsonify({
                'success': True,
                'message': f'Migration completed. {len(migrated_files)} files migrated.',
                'migrated_files': migrated_files,
                'failed_files': failed_files,
                'old_directory': old_upload_dir,
                'new_directory': new_upload_dir,
                'total_migrated': len(migrated_files),
                'total_failed': len(failed_files)
            })
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route("/cleanup-old-uploads", methods=["POST"])
    @login_required
    def cleanup_old_uploads():
        """Remove the old src/uploads directory after migration"""
        try:
            old_upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
            
            if not os.path.exists(old_upload_dir):
                return jsonify({
                    'success': False,
                    'message': 'Old upload directory does not exist',
                    'old_directory': old_upload_dir
                }), 404
            
            # Check if directory is empty
            if os.listdir(old_upload_dir):
                return jsonify({
                    'success': False,
                    'message': 'Old upload directory is not empty. Please migrate files first.',
                    'old_directory': old_upload_dir,
                    'contents': os.listdir(old_upload_dir)
                }), 400
            
            # Remove empty directory
            import shutil
            shutil.rmtree(old_upload_dir)
            
            return jsonify({
                'success': True,
                'message': 'Old upload directory removed successfully',
                'old_directory': old_upload_dir
            })
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route("/test-file-creation", methods=["POST"])
    @login_required
    def test_file_creation():
        """Test file creation with different methods"""
        try:
            user_email = current_user.email
            base_upload = app.config['UPLOAD_FOLDER']
            user_dir = os.path.join(base_upload, user_email)
            
            # Ensure directories exist
            os.makedirs(base_upload, exist_ok=True)
            os.makedirs(user_dir, exist_ok=True)
            
            test_file_path = os.path.join(user_dir, 'test_file_creation.txt')
            test_content = 'This is a test file created at ' + datetime.utcnow().isoformat()
            
            results = {}
            
            # Test 1: Direct file write
            try:
                with open(test_file_path, 'w') as f:
                    f.write(test_content)
                results['direct_write'] = {'success': True, 'file_exists': os.path.exists(test_file_path)}
                if os.path.exists(test_file_path):
                    os.remove(test_file_path)
            except Exception as e:
                results['direct_write'] = {'success': False, 'error': str(e)}
            
            # Test 2: Binary file write
            try:
                with open(test_file_path, 'wb') as f:
                    f.write(test_content.encode('utf-8'))
                results['binary_write'] = {'success': True, 'file_exists': os.path.exists(test_file_path)}
                if os.path.exists(test_file_path):
                    os.remove(test_file_path)
            except Exception as e:
                results['binary_write'] = {'success': False, 'error': str(e)}
            
            # Test 3: File with special characters in path
            special_path = os.path.join(user_dir, 'test_file_with_spaces_and_special_chars_@#$%.txt')
            try:
                with open(special_path, 'w') as f:
                    f.write(test_content)
                results['special_chars'] = {'success': True, 'file_exists': os.path.exists(special_path)}
                if os.path.exists(special_path):
                    os.remove(special_path)
            except Exception as e:
                results['special_chars'] = {'success': False, 'error': str(e)}
            
            return jsonify({
                'success': True,
                'user_email': user_email,
                'base_directory': base_upload,
                'user_directory': user_dir,
                'test_results': results,
                'current_working_directory': os.getcwd(),
                'absolute_paths': {
                    'base': os.path.abspath(base_upload),
                    'user': os.path.abspath(user_dir)
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route("/update-chat-title", methods=["POST"])
    @login_required
    def update_chat_title():
        """Update the title of a chat"""
        try:
            data = request.get_json()
            chat_id = data.get('chat_id')
            new_title = data.get('title')
            
            if not chat_id or not new_title:
                return jsonify({'error': 'Missing chat_id or title'}), 400
            
            # Validate title length
            if len(new_title) > 255:
                return jsonify({'error': 'Title too long (max 255 characters)'}), 400
            
            # Find the chat and verify ownership
            chat = Chat.query.filter_by(
                id=chat_id, 
                user_email=current_user.email
            ).first()
            
            if not chat:
                return jsonify({'error': 'Chat not found or access denied'}), 404
            
            # Update the title
            old_title = chat.title
            chat.title = new_title
            
            try:
                db.session.commit()
                print(f"✅ Chat title updated: '{old_title}' -> '{new_title}' (Chat ID: {chat_id}, User: {current_user.email})")
                return jsonify({
                    'success': True,
                    'message': 'Chat title updated successfully',
                    'old_title': old_title,
                    'new_title': new_title
                })
            except Exception as db_error:
                db.session.rollback()
                print(f"❌ Database error updating chat title: {db_error}")
                return jsonify({'error': 'Failed to update chat title in database'}), 500
                
        except Exception as e:
            print(f"❌ Error updating chat title: {e}")
            return jsonify({'error': str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    print(f"🌐 Server starting at http://127.0.0.1:5000")
    app.run(debug=True) 