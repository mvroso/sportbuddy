from flask import url_for
from website import mail
from flask_mail import Message

# Send reset email user
def send_reset_email(user):
    token = user.get_reset_token()
    
    msg = Message('Password Reset Request',
            sender='noreply@sportbuddy.com', recipients=[user.email])

    msg.body = f"To reset your password, visit the following link:\n\n" \
            f"{url_for('users.reset_password', token=token, _external=True)}\n\n" \
            f"If you did not make this request then simply ignore this email."

    mail.send(msg)