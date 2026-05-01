from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ProductReview(db.Model):
    """Model for storing product reviews"""
    __tablename__ = 'product_reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(db.String(255), nullable=False, index=True)
    user_email = db.Column(db.String(255), nullable=False)
    user_name = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert review to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'rating': self.rating,
            'review_text': self.review_text,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<ProductReview {self.id} - Product {self.product_id}>'


class SellerReview(db.Model):
    """Model for storing seller reviews"""
    __tablename__ = 'seller_reviews'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(db.String(255), nullable=False, index=True)
    user_email = db.Column(db.String(255), nullable=False)
    user_name = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert review to dictionary"""
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'rating': self.rating,
            'review_text': self.review_text,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<SellerReview {self.id} - Seller {self.seller_id}>'


class CartItem(db.Model):
    """Model for storing shopping cart items"""
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False, index=True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert cart item to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<CartItem {self.id} - Product {self.product_id}>'


class User(db.Model):
    """Model for storing user profiles"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    fullname = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'firebase_uid': self.firebase_uid,
            'email': self.email,
            'username': self.username,
            'fullname': self.fullname,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.id} - {self.email}>'


class ChatMessage(db.Model):
    """Model for storing live chat messages"""
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=True, index=True)  # Firebase UID or anonymous
    user_email = db.Column(db.String(255), nullable=True)
    user_name = db.Column(db.String(255), nullable=False, default='Anonymous')
    message = db.Column(db.Text, nullable=False)
    sender_type = db.Column(db.String(50), nullable=False, default='customer')  # 'customer' or 'admin'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'user_name': self.user_name,
            'message': self.message,
            'sender_type': self.sender_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<ChatMessage {self.id} - {self.user_name}>'


class Part(db.Model):
    """Model for storing registered car parts"""
    __tablename__ = 'parts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert part to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'image': self.image,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Part {self.id} - {self.name}>'
