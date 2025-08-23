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
                
                # Show success message and redirect to verification page
                flash("Registration successful! OTP sent to your email. Please verify your account.", "success")
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
            try:
                send_password_reset(user.email, token)
                flash("Password reset link sent to your email.", "success")
            except Exception as e:
                flash("Error sending email. Please try again.", "error")
        
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
            # Check if new password is the same as current password
            if user.is_same_password(form.password.data):
                flash("❌ Your new password cannot be the same as your current password! Please choose a different password.", "error")
                return render_template("reset_password.html", form=form)
            
            # Set new password if it's different
            user.set_password(form.password.data)
            db.session.commit()
            flash("✅ Password updated successfully! Please log in.", "success")
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
        
        email_form = EmailOTPForm()
        resend_form = ResendOTPForm()
        
        if request.method == "POST":
            if email_form.submit.data and email_form.validate():
                if email_form.email_otp.data == user.email_otp and not is_otp_expired(user.email_otp_expires):
                    user.email_verified = True
                    user.email_otp = None
                    user.email_otp_expires = None
                    db.session.commit()
                    flash("Email verified successfully! Please log in to continue.", "success")
                    return redirect(url_for("login"))
                else:
                    flash("Invalid or expired email verification code.", "error")
            

            
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
                    flash(f"OTP generated! Check terminal for code: {email_otp}", "success")
                    
                    # Try to send email OTP in background (don't wait for it)
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

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True) 