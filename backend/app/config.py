import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'lung_ai.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB max file size (allow batch zips)
    ALLOWED_EXTENSIONS = {'npy', 'png', 'jpg', 'jpeg', 'zip', 'dcm', 'dicom'}
    
    # AI "OLD" Model settings
    # MODEL_PATH = os.path.join(BASE_DIR, 'models', 'unet_lung_segmentation.pth')
    # MODEL_NAME = 'unet_lung_segmentation'

    # AI "NEW" Model settings
    MODEL_PATH = os.path.join(BASE_DIR, 'models', 'resnet34_lung_segmentation.pth')
    MODEL_NAME = 'resnet34_lung_segmentation'
    
    # Ensure necessary directories exist
    @staticmethod
    def init_app(app):
        """Initialize application directories"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.join(Config.BASE_DIR, 'instance'), exist_ok=True)
        os.makedirs(os.path.join(Config.BASE_DIR, 'models'), exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False




config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
