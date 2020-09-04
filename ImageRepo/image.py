from flask import make_response, abort,request
from config import db
from models import Images,ImageSchema,User,UserSchema,Permissions
from pathlib import Path
import sys
import pyrebase
import os
import imghdr
import wget
from certificate import config
import connexion
from io import BufferedReader
from passlib.context import CryptContext

JWT_ISSUER = 'com.zalando.connexion'
JWT_SECRET = 'change_this'
JWT_LIFETIME_SECONDS = 600
JWT_ALGORITHM = 'HS256'

# create CryptContext object
context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=50000
)


# TODO: password field still returning

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

supported_types = ['image/bmp','image/dds','image/exif','image/gif','image/jpg','image/jpeg','image/jp2','image/jpx','image/pcx','image/png','image/pnm','image/ras','image/tga','image/tif','image/tiff','image/xbm','image/xpm']

admin_user = 1

MAX_IMAGE_SIZE = 10*1024*1024 
MIN_IMAGE_SIZE = 2*1024

def  upload(user_id):
    """
    This function uploads an image
    :param user_id:   Id of user
    :return:          201 on success
    """
    # Get the token info
    token_info = connexion.context['token_info']
    # Get the file from request body
    file = connexion.request.files['filename']
    # red the file and determine its size
    blob = file.read()
    size = len(blob)
   
    # Allowing only the file size between 2 KB to 10 MB  ,length of the filename to be between 6 to 100 
    #  Checking of the type of file is within the supported types
    # Checking if user_id,filename is not None or empty string
    if (user_id is None or user_id is "" or file is None  or (file.filename is None) or 
        (file.content_type not in supported_types) or 
        (size < MIN_IMAGE_SIZE or size > MAX_IMAGE_SIZE ) or (len(file.filename) > 100 or len(file.filename) < 6)):
        abort(
            400,
            "Bad Request: Please send a valid file"
        )

  
    #  Check the token belongs to the authorized user or the admin user
    if token_info['sub'] != str(user_id) and token_info['sub'] != str(admin_user):
        abort(
            403,
            "Forbidden: The given user doesnt have access to uoload an image"
        )
    
    # Hash the filename to prevent attacks
    path  = context.hash(file.filename)

    file_path = {
        "image": path
    }
    
    # check the user with the given user_id and to avoid conflicts
    user = User.query.filter(User.id == user_id).one_or_none()

     #  Return 404 if no user found
    if user is None:
        abort(
            404, f"Person not found for Id: {user_id}"
            )
    
    # create a new image object
    new_image = Images()
    new_image.image = file_path
    schema = ImageSchema()
    image = file
    image.name = image.filename
    # Store the image in firebase 
    # TODO: implement proper  error checking to see if teh firebase stored it properly
    storage.child(path).put(image)

    new_image_schema = schema.load(file_path, session=db.session)
    user.images.append(new_image_schema)
    db.session.commit()

    # Serialize and return the newly created image 
    image = Images.query.order_by(Images.timestamp).filter(Images.image == path).one_or_none()
    # Serialize the data for the response
    image_schema = ImageSchema()
    data = image_schema.dump(image)

    return data, 201



def read_images(user_id):
    """
    This function returns the images related to a particular user
    with the complete lists of people

    :return:        200,json string of list of images
    """
    if user_id is None or user_id == "":
        abort(
            400,
            "Bad Request: Please send valid user"
        )
    token_info = connexion.context['token_info']
   
     #  Check the token belongs to the authorized user or the admin user
    if token_info['sub'] != str(user_id) and token_info['sub'] != str(admin_user):
        abort(
            403,
            "Forbidden: The given user doesnt have access to read the images"
        )
    
    user = User.query.filter(User.id == user_id).one_or_none()
    if user is None:
         abort(
            404,
            " Not Found: No user found with the given user id"
        )
    #  Search for the image associated with the  associated user
    image = db.session.query(
            Images
        ).filter(
            User.id == Permissions.user_id,
        ).filter(
            Images.id == Permissions.image_id,
        ).filter(
            User.id == user_id,
        ).all()

    if image is not None:
        # Serialize the data for the response
        image_schema = ImageSchema(many=True)
        data = image_schema.dump(image)

        return data,200
    else:
        abort(
            404,
            " Not Found: No images found"
        )
    


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

