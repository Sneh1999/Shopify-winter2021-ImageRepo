from datetime import datetime
from config import db, ma
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    # TODO:  check if the  number here is right or not  
    lname = db.Column(db.String(32))
    fname = db.Column(db.String(32))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100))
    image = db.relationship('Permission', back_populates='user')

class Image(db.Model):
    __table__name = "image"
    image_id = db.Column(db.Integer, primary_key=True)
    
    image = db.Column(db.String(300), nullable=False)
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    user = db.relationship('Permission', back_populates='image')

class Permission(db.Model):
    __table__name = "permission"
    permission_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"),nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey("image.image_id"),nullable=False)
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    user = db.relationship('User', back_populates='image')
    image = db.relationship('Image', back_populates='user')

class UserSchema(ModelSchema):

    class Meta:
        model = User
        sqla_session = db.session

    images = fields.Nested("ImageSchema", only=("image_id",), default=[], many=True)


class ImageSchema(ModelSchema):

    class Meta:
        model = Image
        sqla_session = db.session

    user = fields.Nested("UserSchema",only=("user_id",) ,default=None, many=True)
