from datetime import datetime
from app.extensions import db


class User(db.Model):
    """User model - PATIENT or ADMIN"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    Fname = db.Column(db.String(100), nullable=False)
    Lname = db.Column(db.String(100), nullable=False)
    
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    role = db.Column(db.String(10), nullable=False, default='PATIENT')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tumor_images = db.relationship('TumorImage', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sessions = db.relationship('UserSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    logs = db.relationship('SystemLog', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'user_id': self.user_id,
            'Fname': self.Fname,
            'Lname': self.Lname,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TumorImage(db.Model):
    """Tumor image model - stores uploaded DICOM images"""
    __tablename__ = 'tumor_images'
    
    image_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    
    image_path = db.Column(db.String(500), nullable=False)
    
    file_extension = db.Column(db.String(10), nullable=False)
    file_size_mb = db.Column(db.Float, nullable=False)
    file_hash = db.Column(db.String(64), unique=True)
    
    is_valid = db.Column(db.Boolean, nullable=False, default=True)
    
    # AWS S3 Storage fields
    s3_url = db.Column(db.String(1000), nullable=True)
    s3_key = db.Column(db.String(500), unique=True, nullable=True, index=True)
    s3_bucket = db.Column(db.String(255), nullable=True)
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='image', lazy='dynamic')
    
    def __repr__(self):
        return f'<TumorImage {self.image_id}>'
    
    def to_dict(self):
        """Convert image to dictionary"""
        return {
            'image_id': self.image_id,
            'user_id': self.user_id,
            'image_path': self.image_path,
            'file_extension': self.file_extension,
            'file_size_mb': self.file_size_mb,
            'file_hash': self.file_hash,
            'is_valid': self.is_valid,
            's3_url': self.s3_url,
            's3_key': self.s3_key,
            's3_bucket': self.s3_bucket,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class Prediction(db.Model):
    """AI prediction model - stores cancer stage predictions"""
    __tablename__ = 'predictions'
    
    prediction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    image_id = db.Column(db.Integer, db.ForeignKey('tumor_images.image_id', ondelete='SET NULL'))
    
    cancer_stage = db.Column(db.String(1), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    
    model_name = db.Column(db.String(100), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Prediction {self.prediction_id} - Stage {self.cancer_stage}>'
    
    def to_dict(self):
        """Convert prediction to dictionary"""
        return {
            'prediction_id': self.prediction_id,
            'user_id': self.user_id,
            'image_id': self.image_id,
            'cancer_stage': self.cancer_stage,
            'confidence': self.confidence,
            'model_name': self.model_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SystemLog(db.Model):
    """System log model - tracks user actions"""
    __tablename__ = 'system_logs'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    action = db.Column(db.String(255), nullable=False)
    
    log_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemLog {self.log_id} - {self.action}>'
    
    def to_dict(self):
        """Convert log to dictionary"""
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'action': self.action,
            'log_time': self.log_time.isoformat() if self.log_time else None
        }


class UserSession(db.Model):
    """User session model - manages JWT sessions"""
    __tablename__ = 'user_sessions'
    
    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    
    session_token = db.Column(db.String(500), nullable=False, unique=True)
    jwt_id = db.Column(db.String(100), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    is_revoked = db.Column(db.Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return f'<UserSession {self.session_id}>'
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'jwt_id': self.jwt_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_revoked': self.is_revoked
        }
