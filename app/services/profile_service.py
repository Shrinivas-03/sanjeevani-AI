from app import db
from app.models.user_model import User

class ProfileService:
    @staticmethod
    def get_profile(user_id):
        try:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}, 404
            
            return {'profile': user.to_dict()}, 200
        except Exception as e:
            return {'error': 'Failed to fetch profile'}, 500
    
    @staticmethod
    def update_profile(user_id, profile_data):
        try:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}, 404
            
            # Update allowed fields
            allowed_fields = ['name', 'age', 'gender', 'contact', 'medical_history']
            for field in allowed_fields:
                if field in profile_data:
                    setattr(user, field, profile_data[field])
            
            db.session.commit()
            return {
                'message': 'Profile updated successfully',
                'profile': user.to_dict()
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to update profile'}, 500
