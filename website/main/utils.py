import os, secrets
from PIL import Image
from flask import current_app

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