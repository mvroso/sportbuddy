import os
from flask import Flask
# Database management
from flask_sqlalchemy import SQLAlchemy
# Cryptography for storing hashes
from flask_bcrypt import Bcrypt
# User session management
from flask_login import LoginManager
# Mail management
from flask_mail import Mail
# Environment variables
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

app = Flask(__name__)


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# hide password later !!!
# mysql tutorial : https://www.youtube.com/watch?v=hQl2wyJvK5k
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234abcd@localhost/users'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Flask-Login configuration
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASS')
mail = Mail(app)

from website import routes