from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    result, status_code = AuthService.register_user(
        email=data['email'],
        password=data['password'],
        name=data.get('name')
    )
    
    return jsonify(result), status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    result, status_code = AuthService.login_user(
        email=data['email'],
        password=data['password']
    )
    
    return jsonify(result), status_code

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # JWT tokens are stateless, so logout is handled client-side
    # You could implement a token blacklist here if needed
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    current_user_id = get_jwt_identity()
    return jsonify({
        'message': 'Token is valid',
        'user_id': current_user_id
    }), 200
