from flask import make_response, abort,request
from config import db
from models import Images,ImageSchema,User,UserSchema
from pathlib import Path
import sys
import pyrebase
import os
import imghdr
import wget
from certificate import config
import connexion
from io import BufferedReader

# TODO: password field still returning

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

supported_types = ['image/bmp','image/dds','image/exif','image/gif','image/jpg','image/jpeg','image/jp2','image/jpx','image/pcx','image/png','image/pnm','image/ras','image/tga','image/tif','image/tiff','image/xbm','image/xpm']

admin_user = 1

MAX_IMAGE_SIZE = 10*1024*1024 
MIN_IMAGE_SIZE = 10*1024

def  upload(user_id):
    """
    This function uploads an image
    :param user_id:   Id of user
    :return:          201 on success
    """
    token_info = connexion.context['token_info']
   
    if token_info['sub'] != str(user_id) and token_info['sub'] != str(admin_user):
        abort(
            403,
            "Forbidden: The given user doesnt have access to uoload an image"
        )
    
    if user_id is None or user_id is "":
        abort(
            400,
            "Bad Request: Please send valid user_id"
        )

    file = connexion.request.files['filename']
    blob = file.read()
    size = len(blob)
    print(file.content_type,flush=True)
    # Allowing only the file size between 2 to 10 kb
    if file is None  or (file.filename is None) or (file.content_type not in supported_types) or (size < MIN_IMAGE_SIZE or size > MAX_IMAGE_SIZE ):
        abort(
            400,
            "Bad Request: Please send a valid file"
        )

    

    file_path = {
        "image": file.filename
    }
    
    user = User.query.filter(User.id == user_id).one_or_none()
    
    if user is None:
        abort(
            404, f"Person not found for Id: {user_id}"
            )
    
    if file_path is not None:
      
        new_image = Images()
        new_image.image = file_path
        schema = ImageSchema()
        path =  file_path["image"]
        image = file
        image.name = image.filename
        storage.child(path).put(image)
        new_image_schema = schema.load(file_path, session=db.session)
        user.images.append(new_image_schema)
        db.session.commit()

        # Serialize and return the newly created person in the response
        data = schema.dump(new_image)

        return 0, 201
    else:
        abort(
            409,
            "Not working fine"
        )


def read_images(user_id):
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        json string of list of people
    """
    token_info = connexion.context['token_info']
   
    if token_info['sub'] != str(user_id):
        abort(
            401,
            "Unauthorized"
        )
    # Create the list of people from our data
    image = Images.query.order_by(Images.timestamp).all()
    
    # Serialize the data for the response
    image_schema = ImageSchema(many=True)
    data = image_schema.dump(image)
    return data,200


def download(user_id,image_id):
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        json string of list of people
    """
    token_info = connexion.context['token_info']
   
    if token_info['sub'] != str(user_id):
        abort(
            401,
            "Unauthorized"
        )
    
    existing_image = (
        Images.query.filter(Images.id == image_id)
        .one_or_none()
    )
    
    if existing_image is not None:
        path_to_download_folder = str(os.path.join(Path.home(), "Downloads"))
        url = storage.child(existing_image.image).get_url(None)
        # TODO complete with ssl certificate
        # image_filename = wget.download(url)
        schema = ImageSchema()
        data = schema.dump(existing_image)
        return  data,200
    else:
        abort(
            409,
            "Image doesnt exist"
        )


def delete_image(user_id,image_id):

    token_info = connexion.context['token_info']
   
    if token_info['sub'] != str(user_id):
        abort(
            401,
            "Unauthorized"
        )

    existing_image = (
        Images.query.filter(Images.id == image_id)
        .filter(Images.id == user_id)
        .one_or_none()
    )


    if existing_image is not None:
        storage.delete(existing_image.image)
        db.session.delete(existing_image)
        db.session.commit()
        return make_response(
            "Image deleted", 200
        )
    else:
        abort(
            409,
            "Image doesnt exist"
        )

def create_access(user_id,image_id):
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        json string of list of people
    """
    token_info = connexion.context['token_info']
   
    if token_info['sub'] != str(user_id):
        abort(
            401,
            "Unauthorized"
        )

    email = connexion.request.get_json()
    user = User.query.filter(User.id == user_id).one_or_none()
    email_user = User.query.filter(User.email == email["email"]).one_or_none()
    image = Images.query.filter(Images.id == image_id).one_or_none()
    if user and email_user and image: 
        file_path = {
            "image": image.image
        }
        schema = ImageSchema()
        new_image_schema = schema.load(file_path, session=db.session)
        email_user.images.append(new_image_schema)
        db.session.commit()

            # Serialize and return the newly created person in the response
        data = schema.dump(email_user)

        return 0, 201
    else:
        abort(
            409,
            "Not working fine"
        )



def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0