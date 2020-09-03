from flask import make_response, abort
from config import db
from models import Images,ImageSchema,User,UserSchema
from pathlib import Path
import pyrebase
import os
from certificate import config
import connexion

from passlib.context import CryptContext


# create CryptContext object
context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=50000
)

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()



def create():
    """
    This function creates a new user in the user structure

    :param user:  person to create in people structure
    :return:        201 on success, 406 on person exists
    """
    # Get the user from the request body
    user = connexion.request.get_json()
    #  Verify that the user is not none
    if user is None:
        abort(
            400,
            "Bad Request: Please send valid user"
        )
    
    fname = user.get("fname")
    lname = user.get("lname")
    email = user.get("email")
    password = user.get("password")

    # Check if the data within the user is not None
    if fname is None or lname is None or email is None or password is None:
        abort(
            400,
            "Bad Request: Please send valid user"
        )

    if fname is "" or lname is "" or email is "" or password is "":
        abort(
            400,
            "Bad Request: Please send valid user"
        )
        
    # Create a hash for the password, to prevent direct storage of the password
    user["password"]= context.hash(password)

    # Check if there is an existing user
    existing_user = (
        User.query.filter(User.fname == fname)
        .filter(User.lname == lname)
        .filter(User.email == email)
        .one_or_none()
    )

    # Add the user only if the user doesnt exist   
    if existing_user is None:

        # Create a user
        schema = UserSchema()
        new_person = schema.load(user, session=db.session)

        # Add the user to the database
        db.session.add(new_person)
        db.session.commit()

        # Serialize and return the newly created user in the response
        data = schema.dump(new_person)

        # Delete the password field from the data 
        del data['password']

        return data, 201

    # user exists already
    else:
        abort(
            409,
            "Person {fname} {lname} exists already".format(
                fname=fname, lname=lname
            ),
        )


def get_users():
    """
    This function is used to get all the users by the admin.Only admin is allowed to view the all the users
    :return: json list of all users
    """
    # Get the person requested
    token_info = connexion.context['token_info']
    
    # Only the admin user with user id = 1 should be allowed to see all the users
    if token_info['sub'] != "1":
        abort(
            403,
            "Forbidden: Only the admin's are allowed to see all the users"
        )
    
    #  Get all the users expect the admin user
    users = User.query.order_by(db.desc(User.timestamp)).filter(User.id != "1").all()
    
    #  Return 404 if no users found
    if users is None:
        abort(
            404,
            "No users found"
        )
    
    user_schema = UserSchema(many=True)
    data = user_schema.dump(users)
    return data

def get_user(user_id):
    """
    This function responds to a request for /api/people/{person_id}
    with one matching person from people

    :param person_id:   Id of person to find
    :return:            person matching id
    """
    # Get the person requested
    token_info = connexion.context['token_info']
   
    if token_info['sub'] != str(user_id):
        abort(
            401,
            "Unauthorized"
        )
    user = User.query.filter(User.id == user_id).outerjoin(Images).one_or_none()

    # user exists
    if user is not None:
        # Serialize the data for the response
        user_schema = UserSchema()
        data = user_schema.dump(user)
        return data

    # Otherwise, nope, didn't find that person
    else:
        abort(
            404,
            "Person not found for Id: {user_id}".format(user_id=user_id),
        )