from flask import Flask
from flask_cors import CORS
from app.extensions import db
from app.config import Config
import os


def create_app(config_class=Config):
    """Application factory pattern"""
    # Create Flask app with instance path relative to app module
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    instance_path = os.path.join(app_root, 'instance')
    
    app = Flask(__name__, instance_path=instance_path)
    app.config.from_object(config_class)
    
    # Ensure required directories exist
    os.makedirs(instance_path, exist_ok=True)
    os.makedirs(os.path.join(app_root, 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(app_root, 'models'), exist_ok=True)
    
    # Update database URI to use absolute path
    db_path = os.path.join(instance_path, 'lung_ai.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    # Initialize CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from app.routes import auth, images, predictions, admin, logs
    app.register_blueprint(auth.bp)
    app.register_blueprint(images.bp)
    app.register_blueprint(predictions.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(logs.bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'Lung Cancer AI Backend'}, 200
    
    return app
