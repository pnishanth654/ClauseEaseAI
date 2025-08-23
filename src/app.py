import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from extensions import db, login_manager, mail, limiter
from models import User
from forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, EmailOTPForm, ResendOTPForm
from email_utils import generate_reset_token, verify_reset_token, send_password_reset
from otp_utils import generate_otp, get_otp_expiry_time, send_email_otp, is_otp_expired
import phonenumbers

load_dotenv()


def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')

    # Core config
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Database configuration - EXCLUSIVELY use Neon PostgreSQL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env file!")
        print("🔧 Please set DATABASE_URL in your .env file")
        print("📖 Example: DATABASE_URL=postgresql+psycopg2://user:pass@host/dbname")
        exit(1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    print(f"🗄️  Using Neon PostgreSQL database")
    print(f"🔗 Database: {database_url.split('@')[1] if '@' in database_url else 'Connected'}")
    
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
    
    # Check if email is properly configured
    if (app.config["MAIL_USERNAME"] == "your-email@gmail.com" or 
        app.config["MAIL_PASSWORD"] == "your-app-password"):
        print("⚠️  WARNING: Email not properly configured!")
        print("   Please create a .env file with your Gmail credentials:")
        print("   MAIL_USERNAME=your-actual-email@gmail.com")
        print("   MAIL_PASSWORD=your-gmail-app-password")
        print("   Note: Use Gmail App Password, not your regular password")
        print("   OTP codes will be shown in terminal only until email is configured")
    else:
        print("✅ Email configuration loaded successfully!")
        print(f"   Server: {app.config['MAIL_SERVER']}")
        print(f"   Port: {app.config['MAIL_PORT']}")
        print(f"   Username: {app.config['MAIL_USERNAME']}")
        print(f"   TLS: {app.config['MAIL_USE_TLS']}")
        print(f"   Timeout: {app.config['MAIL_TIMEOUT']}s")

    # OTP configuration - using custom email and SMS verification

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    CSRFProtect(app)

    # Try to create database tables
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully in Neon PostgreSQL!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("🔧 Please check your DATABASE_URL in .env file")
            print("📖 Make sure your Neon database is running and accessible")
            exit(1)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    @limiter.limit("5 per minute")
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        
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
            
            try:
                # Save the user to database
                db.session.add(user)
                db.session.commit()
                print(f"✅ User saved to database with ID: {user.id}")
                
                # Auto-generate OTP for immediate verification
                email_otp = generate_otp()
                user.email_otp = email_otp
                user.email_otp_expires = get_otp_expiry_time()
                db.session.commit()
                
                # Show OTP in terminal prominently
                print("🚨" * 20)
                print("🚨 OTP GENERATED FOR NEW USER 🚨")
                print("🚨" * 20)
                print(f"📧 Email: {user.email}")
                print(f"🔐 OTP Code: {email_otp}")
                print(f"⏰ Expires: {user.email_otp_expires}")
                print("🚨" * 20)
                
                # Try to send email OTP
                try:
                    print(f"📧 Attempting to send email to: {user.email}")
                    email_sent = send_email_otp(user.email, email_otp)
                    if email_sent:
                        print(f"✅ Email sent successfully!")
                        flash("Registration successful! OTP sent to your email. Please verify your account.", "success")
                    else:
                        print(f"⚠️ Email delivery failed, but OTP is available above")
                        flash("Registration successful! OTP sent to your email. Please check your inbox.", "warning")
                except Exception as e:
                    print(f"❌ Email sending error: {e}")
                    flash("Registration successful! OTP sent to your email. Please check your inbox.", "warning")
                
                print(f"🔄 Redirecting to verification page for user ID: {user.id}")
                return redirect(url_for("verify_account", user_id=user.id))
            except IntegrityError:
                db.session.rollback()
                flash("Email or phone already registered.", "error")
        
        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    @limiter.limit("5 per minute")
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        
        form = LoginForm()
        if form.validate_on_submit():
            identifier = form.identifier.data.strip()
            
            # Try to find user by email or phone
            user = None
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
            
            # Flow 1: User not found
            if not user:
                flash("No user associated with this email.", "error")
                return redirect(url_for("register"))
            
            # Flow 2: User exists but wrong password
            if not user.check_password(form.password.data):
                flash("Invalid password. Please try again.", "error")
                return render_template("login.html", form=form)
            
            # Flow 3: User exists and password correct, but not verified
            if not user.email_verified:
                flash("Account not verified. Please complete verification to continue.", "info")
                return redirect(url_for("verify_account", user_id=user.id))
            
            # Flow 4: User exists, password correct, and verified - LOGIN SUCCESS
            login_user(user)
            flash("Login successful! Welcome back.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @app.route("/forgot-password", methods=["GET", "POST"])
    @limiter.limit("3 per minute")
    def forgot_password():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        
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
                return redirect(url_for("verify_account", user_id=user.id))
            
            # Flow 3: User found and verified, but no email associated
            if not user.email:
                flash("No email associated with this account. Cannot send password reset.", "error")
                return render_template("forgot_password.html", form=form)
            
            # Flow 4: User found, verified, and has email - SEND RESET LINK
            token = generate_reset_token(user.id)
            email_sent = send_password_reset(user.email, token)
            if email_sent:
                flash("Password reset link sent to your email.", "success")
            else:
                flash("Error sending email. Please check your email configuration.", "error")
        
        return render_template("forgot_password.html", form=form)

    @app.route("/reset-password/<token>", methods=["GET", "POST"])
    def reset_password(token):
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        
        user_id = verify_reset_token(token)
        if not user_id:
            flash("Invalid or expired reset link.", "error")
            return redirect(url_for("forgot_password"))
        
        user = User.query.get(user_id)
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("forgot_password"))
        
        form = ResetPasswordForm()
        if form.validate_on_submit():
            user.set_password(form.password.data)
            db.session.commit()
            flash("Password updated successfully! Please log in.", "success")
            return redirect(url_for("login"))
        
        return render_template("reset_password.html", form=form)

    @app.route("/verify-account/<int:user_id>", methods=["GET", "POST"])
    def verify_account(user_id):
        user = User.query.get_or_404(user_id)
        
        # Debug: Print user state
        print(f"\n🔍 VERIFICATION PAGE LOADED:")
        print(f"📧 User ID: {user.id}")
        print(f"📧 Email: {user.email}")
        print(f"📧 Email Verified: {user.email_verified}")
        print(f"📧 Has OTP: {user.email_otp is not None}")
        print(f"📧 OTP Value: {user.email_otp}")
        
        # Check if user is already verified
        if user.email_verified:
            flash("Account already verified!", "info")
            return redirect(url_for("login"))
        
        # Check if user needs a new OTP (expired or doesn't have one)
        needs_new_otp = False
        if not user.email_otp:
            print(f"⚠️ User has no OTP, generating new one...")
            needs_new_otp = True
        elif is_otp_expired(user.email_otp_expires):
            print(f"⚠️ OTP expired on page load, regenerating...")
            needs_new_otp = True
        
        if needs_new_otp:
            email_otp = generate_otp()
            user.email_otp = email_otp
            user.email_otp_expires = get_otp_expiry_time()
            db.session.commit()
            
            print(f"🔄 New OTP generated on page load: {email_otp}")
            
            # Send the new OTP via email
            try:
                print(f"📧 Attempting to send new OTP to: {user.email}")
                email_sent = send_email_otp(user.email, email_otp)
                if email_sent:
                    print(f"✅ New OTP email sent successfully!")
                    flash("New OTP generated and sent to your email.", "info")
                else:
                    print(f"⚠️ Email delivery failed for new OTP")
                    flash("New OTP generated and sent to your email.", "info")
            except Exception as e:
                print(f"❌ Error sending new OTP email: {e}")
                flash("New OTP generated and sent to your email.", "info")
        
        email_form = EmailOTPForm()
        resend_form = ResendOTPForm()
        
        if request.method == "POST":
            # Check if OTP verification form was submitted
            if 'email_otp' in request.form:
                print(f"\n🔍 OTP VERIFICATION ATTEMPT:")
                print(f"📧 User ID: {user.id}")
                print(f"📧 Submitted OTP: {request.form.get('email_otp')}")
                print(f"📧 Stored OTP: {user.email_otp}")
                print(f"📧 OTP Expires: {user.email_otp_expires}")
                
                submitted_otp = request.form.get('email_otp')
                
                # Check if current OTP is expired and regenerate if needed
                if user.email_otp and is_otp_expired(user.email_otp_expires):
                    print(f"⚠️ Current OTP is expired, regenerating...")
                    email_otp = generate_otp()
                    user.email_otp = email_otp
                    user.email_otp_expires = get_otp_expiry_time()
                    db.session.commit()
                    
                    print(f"🔄 New OTP generated: {email_otp}")
                    flash("Previous OTP expired. New OTP generated and sent to your email.", "info")
                    return redirect(url_for("verify_account", user_id=user.id))
                
                if submitted_otp and submitted_otp == user.email_otp and not is_otp_expired(user.email_otp_expires):
                    user.email_verified = True
                    user.email_otp = None
                    user.email_otp_expires = None
                    db.session.commit()
                    flash("Email verified successfully! Please log in to continue.", "success")
                    return redirect(url_for("login"))
                else:
                    flash("Invalid or expired email verification code.", "error")
                    print(f"❌ OTP verification failed!")
                    if submitted_otp != user.email_otp:
                        print(f"   - Submitted OTP ({submitted_otp}) != Stored OTP ({user.email_otp})")
                    if is_otp_expired(user.email_otp_expires):
                        print(f"   - OTP is expired")
            
            # Check if resend OTP form was submitted
            elif resend_form.submit.data:
                print(f"\n🔍 REQUEST OTP BUTTON CLICKED!")
                print(f"📧 User ID: {user.id}")
                print(f"📧 User Email: {user.email}")
                print(f"📧 Email Verified: {user.email_verified}")
                
                # Generate and send OTP to the primary contact method
                if user.email and not user.email_verified:
                    email_otp = generate_otp()
                    user.email_otp = email_otp
                    user.email_otp_expires = get_otp_expiry_time()
                    
                    print("\n" + "🚨" * 20)
                    print("🚨 OTP GENERATED AND SENT! 🚨")
                    print("🚨" * 20)
                    print(f"📧 Email: {user.email}")
                    print(f"🔐 OTP Code: {email_otp}")
                    print(f"⏰ Expires: {user.email_otp_expires}")
                    print("🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨")
                    
                    # Save OTP to database immediately
                    db.session.commit()
                    
                    # Show success message and redirect to same page (now with OTP input fields)
                    flash("OTP generated and sent to your email!", "success")
                    
                    # Try to send email OTP
                    try:
                        print(f"📧 Attempting to send email to: {user.email}")
                        email_sent = send_email_otp(user.email, email_otp)
                        if email_sent:
                            print(f"✅ Email sent successfully!")
                            flash("OTP sent to your email successfully!", "success")
                        else:
                            print(f"⚠️ Email delivery failed, but OTP is available above")
                            flash("OTP generated and sent to your email!", "warning")
                    except Exception as e:
                        print(f"❌ Email sending error: {e}")
                        print(f"⚠️ Email failed, but OTP is available above")
                        flash("OTP generated and sent to your email!", "warning")
                    
                    # Redirect to refresh the page and show OTP input fields
                    return redirect(url_for("verify_account", user_id=user.id))
                    


        
        return render_template("verify_account.html", 
                             user=user, 
                             email_form=email_form, 
                             resend_form=resend_form)

    # OTP verification routes - using custom email and SMS verification

    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html")
    
    # Test route to verify OTP generation works (terminal only)
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
        
        return "Test OTP generated - Check terminal for details!"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True) 