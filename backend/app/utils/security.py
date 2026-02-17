# Security utilities

import secrets
import jwt
from datetime import datetime, timedelta
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash


class SecurityUtils:
    """Security-related utility functions"""
    
    @staticmethod
    def hash_password(password):
        """Hash a password"""
        return generate_password_hash(password)
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify a password against its hash"""
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def generate_token(length=32):
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_jwt(user_id, jwt_id, expires_in_hours=1):
        """Generate a JWT token"""
        payload = {
            'user_id': user_id,
            'jti': jwt_id,  # JWT ID for session tracking
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        return token
    
    @staticmethod
    def decode_jwt(token):
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename to prevent directory traversal"""
        # Remove any directory paths
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Remove any non-alphanumeric characters except dots, dashes, and underscores
        import re
        filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
        
        return filename
    
    @staticmethod
    def rate_limit_key(user_id, endpoint):
        """Generate a key for rate limiting"""
        return f"rate_limit:{user_id}:{endpoint}"
    
    @staticmethod
    def create_api_key():
        """Generate a secure API key"""
        return f"lung_ai_{secrets.token_urlsafe(32)}"


class PasswordPolicy:
    """Password policy enforcement"""
    
    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = False
    
    @staticmethod
    def is_strong_password(password):
        """Check if password meets policy requirements"""
        if len(password) < PasswordPolicy.MIN_LENGTH:
            return False, f"Password must be at least {PasswordPolicy.MIN_LENGTH} characters"
        
        if PasswordPolicy.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if PasswordPolicy.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if PasswordPolicy.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if PasswordPolicy.REQUIRE_SPECIAL and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            return False, "Password must contain at least one special character"
        
        return True, None
