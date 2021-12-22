from flask import Flask
# Database management
from flask_sqlalchemy import SQLAlchemy
# Cryptography for storing hashes
from flask_bcrypt import Bcrypt
# User session management
from flask_login import LoginManager

app = Flask(__name__)


app.config['SECRET_KEY'] = 'test'
# hide password later !!!
# tutorial : https://www.youtube.com/watch?v=hQl2wyJvK5k
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234abcd@localhost/users'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from website import routes