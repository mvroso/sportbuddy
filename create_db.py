import os
# Environment variables
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
# mysql-connector
import mysql.connector

# Connect to the database
my_db = mysql.connector.connect(
	host='localhost',
	user=os.getenv('MYSQL_USER'),
	passwd=os.getenv('MYSQL_PASS'),
	)

# Create a mysql cursor
my_cursor = my_db.cursor()

# Create database sportsbuddy
my_cursor.execute("DROP DATABASE IF EXISTS sportsbuddy")
my_cursor.execute("CREATE DATABASE IF NOT EXISTS sportsbuddy")

# Check if database was created correctly
my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
	print(db)

# Create database tables
from website.models import *
from website import create_app
app = create_app()
db.create_all(app=create_app())

my_cursor.execute("ALTER TABLE sportsbuddy.coach AUTO_INCREMENT = 21;")
