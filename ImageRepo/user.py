from flask import make_response, abort
from config import db
from models import Images, ImageSchema, User, UserSchema
from pathlib import Path
import pyrebase
import os
from certificate import config
import connexion
from passlib.context import CryptContext
from sqlalchemy import and_


JWT_ISSUER = os.environ.get('JWT_ISSUER')
JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_LIFETIME_SECONDS = 31622400
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM')
ADMIN_USER = os.environ.get('ADMIN_USER')

# create CryptContext object
context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=50000
)

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()


def create():
    """
    This function creates a new user in the user structure

    :param user:  user object
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

    # Get the user details from teh request body
    fname = user.get("fname")
    lname = user.get("lname")  
    email = user.get("email")
    password = user.get("password")

    # Check if the data within the user is not None
    if (
        fname is None or lname is None or 
        email is None or password is None or 
        fname is "" or lname is "" or email is "" 
        or password is ""):
        abort(
            400,
            "Bad Request: Please send valid user"
        )

    # Create a hash for the password, to prevent direct storage of the password
    user["password"] = context.hash(password)

    # Check if there is an existing user
    existing_user = (
        User.query.filter(
            and_(User.fname == fname, User.lname == lname, User.email == email))
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

    # Only the admin user should be allowed to see all the users
    if token_info['sub'] != ADMIN_USER:
        abort(
            403,
            "Forbidden: Only the admin's are allowed to see all the users"
        )

    #  Get all the users expect the admin user
    users = User.query.order_by(db.desc(User.timestamp)).all()

    #  Return 404 if no users found
    if users is None:
        abort(
            404,
            "No users found"
        )

    user_schema = UserSchema(many=True)
    data = user_schema.dump(users)
    for d in data:
        del(d["password"])

    return data, 200


def get_user(user_id):
    """
    This function gets the user with the given user_id
    :param user_id:   Id of user to find
    :return:           200 on successful , 404 if not found
    """

    # Check if user_id is None or an empty string
    if user_id == None or user_id == "":
        abort(
            400,
            "Bad Request: Please send valid user_id"
        )

    # Get the person requested
    token_info = connexion.context['token_info']

    # Only the authorized user or the admin should be able to access the user details
    if token_info['sub'] != str(user_id) and token_info['sub'] != ADMIN_USER:
        abort(
            403,
            "Forbidden: The given user cannot access the user_id provided"
        )

    # Check for the user with  user_id
    user = User.query.filter(User.id == user_id).one_or_none()

    # user exists
    if user is not None:
        # Serialize the data for the response
        user_schema = UserSchema()
        data = user_schema.dump(user)
        del(data["password"])
        return data, 200

    # user doesnt exist
    else:
        abort(
            404,
            "User not found for Id: {user_id}".format(user_id=user_id),
        )


def put_user(user_id):
    """
    This function ammends the user with user_id 
    :param user_id:   Id of the user to be deleted
    :return:          201 on successful update, 404 if not found
    """

    if user_id == None or user_id == "":
        abort(
            400,
            "Bad Request: Please send valid user_id"
        )

     # Get the token provided
    token_info = connexion.context['token_info']

    # The user should be able to delete his account as well as the admin should be able to delete the account
    if token_info['sub'] != str(user_id) and token_info['sub'] != ADMIN_USER:
        abort(
            403,
            "Forbidden: The given user cannot ammend the user_id provided"
        )

    # get the user from the request body
    request_user = connexion.request.get_json()

    if request_user == None:
        abort(
            400,
            "Bad Request: Please send valid user"
        )

    email = request_user.get("email")
    fname = request_user.get("fname")
    lname = request_user.get("lname")

    # check if the properties of the user are not none or empty string
    if email is None or email is "" or fname is None or fname is "" or lname is None or fname is "":
        abort(
            400,
            "Bad Request: Please send valid user details"
        )

    # search for the user with the given user_id
    user = (
        User.query.filter(User.id == user_id)
        .one_or_none()
    )

    ammend_user = (User.query.filter(User.email == email)
                   .filter(User.fname == fname)
                   .filter(User.lname == lname)
                   .one_or_none()
                   )
    if ammend_user is not None:
        abort(
            409,
            "Person {fname} {lname} exists already".format(
                fname=fname, lname=lname
            ),
        )

    # user exists
    if user is not None:
        schema = UserSchema()
        update = schema.load(request_user, session=db.session)
        update.id = user.id
        db.session.merge(update)
        db.session.commit()
        data = schema.dump(user)
        del(data["password"])
        return data, 201

    # user not found
    else:
        abort(404, "User not found")


def delete_user(user_id):
    """
    This function deletes the user_id that is passed
    :param user_id:   Id of the user to be deleted
    :return:           204 on successful delete, 404 if not found
    """

    if user_id == None or user_id == "":
        abort(
            400,
            "Bad Request: Please send valid user_id"
        )

    # Get the person requested
    token_info = connexion.context['token_info']

  # The user should be able to delete his account as well as the admin should be able to delete the account
    if (token_info['sub'] != str(user_id)) and token_info['sub'] != ADMIN_USER:
        abort(
            403,
            "Forbidden: The given user cannot delete the user_id provided"
        )

    # search for the user with the given user_id
    user = (
        User.query.filter(User.id == user_id)
        .one_or_none()
    )

    # user exists
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        return make_response(
            "User has been deleted deleted", 204
        )

    # user doesnt exist
    else:
        abort(404, "User not found")
