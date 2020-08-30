from flask import make_response, abort
from config import db
from PIL import Image
import numpy as np
from models import Images,ImageSchema
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="<add your credentials path>"

def  upload():
    """
    This function responds to a request for /api/upload
    to upload a list of images

    :param person_id:   Id of person to find
    :return:            Integer
    """
    # user = User.query.filter(User.user_id == user_id).one_or_none()
    
    # if user is None:
    #     abort(404, f"Person not found for Id: {user_id}")

    file_path = {
        "image": "./images_dir/1.png"
    }
    if file_path is not None:
      
        new_image = Images()
        new_image.image = file_path
        schema = ImageSchema()

        new_image_schema = schema.load(file_path, session=db.session)
        db.session.add(new_image_schema)
        db.session.commit()

        # Serialize and return the newly created person in the response
        data = schema.dump(new_image)

        return 0, 201
    else:
        abort(
            409,
            "Not working fine"
        )
