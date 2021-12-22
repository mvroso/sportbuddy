from flask import Flask

from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)


# app.config[secret key]
# hide password later !!!
# tutorial : https://www.youtube.com/watch?v=hQl2wyJvK5k
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234abcd@localhost/users'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

from website import routes