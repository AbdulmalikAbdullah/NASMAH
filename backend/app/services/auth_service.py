# Service layer for authentication logic

from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, UserSession
from app.extensions import db
from datetime import datetime, timedelta
import uuid


class AuthService:
    """Handles authentication business logic"""
    
    @staticmethod
    def hash_password(password):
        """Hash a password"""
        return generate_password_hash(password)
    
    @staticmethod
    def verify_password(password_hash, password):
        """Verify a password against its hash"""
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def create_user(fname, lname, email, password, role='PATIENT'):
        """Create a new user"""
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValueError('User with this email already exists')
        
        # Create new user
        user = User(
            Fname=fname,
            Lname=lname,
            email=email,
            password_hash=AuthService.hash_password(password),
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password"""
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.is_active:
            return None
        
        if AuthService.verify_password(user.password_hash, password):
            return user
        
        return None
    
    @staticmethod
    def create_session(user_id, token, jwt_id, expires_in_hours=1):
        """Create a new user session"""
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        session = UserSession(
            user_id=user_id,
            session_token=token,
            jwt_id=jwt_id,
            expires_at=expires_at
        )
        
        db.session.add(session)
        db.session.commit()
        
        return session
    
    @staticmethod
    def revoke_session(session_token):
        """Revoke a user session"""
        session = UserSession.query.filter_by(session_token=session_token).first()
        
        if session:
            session.is_revoked = True
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def is_session_valid(session_token):
        """Check if a session is valid"""
        session = UserSession.query.filter_by(session_token=session_token).first()
        
        if not session or session.is_revoked:
            return False
        
        if datetime.utcnow() > session.expires_at:
            return False
        
        return True
