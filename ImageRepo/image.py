from flask import make_response, abort
from config import db
from models import Images,ImageSchema,User,UserSchema
from pathlib import Path
import pyrebase
import os
from certificate import config

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()


def  upload(user_id):
    """
    This function responds to a request for /api/upload
    to upload a list of images

    :param person_id:   Id of person to find
    :return:            Integer
    """
    user = User.query.filter(User.user_id == user_id).one_or_none()
    
    if user is None:
        abort(404, f"Person not found for Id: {user_id}")

    file_path = {
        "image": "1.png"
    }
    
    if file_path is not None:
      
        new_image = Images()
        new_image.image = file_path
        schema = ImageSchema()
        path =  file_path["image"]
        storage.child(path).put(file_path["image"])
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


def read_images():
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        json string of list of people
    """
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
    existing_image = (
        Images.query.filter(Images.image_id == image_id)
        .filter(Images.user_id == user_id)
        .one_or_none()
    )
    
    if existing_image is not None:
        path_to_download_folder = str(os.path.join(Path.home(), "Downloads"))
        storage.child(existing_image.image).download(str(existing_image.image_id) + ".jpg")
        schema = ImageSchema()
        data = schema.dump(existing_image)

        return  data,200
    else:
        abort(
            409,
            "Image doesnt exist"
        )


def delete_image(user_id,image_id):

    existing_image = (
        Images.query.filter(Images.image_id == image_id)
        .filter(Images.user_id == user_id)
        .one_or_none()
    )

    if existing_image is not None:
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