import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from extensions import db, login_manager, mail, limiter
from models import User
from forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, EmailOTPForm, PhoneOTPForm, ResendOTPForm
from email_utils import generate_reset_token, verify_reset_token, send_password_reset
from otp_utils import generate_otp, get_otp_expiry_time, send_email_otp, send_sms_otp, is_otp_expired
import phonenumbers

load_dotenv()


def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')

    # Core config
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Force SQLite for testing (comment out to use PostgreSQL)
    # database_url = os.getenv("DATABASE_URL")
    # if database_url:
    #     app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    # else:
    # Database will be created in the root directory
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clauseease.db')
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    print(f"📁 Using SQLite database: {db_path}")
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Mail config
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "your-email@gmail.com")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "your-app-password")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", "your-email@gmail.com")

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
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            print("📁 The app will still run, but database features won't work")
            print("🔧 To fix: Set up your DATABASE_URL in .env file or use SQLite")

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
            user = User()
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            if form.email.data:
                user.email = form.email.data.lower()
            if form.phone.data:
                user.phone = form.phone.data
            user.gender = form.gender.data
            user.date_of_birth = datetime.strptime(form.date_of_birth.data, '%Y-%m-%d').date()
            user.set_password(form.password.data)
            
            try:
                db.session.add(user)
                db.session.commit()
                
                # Generate and send OTP to the primary contact method
                if user.email:
                    # Send OTP via email
                    email_otp = generate_otp()
                    user.email_otp = email_otp
                    user.email_otp_expires = get_otp_expiry_time()
                    
                    # Send email OTP
                    email_sent = send_email_otp(user.email, email_otp)
                    
                    if email_sent:
                        flash(f"Verification code sent to {user.email}", "success")
                    else:
                        # If email fails, show OTP in console for testing
                        print(f"🔐 EMAIL OTP FOR TESTING: {email_otp}")
                        print(f"📧 Email: {user.email}")
                        flash(f"Email delivery failed. Check console for OTP code.", "warning")
                elif user.phone:
                    # Send OTP via phone (SMS)
                    phone_otp = generate_otp()
                    user.phone_otp = phone_otp
                    user.phone_otp_expires = get_otp_expiry_time()
                    send_sms_otp(user.phone, phone_otp)
                    flash(f"Verification code sent to {user.phone}", "success")
                else:
                    flash("Please provide either email or phone number for verification", "warning")
                
                db.session.commit()
                
                flash("Account created! Please verify your email/phone to activate your account.", "success")
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
            
            if user and user.check_password(form.password.data):
                # Check if account is verified
                if not user.email_verified and not user.phone_verified:
                    flash("Please verify your account before logging in.", "error")
                    return redirect(url_for("verify_account", user_id=user.id))
                
                login_user(user)
                next_page = request.args.get("next")
                return redirect(next_page or url_for("dashboard"))
            else:
                flash("Invalid email/phone or password.", "error")
        
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
            
            if user and user.email:
                token = generate_reset_token(user.id)
                try:
                    send_password_reset(user.email, token)
                    flash("Password reset link sent to your email.", "success")
                except Exception as e:
                    flash("Error sending email. Please try again.", "error")
            else:
                flash("Email or phone not found, or no email associated with account.", "error")
        
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
        
        # Check if user is already verified (either email or phone)
        if user.email_verified or user.phone_verified:
            flash("Account already verified!", "info")
            return redirect(url_for("login"))
        
        email_form = EmailOTPForm()
        phone_form = PhoneOTPForm()
        resend_form = ResendOTPForm()
        
        if request.method == "POST":
            if email_form.submit.data and email_form.validate():
                if email_form.email_otp.data == user.email_otp and not is_otp_expired(user.email_otp_expires):
                    user.email_verified = True
                    user.email_otp = None
                    user.email_otp_expires = None
                    db.session.commit()
                    flash("Email verified successfully!", "success")
                else:
                    flash("Invalid or expired email verification code.", "error")
            
            elif phone_form.submit.data and phone_form.validate():
                if phone_form.phone_otp.data == user.phone_otp and not is_otp_expired(user.phone_otp_expires):
                    user.phone_verified = True
                    user.phone_otp = None
                    user.phone_otp_expires = None
                    db.session.commit()
                    flash("Phone verified successfully!", "success")
                else:
                    flash("Invalid or expired phone verification code.", "error")
            
            elif resend_form.submit.data:
                # Resend OTP to the primary contact method
                if user.email and not user.email_verified:
                    email_otp = generate_otp()
                    user.email_otp = email_otp
                    user.email_otp_expires = get_otp_expiry_time()
                    send_email_otp(user.email, email_otp)
                    flash(f"Verification code resent to {user.email}", "success")
                elif user.phone and not user.phone_verified:
                    phone_otp = generate_otp()
                    user.phone_otp = phone_otp
                    user.phone_otp_expires = get_otp_expiry_time()
                    send_sms_otp(user.phone, phone_otp)
                    flash(f"Verification code resent to {user.phone}", "success")
                else:
                    flash("No verification method available", "warning")
                
                db.session.commit()
        
        return render_template("verify_account.html", 
                             user=user, 
                             email_form=email_form, 
                             phone_form=phone_form, 
                             resend_form=resend_form)

    # OTP verification routes - using custom email and SMS verification

    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True) 