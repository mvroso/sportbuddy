import os, secrets
from PIL import Image
from flask import current_app
from website.models import Role, Sport, Timeperiod

# Save user uploaded picture in /static/img/profile_pictures
def save_picture(form_picture, width, height):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path,
                'static/img/profile_pictures', picture_fn)
    
    # Resize picture with Pillow
    output_size = (width, height)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_fn

# Create models list to populate the database
def fetch_models():
    timeperiods = [
        Timeperiod(name='Morning'),
        Timeperiod(name='Afternoon'),
        Timeperiod(name='Evening'),
        Timeperiod(name='Night')
    ]

    roles = [
        Role(name='Common'),
        Role(name='Coach'),
        Role(name='Company')
    ]
    
    # 39 standard sports
    sports = [
        Sport(name='Archery'),
        Sport(name='Artistic Gymnastics'),
        Sport(name='Artistic Swimming'),
        Sport(name='Athletics'),
        Sport(name='Badminton'),
        Sport(name='Basketball'),
        Sport(name='Beach Volleyball'),
        Sport(name='Biathlon'),
        Sport(name='BMX Racing'),
        Sport(name='Boxing'),
        Sport(name='Diving'),
        Sport(name='Equestrian'),
        Sport(name='Fencing'),
        Sport(name='Golf'),
        Sport(name='Handball'),
        Sport(name='Hockey'),
        Sport(name='Judo'),
        Sport(name='Kayak Flatwater'),
        Sport(name='Kayak Slalom'),
        Sport(name='Marathon Swimming'),
        Sport(name='Modern Pentatlhlon'),
        Sport(name='Montain Bike'),
        Sport(name='Rhythmic Gymnastics'),
        Sport(name='Road Cycling'),
        Sport(name='Rowing'),
        Sport(name='Rugby'),
        Sport(name='Sailing'),
        Sport(name='Soccer'),
        Sport(name='Surfing'),
        Sport(name='Swimming'),
        Sport(name='Table Tennis'),
        Sport(name='Tennis'),
        Sport(name='Track Cycling'),
        Sport(name='Trampoline'),
        Sport(name='Triathlon'),
        Sport(name='Volleyball'),
        Sport(name='Water Polo'),
        Sport(name='Weight Lifting'),
        Sport(name='Wrestling')
    ]

    return (timeperiods, roles, sports)