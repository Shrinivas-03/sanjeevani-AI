from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_cors import cross_origin
import random
import string
from datetime import datetime, timedelta
# Fix the bcrypt issue by using a direct import
import bcrypt
from email_validator import validate_email, EmailNotValidError
import re

from utils.email_service import EmailService
from utils.database import DatabaseService

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

# Initialize services
email_service = EmailService()
db_service = DatabaseService()

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

# Update password hashing functions to use bcrypt directly
def hash_password(password):
    """Hash password using bcrypt"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password, hashed_password):
    """Verify password against hash"""
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password, hashed_password)

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@auth_bp.route('/login', methods=['GET', 'POST'])
@cross_origin()
def login():
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            # Validate input
            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400
            
            # Validate email format
            try:
                validated_email = validate_email(email)
                email = validated_email.email
            except EmailNotValidError:
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Get user from database
            user = db_service.get_user_by_email(email)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Check if email is verified
            if not user.get('email_verified', False):
                return jsonify({'error': 'Please verify your email before logging in'}), 401
            
            # Verify password
            if not verify_password(password, user['password_hash']):
                return jsonify({'error': 'Invalid password'}), 401
            
            # Update last login timestamp
            # You can add this to your database service
            # db_service.update_last_login(user['id'])
            
            # Success response
            return jsonify({
                'message': f'Welcome back, {user["full_name"]}!',
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'full_name': user['full_name']
                },
                'redirect_url': url_for('func.dashboard')  # Changed from 'functionality' to 'func'
            }), 200
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            return jsonify({'error': 'An error occurred during login'}), 500
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
@cross_origin()
def register():
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            full_name = data.get('full_name', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            phone = data.get('phone', '').strip()
            date_of_birth = data.get('date_of_birth', '').strip()
            gender = data.get('gender', '').strip()
            blood_group = data.get('blood_group', '').strip()
            address = data.get('address', '').strip()
            
            # Validate input
            if not all([full_name, email, password, confirm_password]):
                return jsonify({'error': 'All required fields must be filled'}), 400
            
            if password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400
            
            # Validate email format
            try:
                validated_email = validate_email(email)
                email = validated_email.email
            except EmailNotValidError:
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Validate password strength
            is_valid, message = validate_password_strength(password)
            if not is_valid:
                return jsonify({'error': message}), 400
            
            # Validate optional fields
            if gender and gender not in ['male', 'female', 'other']:
                return jsonify({'error': 'Invalid gender selection'}), 400
            
            if blood_group and blood_group not in ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']:
                return jsonify({'error': 'Invalid blood group selection'}), 400
            
            if date_of_birth:
                try:
                    from datetime import datetime
                    birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                    today = datetime.now().date()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    if age < 0 or age > 120:
                        return jsonify({'error': 'Invalid date of birth'}), 400
                except ValueError:
                    return jsonify({'error': 'Invalid date format'}), 400
            
            # Check if user already exists
            existing_user = db_service.get_user_by_email(email)
            if existing_user:
                if existing_user.get('email_verified', False):
                    return jsonify({'error': 'An account with this email already exists'}), 409
                else:
                    # User exists but not verified, allow re-registration
                    pass
            
            # Store user data temporarily (in session or database with a pending status)
            # We'll use Flask session to store this data temporarily
            session['pending_user'] = {
                'full_name': full_name,
                'email': email,
                'password': password,  # Will be hashed before storage
                'phone': phone,
                'date_of_birth': date_of_birth,
                'gender': gender,
                'blood_group': blood_group,
                'address': address
            }
            
            # Generate and store OTP
            otp_code = generate_otp()
            if not db_service.store_otp(email, otp_code):
                return jsonify({'error': 'Failed to generate verification code'}), 500
            
            # Send OTP email
            if not email_service.send_otp_email(email, otp_code, full_name):
                return jsonify({'error': 'Failed to send verification email'}), 500
            
            # Store user data temporarily in session or cache for OTP verification
            # You might want to use Redis or session storage for this
            
            return jsonify({
                'message': 'Registration initiated. Please check your email for verification code.',
                'email': email,
                'redirect_url': url_for('auth.otp_verification', email=email)
            }), 200
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return jsonify({'error': 'An error occurred during registration'}), 500
    
    return render_template('sign.html')

@auth_bp.route('/otp-verification')
@cross_origin()
def otp_verification():
    email = request.args.get('email')
    if not email:
        return redirect(url_for('auth.register'))
    return render_template('otp_verification.html', email=email)

@auth_bp.route('/verify-otp', methods=['POST'])
@cross_origin()
def verify_otp():
    try:
        data = request.get_json() if request.is_json else request.form
        otp = data.get('otp', '').strip()
        email = data.get('email', '').strip().lower()
        
        if not otp or not email:
            return jsonify({'error': 'OTP and email are required'}), 400
        
        if len(otp) != 6 or not otp.isdigit():
            return jsonify({'error': 'Invalid OTP format'}), 400
        
        # Verify OTP
        if not db_service.verify_otp(email, otp):
            # Increment attempts
            attempts = db_service.increment_otp_attempts(email)
            if attempts >= 3:
                return jsonify({'error': 'Too many failed attempts. Please request a new OTP.'}), 429
            return jsonify({'error': 'Invalid or expired OTP'}), 400
        
        # OTP verified, now complete user registration
        from flask import session
        pending_user = session.get('pending_user', {})
        
        # Only proceed if we have pending user data and emails match
        if pending_user and pending_user.get('email') == email:
            # Hash the password
            password_hash = hash_password(pending_user.get('password', ''))
            
            # Create user in database
            user_data = {
                'full_name': pending_user.get('full_name', ''),
                'email': email,
                'password_hash': password_hash,
                'phone': pending_user.get('phone', ''),
                'date_of_birth': pending_user.get('date_of_birth', ''),
                'gender': pending_user.get('gender', ''),
                'blood_group': pending_user.get('blood_group', ''),
                'address': pending_user.get('address', '')
            }
            
            # Create user in database
            user = db_service.create_user(**user_data)
            if not user:
                return jsonify({'error': 'Failed to create user account'}), 500
            
            # Mark email as verified
            db_service.verify_user_email(email)
            
            # Clear the pending user data
            session.pop('pending_user', None)
        else:
            # If we don't have pending user data, check if user already exists
            user = db_service.get_user_by_email(email)
            if user:
                # Just mark email as verified if user exists
                db_service.verify_user_email(email)
            else:
                return jsonify({'error': 'User registration data not found'}), 400
        
        return jsonify({
            'message': 'Email verified successfully!',
            'redirect_url': url_for('auth.login')
        }), 200
        
    except Exception as e:
        print(f"OTP verification error: {str(e)}")
        return jsonify({'error': 'An error occurred during verification'}), 500

@auth_bp.route('/resend-otp', methods=['POST'])
@cross_origin()
def resend_otp():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Generate new OTP
        otp_code = generate_otp()
        if not db_service.store_otp(email, otp_code):
            return jsonify({'error': 'Failed to generate verification code'}), 500
        
        # Send OTP email
        if not email_service.send_otp_email(email, otp_code):
            return jsonify({'error': 'Failed to send verification email'}), 500
        
        return jsonify({'message': 'New OTP sent successfully'}), 200
        
    except Exception as e:
        print(f"Resend OTP error: {str(e)}")
        return jsonify({'error': 'An error occurred while resending OTP'}), 500

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@cross_origin()
def forgot_password():
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            email = data.get('email', '').strip().lower()
            
            if not email:
                return jsonify({'error': 'Email is required'}), 400
            
            # Validate email format
            try:
                validated_email = validate_email(email)
                email = validated_email.email
            except EmailNotValidError:
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Check if user exists
            user = db_service.get_user_by_email(email)
            if user:
                # Generate reset token (using OTP system)
                reset_token = generate_otp()
                if db_service.store_otp(email, reset_token, 'password_reset'):
                    email_service.send_password_reset_email(email, reset_token, user.get('full_name'))
            
            # Always return success message (don't reveal if email exists)
            return jsonify({
                'message': 'If an account with this email exists, you will receive a password reset link shortly.'
            }), 200
            
        except Exception as e:
            print(f"Forgot password error: {str(e)}")
            return jsonify({'error': 'An error occurred while processing your request'}), 500
    
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
@cross_origin()
def reset_password():
    token = request.args.get('token') or (request.get_json() or request.form).get('token') if request.method == 'POST' else request.args.get('token')
    message = request.args.get('message')
    
    if not token and request.method == 'POST':
        return jsonify({'error': 'Invalid or missing reset token'}), 400
    
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            token = data.get('token', token)  # Get token from form data or URL parameter
            
            if not password or not confirm_password:
                return jsonify({'error': 'Password and confirmation are required'}), 400
            
            if password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400
            
            # Validate password strength
            is_valid, message = validate_password_strength(password)
            if not is_valid:
                return jsonify({'error': message}), 400
            
            # Find the OTP record to get the associated email
            email = db_service.get_email_by_otp(token, 'password_reset')
            if not email:
                return jsonify({'error': 'Invalid or expired reset token'}), 400
            
            # Get the user by email
            user = db_service.get_user_by_email(email)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Hash the new password
            password_hash = hash_password(password)
            
            # Update the user's password in the database
            if not db_service.update_user_password(email, password_hash):
                return jsonify({'error': 'Failed to update password'}), 500
            
            # Invalidate the OTP token
            db_service.invalidate_otp(email, token, 'password_reset')
            
            # Return success response
            return jsonify({
                'message': 'Password reset successfully. Please log in with your new password.',
                'redirect_url': url_for('auth.login')
            }), 200
            
        except Exception as e:
            print(f"Reset password error: {str(e)}")
            return jsonify({'error': 'An error occurred while resetting password'}), 500
    
    return render_template('reset_password.html', token=token, message=message)

# Helper route to complete user registration after OTP verification
@auth_bp.route('/complete-registration', methods=['POST'])
@cross_origin()
def complete_registration():
    try:
        data = request.get_json()
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        phone = data.get('phone', '').strip()
        date_of_birth = data.get('date_of_birth', '').strip()
        gender = data.get('gender', '').strip()
        blood_group = data.get('blood_group', '').strip()
        address = data.get('address', '').strip()
        
        # Hash password
        password_hash = hash_password(password)
        
        # Prepare user data
        user_data = {
            'full_name': full_name,
            'email': email,
            'password_hash': password_hash,
            'phone': phone if phone else None,
            'date_of_birth': date_of_birth if date_of_birth else None,
            'gender': gender if gender else None,
            'blood_group': blood_group if blood_group else None,
            'address': address if address else None
        }
        
        # Create user
        user = db_service.create_user(**user_data)
        if not user:
            return jsonify({'error': 'Failed to create user account'}), 500
        
        # Mark email as verified
        db_service.verify_user_email(email)
        
        return jsonify({
            'message': 'Account created successfully!',
            'user_id': user['id']
        }), 201
        
    except Exception as e:
        print(f"Complete registration error: {str(e)}")
        return jsonify({'error': 'An error occurred while creating account'}), 500
        # Mark email as verified
        db_service.verify_user_email(email)
        
        return jsonify({
            'message': 'Account created successfully!',
            'user_id': user['id']
        }), 201
        
    except Exception as e:
        print(f"Complete registration error: {str(e)}")
        return jsonify({'error': 'An error occurred while creating account'}), 500
