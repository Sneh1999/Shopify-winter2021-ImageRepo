from flask import make_response, abort, request
from config import db
from models import Images, ImageSchema, User, UserSchema, Permissions
import sys
import pyrebase
import time
from certificate import config
import connexion
from passlib.context import CryptContext
import hashlib
from sqlalchemy import and_
import os

JWT_ISSUER = os.environ.get('JWT_ISSUER')
JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_LIFETIME_SECONDS = 6000
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM')
ADMIN_USER = os.environ.get('ADMIN_USER')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
MAX_IMAGE_SIZE = 10*1024*1024
MIN_IMAGE_SIZE = 2*1024

# create CryptContext object
context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=50000
)

# Supported Image Types
supported_types = ['image/bmp', 'image/dds', 'image/exif', 'image/gif', 'image/jpg', 'image/jpeg', 'image/jp2', 'image/jpx',
                   'image/pcx', 'image/png', 'image/pnm', 'image/ras', 'image/tga', 'image/tif', 'image/tiff', 'image/xbm', 'image/xpm']


# Initialize Firebase
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()


def upload(user_id):
    """
    This function uploads an image
    :param user_id:   Id of user
    :return:          201 on success,with the user type
    """
    # Get the token info
    token_info = connexion.context['token_info']
    # Get the file from request body
    file = connexion.request.files['filename']

    # Allowing only the file size between 2 KB to 10 MB ,length of the filename to be between 6 to 100 characters
    #  Checking  the type of file is within the supported types
    # Checking if user_id,filename is not None or empty string
    if (user_id is None or user_id is "" or file is None or (file.filename is None) or
        (file.content_type not in supported_types) or (get_size(file) > MAX_IMAGE_SIZE or get_size(file) < MIN_IMAGE_SIZE) or
            (len(file.filename) > 100 or len(file.filename) < 6)):
        abort(
            400,
            "Bad Request: Please send a valid file"
        )

    #  Check the token belongs to the authorized user
    if token_info['sub'] != str(user_id) and token_info['sub'] != ADMIN_USER:
        abort(
            403,
            "Forbidden: The given user doesnt have access to uoload an image"
        )

    # Hash the filename to prevent attacks
    name = file.filename
    path = hashlib.sha224(name.encode('utf-8')).hexdigest()
    # Attach timestamp to the path of the file to help with the upload of files with the same name
    timestamp = int(time.time())
    path = path + str(timestamp)

    # check the user with the given user_id  to avoid conflicts
    user = User.query.filter(User.id == user_id).one_or_none()

    #  Return 404 if no user found
    if user is None:
        abort(
            404, f"Person not found for Id: {user_id}"
        )

    # Build an image schema
    schema = ImageSchema()
    # build a copy of file type and change its name to the hash name
    image = file
    image.name = path
    image.admin_user = int(user_id)
    # Login using Firebase
    fireb_user = firebase.auth().sign_in_with_email_and_password(
        ADMIN_EMAIL, ADMIN_PASSWORD)
    tok = fireb_user['idToken']

    # Put the image in the firebase storage
    result = storage.child(path).put(image, tok)
    if result is None:
        abort(
            500, "Internal Server Error: the given image could not be stored "
        )

    # Store the download token returned from firebase
    download_token = result['downloadTokens']

    file_obj = {
        "image": path,
        "download_token": download_token,
        "admin_id": int(user_id)
    }

     # create a new image schema
    new_image_schema = schema.load(file_obj, session=db.session)

    # Add the new image to the user
    user.images.append(new_image_schema)
    db.session.commit()
    # Serialize and return the newly created image
    image = Images.query.order_by(Images.timestamp).filter(
        Images.image == path).one_or_none()

    # Serialize the data for the response
    image_schema = ImageSchema()
    data = image_schema.dump(image)

    return data, 201


def read_images(user_id):
    """
    This function returns the images related to a particular user
    :param user_id:   Id of user
    :return:        200,json string of list of images
    """
    if user_id is None or user_id == "":
        abort(
            400,
            "Bad Request: Please send valid user"
        )

    token_info = connexion.context['token_info']

    #  Check the token belongs to the authorized user
    if token_info['sub'] != str(user_id) and token_info['sub'] != ADMIN_USER:
        abort(
            403,
            "Forbidden: The given user doesnt have access to read the image"
        )

    # Search the user with the given user id
    user = User.query.filter(User.id == user_id).one_or_none()

    # The user if not found
    if user is None:
        abort(
            404,
            " Not Found: No user found with the given user id"
        )

    #  Search for the image associated with the given user id
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

        return data, 200
    else:
        # No image found for the given user
        abort(
            404,
            " Not Found: No images found"
        )


