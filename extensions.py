from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# SQLAlchemy instance
db = SQLAlchemy()

# Login manager
login_manager = LoginManager()
login_manager.login_view = "login"

# Mail
mail = Mail()

# Limiter (IP based)
limiter = Limiter(key_func=get_remote_address) 