from flask import render_template, url_for
from website import app
from website.models import User

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/contact")
def contact():
    return render_template('contact.html', title='Contact')