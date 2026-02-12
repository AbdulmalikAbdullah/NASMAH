# Flask decorators for common functionality

from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app.models import User, UserSession
from app.services.logging_service import LoggingService


def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode token
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            
            # Check if session is valid
            session = UserSession.query.filter_by(jwt_id=data['jti']).first()
            if not session or session.is_revoked:
                return jsonify({'error': 'Session has been revoked'}), 401
            
            # Get current user
            current_user = User.query.filter_by(user_id=data['user_id']).first()
            
            if not current_user or not current_user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 401
        
        # Pass current user to route
        return f(current_user, *args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'ADMIN':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def log_action(action_template):
    """Decorator to log user actions"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Execute the route function
            result = f(*args, **kwargs)
            
            try:
                # Try to get current user from args (if token_required was used)
                current_user = None
                if args and hasattr(args[0], 'user_id'):
                    current_user = args[0]
                
                # Format action message
                action = action_template.format(**kwargs)
                
                # Log the action
                user_id = current_user.user_id if current_user else None
                LoggingService.log_action(action, user_id)
            except Exception as e:
                # Don't fail the request if logging fails
                print(f"Logging error: {str(e)}")
            
            return result
        
        return decorated
    return decorator


def validate_json(f):
    """Decorator to validate that request contains JSON data"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        return f(*args, **kwargs)
    
    return decorated


def handle_errors(f):
    """Decorator to handle common errors"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except FileNotFoundError as e:
            return jsonify({'error': 'Resource not found'}), 404
        except Exception as e:
            current_app.logger.error(f"Unhandled error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return decorated
