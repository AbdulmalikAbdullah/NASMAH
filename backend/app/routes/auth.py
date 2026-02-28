from flask import Blueprint, request, jsonify
from app.models import User, UserSession
from app.extensions import db
from app.services.auth_service import AuthService
from app.services.logging_service import LoggingService
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
        
        # Log the registration action
        LoggingService.log_action(
            action=f"User Registered: {user.email}",
            user_id=user.user_id
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
        
        # Log the login action
        LoggingService.log_action(
            action=f"User Login: {user.email}",
            user_id=user.user_id
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
        
        # Decode token to get user_id for logging
        payload, error = SecurityUtils.decode_jwt(token)
        user_id = payload.get('user_id') if payload else None
        
        # Revoke session
        success = AuthService.revoke_session(token)
        if not success:
            return jsonify({'error': 'Session not found'}), 404
        
        # Log the logout action
        if user_id:
            user = User.query.get(user_id)
            if user:
                LoggingService.log_action(
                    action=f"User Logout: {user.email}",
                    user_id=user_id
                )
        
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


@bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user profile"""
    from app.utils.decorators import token_required
    from functools import wraps
    
    # Manual token verification since we can't use decorator directly
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401
        
        token = auth_header[7:]
        payload, error = SecurityUtils.decode_jwt(token)
        if error:
            return jsonify({'error': error}), 401
        
        user_id = payload.get('user_id')
        user = User.query.filter_by(user_id=user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'message': 'User profile retrieved successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve user profile: ' + str(e)}), 500


@bp.route('/me', methods=['PUT'])
def update_current_user():
    """Update current user profile"""
    try:
        # Manual token verification
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401
        
        token = auth_header[7:]
        payload, error = SecurityUtils.decode_jwt(token)
        if error:
            return jsonify({'error': error}), 401
        
        user_id = payload.get('user_id')
        user = User.query.filter_by(user_id=user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'fname' in data:
            is_valid, error = Validators.validate_name(data['fname'], 'First name')
            if not is_valid:
                return jsonify({'error': error}), 400
            user.Fname = data['fname']
        
        if 'lname' in data:
            is_valid, error = Validators.validate_name(data['lname'], 'Last name')
            if not is_valid:
                return jsonify({'error': error}), 400
            user.Lname = data['lname']
        
        if 'email' in data:
            is_valid, error = Validators.validate_email(data['email'])
            if not is_valid:
                return jsonify({'error': error}), 400
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.user_id != user.user_id:
                return jsonify({'error': 'Email already in use'}), 409
            
            user.email = data['email']
        
        db.session.commit()
        
        # Log the profile update action
        LoggingService.log_action(
            action=f"Profile Updated: {user.email}",
            user_id=user.user_id
        )
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile: ' + str(e)}), 500


@bp.route('/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    try:
        # Manual token verification
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401
        
        token = auth_header[7:]
        payload, error = SecurityUtils.decode_jwt(token)
        if error:
            return jsonify({'error': error}), 401
        
        user_id = payload.get('user_id')
        user = User.query.filter_by(user_id=user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required = ['current_password', 'new_password']
        is_valid, error = validate_request_data(data, required)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Verify current password
        if not SecurityUtils.verify_password(data['current_password'], user.password_hash):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        is_valid, error = Validators.validate_password(data['new_password'])
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Update password
        user.password_hash = SecurityUtils.hash_password(data['new_password'])
        db.session.commit()
        
        # Log the password change action
        LoggingService.log_action(
            action=f"Password Changed: {user.email}",
            user_id=user.user_id
        )
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password: ' + str(e)}), 500


@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Initiate password reset by sending an email with a time-limited token"""
    try:
        data = request.get_json()
        required = ['email']
        is_valid, error = validate_request_data(data, required)
        if not is_valid:
            return jsonify({'error': error}), 400

        email = data['email']
        user = User.query.filter_by(email=email).first()

        # Always return success to avoid user enumeration; if user exists, send email
        if not user:
            return jsonify({'message': 'If an account with that email exists, a reset email was sent'}), 200

        # Generate a short-lived JWT token for password reset (1 hour)
        jwt_id = str(uuid.uuid4())
        reset_token = SecurityUtils.generate_jwt(user.user_id, jwt_id, expires_in_hours=1)

        # Build reset link (frontend should handle reset flow)
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"

        # Attempt to send via SMTP if configured, otherwise return token in response (dev fallback)
        smtp_host = os.environ.get('SMTP_HOST')
        email_sent = False
        send_error = None
        if smtp_host:
            try:
                smtp_port = int(os.environ.get('SMTP_PORT', 587))
                smtp_user = os.environ.get('SMTP_USER')
                smtp_pass = os.environ.get('SMTP_PASS')
                use_tls = os.environ.get('SMTP_USE_TLS', '1') in ['1', 'true', 'True']

                subject = 'Password reset instructions'

                # Plain text fallback (do not expose raw token)
                text_body = (
                    f"Hello {user.Fname},\n\n"
                    "To reset your password please open the reset page in your browser.\n"
                    f"If your email client supports HTML, click the link provided in this message.\n\n"
                    "If you didn't request this, ignore this email."
                )

                # HTML body with clickable link (token included only in href, not displayed)
                html_body = (
                    f"<p>Hello {user.Fname},</p>"
                    f"<p>To reset your password <a href=\"{reset_link}\">click here</a>.</p>"
                    "<p>If you didn't request this, ignore this email.</p>"
                )

                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                from_addr = os.environ.get('SMTP_FROM') or smtp_user or 'no-reply@example.com'
                msg['From'] = from_addr
                msg['To'] = user.email

                part1 = MIMEText(text_body, 'plain')
                part2 = MIMEText(html_body, 'html')
                msg.attach(part1)
                msg.attach(part2)

                server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
                if use_tls:
                    server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)

                server.sendmail(from_addr, [user.email], msg.as_string())
                server.quit()
                email_sent = True
            except Exception as e:
                send_error = str(e)

        # Log the reset request
        LoggingService.log_action(
            action=f"Password Reset Requested: {user.email}",
            user_id=user.user_id
        )

        resp = {'message': 'If an account with that email exists, a reset email was sent'}
        if not smtp_host or not email_sent:
            # Do not return the reset token in responses (avoid exposing it).
            if send_error:
                resp['send_error'] = send_error

        return jsonify(resp), 200

    except Exception as e:
        return jsonify({'error': 'Failed to initiate password reset: ' + str(e)}), 500


@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token and new password"""
    try:
        data = request.get_json()
        required = ['token', 'new_password']
        is_valid, error = validate_request_data(data, required)
        if not is_valid:
            return jsonify({'error': error}), 400

        token = data['token']
        new_password = data['new_password']

        # Decode token
        payload, decode_error = SecurityUtils.decode_jwt(token)
        if decode_error:
            return jsonify({'error': decode_error}), 400

        user_id = payload.get('user_id')
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Validate new password strength
        is_valid, error = Validators.validate_password(new_password)
        if not is_valid:
            return jsonify({'error': error}), 400

        # Update password
        user.password_hash = SecurityUtils.hash_password(new_password)
        db.session.commit()

        # Log the password reset action
        LoggingService.log_action(
            action=f"Password Reset: {user.email}",
            user_id=user.user_id
        )

        return jsonify({'message': 'Password has been reset successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reset password: ' + str(e)}), 500
