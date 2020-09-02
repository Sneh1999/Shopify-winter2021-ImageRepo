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
    This function creates a new person in the people structure
    based on the passed in person data

    :param person:  person to create in people structure
    :return:        201 on success, 406 on person exists
    """
    user = connexion.request.get_json()
    fname = user.get("fname")
    lname = user.get("lname")
    email = user.get("email")
    password = user.get("password")
    user["password"]= context.hash(password)
    existing_user = (
        User.query.filter(User.fname == fname)
        .filter(User.lname == lname)
        .filter(User.email == email)
        .one_or_none()
    )

    # Can we insert this person?
    if existing_user is None:

        # Create a person instance using the schema and the passed in person
        schema = UserSchema()
        new_person = schema.load(user, session=db.session)

        # Add the person to the database
        db.session.add(new_person)
        db.session.commit()

        # Serialize and return the newly created person in the response
        data = schema.dump(new_person)
        del data['password']
        return data, 201

    # Otherwise, nope, person exists already
    else:
        abort(
            409,
            "Person {fname} {lname} exists already".format(
                fname=fname, lname=lname
            ),
        )


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
    user = User.query.filter(User.user_id == user_id).outerjoin(Images).one_or_none()

    # Did we find a person?
    if user is not None:

        # Serialize the data for the response
        user_schema = UserSchema()
        data = user_schema.dump(user)
        del data['password']
        return data

    # Otherwise, nope, didn't find that person
    else:
        abort(
            404,
            "Person not found for Id: {user_id}".format(user_id=user_id),
        )
