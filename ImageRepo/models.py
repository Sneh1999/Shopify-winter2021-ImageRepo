from datetime import datetime
from config import db, ma
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    lname = db.Column(db.String(32))
    fname = db.Column(db.String(32))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100))
    images = db.relationship(
        "Images",
        backref="user",
        cascade="all, delete, delete-orphan",
        single_parent=True,
        order_by="desc(Images.timestamp)",
    )

class Images(db.Model):
    __table__name = "image"
    image_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"),nullable=False)
    image = db.Column(db.String(300), nullable=False)
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class UserSchema(ModelSchema):

    class Meta:
        model = User
        sqla_session = db.session

    images = fields.Nested("UserImageSchema", default=[], many=True)


class UserImageSchema(ModelSchema):
    """
    This class exists to get around a recursion issue
    """

    image_id = fields.Int()
    user_id = fields.Int()
    image = fields.Str()
    timestamp = fields.Str()


class ImageSchema(ModelSchema):

    class Meta:
        model = Images
        sqla_session = db.session

    user = fields.Nested("ImageUserSchema", default=None)


class ImageUserSchema(ModelSchema):
    """
    This class exists to get around a recursion issue
    """
    user_id = fields.Int()
    lname = fields.Str()
    fname = fields.Str()
    email = fields.Str()
    password = fields.Str()
    timestamp = fields.Str()