from flask import Blueprint, request, jsonify
from app.models import User, UserSession
from app.extensions import db
from app.services.auth_service import AuthService
from app.utils.validators import Validators, validate_request_data
from app.utils.security import SecurityUtils
import uuid
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['fname', 'lname', 'email', 'password']
        is_valid, error = validate_request_data(data, required)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Validate email format
        is_valid, error = Validators.validate_email(data['email'])
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Validate password strength
        is_valid, error = Validators.validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Validate names
        is_valid, error = Validators.validate_name(data['fname'], 'First name')
        if not is_valid:
            return jsonify({'error': error}), 400
        
        is_valid, error = Validators.validate_name(data['lname'], 'Last name')
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user
        user = AuthService.create_user(
            fname=data['fname'],
            lname=data['lname'],
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'PATIENT')
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed: ' + str(e)}), 500


@bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['email', 'password']
        is_valid, error = validate_request_data(data, required)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Authenticate user
        user = AuthService.authenticate_user(data['email'], data['password'])
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate JWT token
        jwt_id = str(uuid.uuid4())
        access_token = SecurityUtils.generate_jwt(user.user_id, jwt_id, expires_in_hours=1)
        refresh_token = SecurityUtils.generate_jwt(user.user_id, jwt_id, expires_in_hours=24)
        
        # Create session with access token
        session = AuthService.create_session(
            user_id=user.user_id,
            token=access_token,
            jwt_id=jwt_id,
            expires_in_hours=1
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 3600,  # 1 hour in seconds
            'user': {
                'user_id': user.user_id,
                'email': user.email,
                'Fname': user.Fname,
                'Lname': user.Lname,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed: ' + str(e)}), 500


@bp.route('/logout', methods=['POST'])
def logout():
    """Logout user - revoke session"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid authorization header'}), 400
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Revoke session
        success = AuthService.revoke_session(token)
        if not success:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Logout failed: ' + str(e)}), 500


@bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh JWT token"""
    try:
        # Get refresh token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid authorization header'}), 400
        
        refresh_token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Decode refresh token
        payload, error = SecurityUtils.decode_jwt(refresh_token)
        if error:
            return jsonify({'error': error}), 401
        
        user_id = payload.get('user_id')
        jwt_id = payload.get('jti')
        
        # Get user
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate new access token
        new_access_token = SecurityUtils.generate_jwt(user.user_id, jwt_id, expires_in_hours=1)
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'access_token': new_access_token,
            'expires_in': 3600  # 1 hour in seconds
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed: ' + str(e)}), 500
