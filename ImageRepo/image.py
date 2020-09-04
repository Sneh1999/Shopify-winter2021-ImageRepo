from flask import make_response, abort,request
from config import db
from models import Images,ImageSchema,User,UserSchema,Permissions
import sys
import pyrebase
import time
from certificate import config
import connexion
from passlib.context import CryptContext
import hashlib


#  TODO: check for the conflict error and add it to swagger as well
# TODO: ensure secure uploading ,downloading and deleting of teh image

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

ADMIN_USER = 1


ADMIN_EMAIL = 'admin@gmail.com'
ADMIN_PASSWORD = 'adminuser'

MAX_IMAGE_SIZE = 10*1024*1024 
MIN_IMAGE_SIZE = 2*1024

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
    # read the file and determine its size
    size = get_size(file)
   
    # Allowing only the file size between 2 KB to 10 MB  ,length of the filename to be between 6 to 100 characters
    #  Checking of the type of file is within the supported types
    # Checking if user_id,filename is not None or empty string
    if (user_id is None or user_id is "" or file is None  or (file.filename is None) or 
        (file.content_type not in supported_types) or (size > MAX_IMAGE_SIZE or size < MIN_IMAGE_SIZE) or
       (len(file.filename) > 100 or len(file.filename) < 6)):
        abort(
            400,
            "Bad Request: Please send a valid file"
        )

  
    #  Check the token belongs to the authorized user 
    if token_info['sub'] != str(user_id) and token_info['sub'] != str(ADMIN_USER) :
        abort(
            403,
            "Forbidden: The given user doesnt have access to uoload an image"
        )
    
    # Hash the filename to prevent attacks
    name = file.filename
    path  = hashlib.sha224(name.encode('utf-8')).hexdigest()
    # Attach timestamp to the path of the file to help with the upload of files with the same name
    timestamp = int(time.time())
    path  = path + str(timestamp)

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
    image.name = path
    
    # TODO: add error checking for firebase here
    # Store the image in firebase 
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
    if token_info['sub'] != str(user_id) and token_info['sub'] != str(ADMIN_USER) :
        abort(
            403,
            "Forbidden: The given user doesnt have access to read the image"
        )
    
    user = User.query.filter(User.id == user_id).one_or_none()

    # The user if not found
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
    


def get_image(user_id,image_id):
    """
    This function returns the download url for an image
    :param user_id:   Id of user
    :param image_id:   Id of image
    :return:   200, download url of the image
    """
    # check if the user_id and image_id are not null or empty strings
    if user_id is None or user_id == "" or image_id is None or image_id == "":
        abort(
            400,
            "Bad Request: Please send valid user and image Ids"
        )
    
    token_info = connexion.context['token_info']
    
    # Check if the token belongs to authorized user
    if token_info['sub'] != str(user_id) and token_info['sub'] != str(ADMIN_USER):
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
            404,
            " Not Found: No user found with the permission for the given  image id"
        )

    # TODO : add error checking for firebase here
    user = firebase.auth().sign_in_with_email_and_password(ADMIN_EMAIL,ADMIN_PASSWORD)

    tok = user['idToken']

    url = storage.child(existing_image.image).get_url(tok)

    return  url,200
   


def delete_image(user_id,image_id):
    """
    This function returns the download url for an image
    :param user_id:   Id of user
    :param image_id:   Id of image
    :return:        json string of list of people
    """
     # check if the user_id and image_id are not null or empty strings
    if user_id is None or user_id == "" or image_id is None or image_id == "":
        abort(
            400,
            "Bad Request: Please send valid user and image Ids"
        )

    token_info = connexion.context['token_info']
    
    # Check if the token belongs to authorized user
    if token_info['sub'] != str(user_id) and token_info['sub'] != str(ADMIN_USER):
        abort(
            403,
            "Forbidden: The given user doesnt have access to read the images"
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

    if existing_image is not None:
        #  TODO: check if the given image is also associated with another user
        storage.delete(existing_image.image)
        db.session.delete(existing_image)
        db.session.commit()
        return make_response(
            "Image deleted", 200
        )
    else:
          abort(
            404,
            " Not Found: No user found with the permission for the given image id"
        )


def create_access(user_id,image_id):
    """
    This function created an access for a person with 
    email provided in the request body to the image of the user with the given user_id
    :param user_id:   Id of user to find
    :param image_id:   Id of image to find
    :return:        201, image object
    """
    token_info = connexion.context['token_info']
   
  # Only the authorized user or the admin should be able to access the user details    
    if token_info['sub'] != str(user_id) and token_info['sub'] != str(ADMIN_USER):
        abort(
            403,
            "Forbidden: The given user cannot access the user_id provided"
        )

    # get the email from teh request body
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

# def create_access(user_id,image_id):
#     """
#     This function created an access for a person with 
#     email provided in the request body to the image of the user with the given user_id
#     :param user_id:   Id of user to find
#     :param image_id:   Id of image to find
#     :return:        201, image to which the access was given to
#     """
#     if user_id is None or user_id == "" or image_id is None or image_id == "":
#         abort(
#             400,
#             "Bad Request: Please send valid user and image Id"
#         )

#     token_info = connexion.context['token_info']
   
#   # Only the authorized user or the admin should be able to access the user details    
#     if token_info['sub'] != str(user_id) and token_info['sub'] != str(admin_user):
#         abort(
#             403,
#             "Forbidden: The given user doesnt have an access"
#         )

#     # get the email from teh request body
#     email = connexion.request.get_json()

#      #  Search for the image associated with the  associated user
#     image = ( db.session.query(
#             Images
#         ).filter(
#             User.id == Permissions.user_id,
#         ).filter(
#             Images.id == Permissions.image_id,
#         ).filter(
#             User.id == user_id,
#         ).filter(
#             Images.id == image_id
#         ).one_or_none()
#         )

#     if image is None:
#         abort(
#             404,
#             " Not Found: Image associated with the given user and image id is not found"
#         )
#     # serach for the user with the given email address
#     email_user = User.query.filter(User.email == email["email"]).one_or_none()

#     if email_user is None:
#         abort(
#             404,
#             " Not Found: User with the given email is not found"
#         )

#     # check if the permission already exists
#     permission = Permissions.query.filter(Permissions.image_id == image_id).filter(Permissions.user_id == email_user.id).one_or_none()

#     if permission is not None:
#         abort(
#             409,
#             "Conflict: the permission already exists"
#         )
    
#     file_path =  {
#         "image": image.image
#     }

#     schema = ImageSchema()
#     new_image_schema = schema.load(file_path, session=db.session)
#     email_user.images.append(new_image_schema)
#     db.session.commit()
#     # Serialize and return the newly created person in the response
#     new_image = Images.query.filter(Images.id == image_id).one_or_none()
#     data = schema.dump(new_image)

#     return data, 201


def get_size(fobj):
    if fobj.content_length:
        return fobj.content_length

    try:
        pos = fobj.tell()
        fobj.seek(0, 2)  #seek to end
        size = fobj.tell()
        fobj.seek(pos)  # back to original position
        return size
    except (AttributeError, IOError):
        pass

    return 0  
