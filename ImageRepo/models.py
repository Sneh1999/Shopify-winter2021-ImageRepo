from datetime import datetime
from config import db, ma
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema


class Permissions(db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
    image_id = db.Column('image_id', db.Integer, db.ForeignKey('images.id'))

class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(300), nullable=False)
    download_token = db.Column(db.String(300), nullable=False)
    admin_id = db.Column('admin_id', db.Integer, nullable=False)
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lname = db.Column(db.String(32))
    fname = db.Column(db.String(32))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.deferred(db.Column(db.String(100)))
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    images = db.relationship(
        "Images",
        secondary = "permissions",
        backref="user",
        lazy="joined",

    )


class UserSchema(ModelSchema):
    images = fields.Nested("ImageSchema",  many=True)
    class Meta:
        model = User
        sqla_session = db.session


class ImageSchema(ModelSchema):
    class Meta:
        model = Images
        sqla_session = db.session




