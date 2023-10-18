from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
import datetime

db = SQLAlchemy()


def get_uuid():
    return uuid4().hex

def now():
    return datetime.datetime.now()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(345), unique=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.Text, nullable=False)

    # Serializes the object
    @staticmethod
    def serialize(user) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
        }


# Model for Products
class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    url = db.Column(db.Text, nullable=False, unique=True)
    user_id = db.Column(db.String(32), nullable=False)
    title = db.Column(db.String(345), nullable=False, unique=True)
    latest_price = db.Column(db.Integer, nullable=False, default=0)
    target_price = db.Column(db.Integer, nullable=True)
    image = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, default=now)

    @staticmethod
    def get_fields() -> list:
        """
        Returns all of the fields used in here
        """
        return ['id', 'url', 'user_id', 'title', 'latest_price', 'image', 'date_added']

    # Serializes the object
    @staticmethod
    def serialize(product) -> dict:
        return {
            "id": product.id,
            "url": product.url,
            "user_id": product.user_id,
            "title": product.title,
            "latest_price": product.latest_price,
            "target_price": product.target_price,
            "image": product.image,
            "date_added": product.date_added
        }


# Model to store all the products price history
class PriceHistory(db.Model):
    __tablename__ = "priceHistory"
    history_id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    product_id = db.Column(db.String(32), nullable=False)
    date = db.Column(db.DateTime, default=now)
    price = db.Column(db.Integer, nullable=True, default=0)

    @staticmethod
    def get_fields() -> list:
        """
        Returns all of the fields used in here
        """
        return ['history_id', 'product_id', 'date', 'price']
    

    # Serializes the object
    @staticmethod
    def serialize(productHistory) -> dict:
        return {
            "history_id": productHistory.history_id,
            "product_id": productHistory.product_id,
            "date": productHistory.data,
            "price": productHistory.price,
        }
