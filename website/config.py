import os
# Environment variables
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Website configuration and environment variables loading
class Config:
	SECRET_KEY = os.getenv('SECRET_KEY')

	# Database config
	SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Mail config
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.getenv('MAIL_USER')
	MAIL_PASSWORD = os.getenv('MAIL_PASS')