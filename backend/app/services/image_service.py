# Service layer for image handling logic

import os
import hashlib
from werkzeug.utils import secure_filename
from app.models import TumorImage, Prediction
from app.extensions import db
from app.services.s3_service import get_s3_service
from flask import current_app


class ImageService:
    """Handles image upload and management business logic"""
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    
    @staticmethod
    def calculate_file_hash(file_path):
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def get_file_size_mb(file_path):
        """Get file size in MB"""
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    
    @staticmethod
    def save_image(file, user_id):
        """Save uploaded image file"""
        if not ImageService.allowed_file(file.filename):
            raise ValueError('Invalid file type. Only DICOM files (.dcm, .dicom) are allowed')
        
        # Create user-specific upload directory
        user_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
        os.makedirs(user_upload_dir, exist_ok=True)
        
        # Generate secure filename
        filename = secure_filename(file.filename)
        file_path = os.path.join(user_upload_dir, filename)
        
        # Save file
        file.save(file_path)
        
        # Calculate file properties
        file_hash = ImageService.calculate_file_hash(file_path)
        file_size_mb = ImageService.get_file_size_mb(file_path)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # Check if file already exists (by hash)
        existing_image = TumorImage.query.filter_by(file_hash=file_hash).first()
        if existing_image:
            os.remove(file_path)  # Remove duplicate file
            raise ValueError('This image has already been uploaded')
        
        # Create database entry
        image = TumorImage(
            user_id=user_id,
            image_path=file_path,
            file_extension=file_extension,
            file_size_mb=file_size_mb,
            file_hash=file_hash
        )
        
        db.session.add(image)
        db.session.commit()
        
        return image
    
    @staticmethod
    def get_user_images(user_id):
        """Get all images for a user"""
        return TumorImage.query.filter_by(user_id=user_id).order_by(TumorImage.uploaded_at.desc()).all()
    
    @staticmethod
    def get_image_by_id(image_id, user_id=None):
        """Get image by ID, optionally filter by user_id"""
        query = TumorImage.query.filter_by(image_id=image_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()
    
    @staticmethod
    def delete_image(image_id, user_id):
        """Delete an image, its associated predictions, and cloud files"""
        image = TumorImage.query.filter_by(image_id=image_id, user_id=user_id).first()
        
        if not image:
            raise ValueError('Image not found or access denied')
        
        try:
            # 1. CASCADE DELETE: Remove associated predictions first
            Prediction.query.filter_by(image_id=image_id).delete()
            
            # 2. CLOUD DELETION: Remove from AWS S3
            if image.s3_key:
                s3_service = get_s3_service()
                s3_service.delete_file_from_s3(image.s3_key)
            
            # 3. LOCAL DELETION: Fallback for older legacy files
            if image.image_path and os.path.exists(image.image_path):
                try:
                    os.remove(image.image_path)
                except Exception as e:
                    current_app.logger.warning(f"Could not delete local file {image.image_path}: {e}")
            
            # 4. DB DELETION: Remove the parent image record
            db.session.delete(image)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to delete image and predictions: {str(e)}")
            raise ValueError(f"Deletion failed: {str(e)}")
