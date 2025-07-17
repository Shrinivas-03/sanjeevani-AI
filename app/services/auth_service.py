from app import db
from app.models.user_model import User
from flask_jwt_extended import create_access_token
import re

class AuthService:
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def register_user(email, password, name=None):
        if not AuthService.validate_email(email):
            return {'error': 'Invalid email format'}, 400
        
        if len(password) < 6:
            return {'error': 'Password must be at least 6 characters'}, 400
        
        if User.query.filter_by(email=email).first():
            return {'error': 'Email already registered'}, 400
        
        try:
            user = User(email=email, name=name)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            access_token = create_access_token(identity=user.id)
            return {
                'message': 'User registered successfully',
                'access_token': access_token,
                'user': user.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'error': 'Registration failed'}, 500
    
    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return {'error': 'Invalid email or password'}, 401
        
        access_token = create_access_token(identity=user.id)
        return {
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }, 200