def get_image(user_id, image_id):
    """
    This function returns the download url for an image
    :param user_id:   Id of user
    :param image_id:   Id of image
    :return:   200, download url of the image
    """
    # check if the user_id and image_id are  null or empty strings
    if user_id is None or user_id == "" or image_id is None or image_id == "":
        abort(
            400,
            "Bad Request: Please send valid user and image Ids"
        )

    token_info = connexion.context['token_info']

    # Check if the token belongs to authorized user
    if token_info['sub'] != str(user_id) and token_info['sub'] != ADMIN_USER:
        abort(
            403,
            "Forbidden: The given user doesnt have access to read the images"
        )

    existing_image = (
        db.session.query(
            Images
        ).filter(
            User.id == Permissions.user_id,
        ).filter(
            Images.id == Permissions.image_id,
        ).filter(
            User.id == user_id,
        ).filter(
            Images.id == image_id
        )
        .first()
    )

    # Check if the user is associated with the given image
    if existing_image is None:
        abort(
            403,
            "Forbidden: User doesnt have permission for the given image"
        )

    # Get the download url from firebase
    url = storage.child(existing_image.image).get_url(
        existing_image.download_token)

    if url is None:
        abort(
            500, "Internal Server Error: The download url could not retrieved"
        )

    return url, 200


def delete_image(user_id, image_id):
    """
    This function deletes an image associated with a given user
    :param user_id:   Id of user
    :param image_id:   Id of image
    :return:        204
    """
    # check if the user_id and image_id are  null or empty strings
    if user_id is None or user_id == "" or image_id is None or image_id == "":
        abort(
            400,
            "Bad Request: Please send valid user and image Ids"
        )

    token_info = connexion.context['token_info']

    
    # Check if the token belongs to authorized user
    if token_info['sub'] != str(user_id) and token_info['sub'] != ADMIN_USER:
        abort(
            403,
            "Forbidden: The given user doesnt have access to delete the image"
        )

    existing_image = (db.session.query(
        Images
    ).filter(
        User.id == Permissions.user_id,
    ).filter(
        Images.id == Permissions.image_id,
    ).filter(
        User.id == user_id,
    ).filter(
        Images.id == image_id
    )
        .one_or_none()
    )

    # if current user has the permission for the given image
    if existing_image is not None:
        # check all the permissions realted to this image
        permissions = Permissions.query.filter(
            Permissions.image_id == image_id).all()
        # if more than one user has permission to this image then dont delete it from firebase and database
        if len(permissions) > 1:
            # Get the permission related to user_id ,image_id
            delete_permission = Permissions.query.filter(and_(
                Permissions.image_id == image_id, Permissions.user_id == user_id)).one_or_none()
            # Delete the permission from the db
            db.session.delete(delete_permission)
            db.session.commit()
        else:
            # delete the image from the firebase and database
            db.session.delete(existing_image)
            db.session.commit()
            # delete the image from firebase storage
            storage.delete(existing_image.image)
        return make_response(
            "Image deleted", 204
        )
    else:
        abort(
            403,
            "Forbidden: The given user doesnt have permission to delete this image"
        )


def create_access(user_id, image_id):
    """
    This function created an access for a person with 
    email provided in the request body to the image of the user with the given user_id
    :param user_id:   Id of user to find
    :param image_id:   Id of image to find
    :return:        201, image to which the access was given to user with the email in request body
    """
    # get the email from the request body
    email = connexion.request.get_json()
    # check if the user_id and the image_is provided is not null or empty string and email is not empty string or null
    if user_id is None or user_id == "" or image_id is None or image_id == "" or email is None or email is {} or email["email"] is None or email["email"] is "":
        abort(
            400,
            "Bad Request: Please send valid user Id, image Id and email"
        )

    token_info = connexion.context['token_info']

  # Only the authorized user or the admin should be able to access the user details
    if token_info['sub'] != str(user_id) and token_info['sub'] != ADMIN_USER:
        abort(
            403,
            "Forbidden: The given user doesnt have an access"
        )

   
     # get the image which needs to be added to  the email_user
    image = Images.query.filter(Images.id == image_id).filter(Images.admin_id == int(user_id)).one_or_none()

    if image is None:
        abort(
            403,
            "Forbidden: The given user doesnt have an admin access to the given image"
        )

    # search for the user with the given email address
    email_user = User.query.filter(User.email == email["email"]).one_or_none()

    # verify admin 

    if email_user is None:
        abort(
            404,
            " Not Found: User with the given email is not found"
        )

    #  Check if the user with the email already has permission for this image
    existing_permission = (db.session.query(
        Permissions
    ).filter(
        User.id == Permissions.user_id,
    ).filter(
        Images.id == Permissions.image_id,
    ).filter(
        User.email == email["email"],
    ).filter(
        Images.id == image_id
    )
        .one_or_none()
    )
    # User with the email already has persmissions
    if existing_permission is not None:
        abort(
            409,
            "Conflict: the permission already exists"
        )


    schema = ImageSchema()
    # append the image to the user
    email_user.images.append(image)
    db.session.merge(email_user)
    db.session.commit()
    # Serialize and return the newly created image in the response
    new_image = Images.query.filter(Images.id == image_id).one_or_none()
    data = schema.dump(new_image)
    return data, 201



def get_size(fobj):
    """
    This function is used to determine the size of a file
    """
    if fobj.content_length:
        return fobj.content_length

    try:
        pos = fobj.tell()
        fobj.seek(0, 2)  # seek to end
        size = fobj.tell()
        fobj.seek(pos)  # back to original position
        return size
    except (AttributeError, IOError):
        pass

    return 0
