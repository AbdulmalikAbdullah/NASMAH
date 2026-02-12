# Input validation utilities

import re
from flask import jsonify


class Validators:
    """Collection of input validators"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return False, "Email is required"
        
        # Basic email regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return False, "Invalid email format"
        
        return True, None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        return True, None
    
    @staticmethod
    def validate_name(name, field_name="Name"):
        """Validate name fields"""
        if not name:
            return False, f"{field_name} is required"
        
        if len(name) < 2:
            return False, f"{field_name} must be at least 2 characters long"
        
        if len(name) > 100:
            return False, f"{field_name} must not exceed 100 characters"
        
        if not re.match(r'^[a-zA-Z\s-]+$', name):
            return False, f"{field_name} can only contain letters, spaces, and hyphens"
        
        return True, None
    
    @staticmethod
    def validate_role(role):
        """Validate user role"""
        valid_roles = ['PATIENT', 'ADMIN']
        if role not in valid_roles:
            return False, f"Role must be one of: {', '.join(valid_roles)}"
        
        return True, None
    
    @staticmethod
    def validate_cancer_stage(stage):
        """Validate cancer stage value"""
        valid_stages = ['0', '1', '2', '3', '4']
        if str(stage) not in valid_stages:
            return False, f"Cancer stage must be one of: {', '.join(valid_stages)}"
        
        return True, None
    
    @staticmethod
    def validate_confidence(confidence):
        """Validate confidence value"""
        try:
            conf = float(confidence)
            if conf < 0 or conf > 1:
                return False, "Confidence must be between 0 and 1"
            return True, None
        except (ValueError, TypeError):
            return False, "Confidence must be a number"
    
    @staticmethod
    def validate_file_size(file_size_mb, max_size=50):
        """Validate file size"""
        if file_size_mb > max_size:
            return False, f"File size must not exceed {max_size} MB"
        
        return True, None


def validate_request_data(data, required_fields):
    """Validate that all required fields are present in request data"""
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, None
