import time
import connexion
from flask import make_response, abort

import six
from werkzeug.exceptions import Unauthorized
from jose import JWTError, jwt
from models import Images,ImageSchema,User,UserSchema,permissions

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
    user = connexion.request.get_json()
    email = user.get("email")
    password = user.get("password")

    try: 
        existing_user = (
            User.query.filter(User.email == email)
            .one_or_none()
        )


        if existing_user is not None:
            verify_password = context.verify(password, existing_user.password)

            if verify_password is False:
                abort(
                401,
                "Unauthorized"
                )
            timestamp = _current_timestamp()
            payload = {
                "iss": JWT_ISSUER,
                "iat": int(timestamp),
                "exp": int(timestamp + JWT_LIFETIME_SECONDS),
                "sub": str(existing_user.id),
            }

            return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        else:
            abort(
            401,
            "Unauthorized"
            )
    except JWTError as e:
        abort(
            401,
            "Unauthorized"
            )

def decode_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        six.raise_from(Unauthorized, e)


def get_secret(user, token_info) -> str:
    return '''
    You are user_id {user} and the secret is 'wbevuec'.
    Decoded token claims: {token_info}.
    '''.format(user=user, token_info=token_info)


def _current_timestamp() -> int:
    return int(time.time())
