import time
import connexion
from flask import  abort
import six
from werkzeug.exceptions import Unauthorized
from jose import JWTError, jwt
from models import User
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

def generate_token():
    """
    This function creates a JWT token
    :param email:       Email of the person trying to login 
    :param password:    password of the person trying to login      
    :return:            200 on success
    """

    # get the user from the request body
    user = connexion.request.get_json()
    
    if user is None:
        abort(
            400,
            "Bad Request: Please send valid email and password"
        )

    email = user.get("email")
    password = user.get("password")

    #  check if the user sent email and password
    if email is None or password is None:
        abort(
            400,
            "Bad Request: Please send valid email and password"
        )

    #  check if the user with the given email exists
    existing_user = (
        User.query.filter(User.email == email)
        .one_or_none()
    )
    
    if existing_user is not None:
        # verify the password against the encrypted password stored in the db
        verify_password = context.verify(password, existing_user.password)

        #  if verify_password is false return Unauthorized
        if verify_password is False:
            abort(
                401,
                "Unauthorized"
            )
        
        timestamp = int(time.time())

        payload = {
            "iss": JWT_ISSUER,
            "iat": int(timestamp),
            "exp": int(timestamp + JWT_LIFETIME_SECONDS),
            "sub": str(existing_user.id),
        }

        # create the jwt token
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    else:
        abort(
        404,
        "NOT FOUND: The  user with the given email is not found"
        )


def decode_token(token):
    """
    This function is used to decode the JWT token passed with the header
    :param token:       Token passed in the header      
    :return:            decoded token 
    """
    # Try decoding the token or else declare unauthorized
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        six.raise_from(Unauthorized, e)
