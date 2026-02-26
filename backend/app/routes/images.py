from flask import Blueprint, request, jsonify, current_app
from app.models import TumorImage, User
from app.extensions import db
from app.utils.decorators import token_required
from app.services.image_service import ImageService
from app.services.s3_service import get_s3_service
import os
from werkzeug.utils import secure_filename

bp = Blueprint('images', __name__, url_prefix='/api/images')

# Initialize S3 service
s3_service = get_s3_service()


@bp.route('/', methods=['GET'])
@token_required
def get_images(current_user):
    """Get all images for current user"""
    try:
        # Query user's images
        images = TumorImage.query.filter_by(user_id=current_user.user_id).all()
        
        return jsonify({
            'message': 'Images retrieved successfully',
            'count': len(images),
            'images': [img.to_dict() for img in images]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve images: {str(e)}'}), 500


@bp.route('/upload', methods=['POST'])
@token_required
def upload_image(current_user):
    """Upload a medical image file"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type using config
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'npy', 'png', 'jpg', 'jpeg', 'zip', 'dcm', 'dicom'})
        file_ext = file.filename.lower().rsplit('.', 1)[-1]
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'File type .{file_ext} not allowed. Supported: {", ".join(sorted(allowed_extensions))}'}), 400
        
        # Get file size
        file.seek(0, 2)  # Seek to end
        file_size_bytes = file.tell()
        file_size_mb = file_size_bytes / (1024 * 1024)
        file.seek(0)  # Seek back to start
        
        # Validate file size (max from config or 500MB)
        max_size_bytes = current_app.config.get('MAX_CONTENT_LENGTH', 500 * 1024 * 1024)
        max_size_mb = max_size_bytes / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            return jsonify({'error': f'File size ({file_size_mb:.2f}MB) exceeds maximum ({max_size_mb:.0f}MB)'}), 413
        
        # Create user upload directory
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        user_upload_dir = os.path.join(upload_folder, str(current_user.user_id))
        os.makedirs(user_upload_dir, exist_ok=True)
        
        # Secure filename and save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(user_upload_dir, filename)
        
        # Save file to disk
        file.save(file_path)
        
        # Calculate file hash for duplicate detection
        file_hash = ImageService.calculate_file_hash(file_path)
        
        # Check for duplicate
        existing_image = TumorImage.query.filter_by(file_hash=file_hash).first()
        if existing_image:
            os.remove(file_path)  # Remove duplicate
            return jsonify({'error': 'This file has already been uploaded', 'image_id': existing_image.image_id}), 409
        
        # Create database entry
        image = TumorImage(
            user_id=current_user.user_id,
            image_path=file_path,
            file_extension=file_ext,
            file_size_mb=round(file_size_mb, 2),
            file_hash=file_hash,
            is_valid=True
        )
        
        db.session.add(image)
        db.session.commit()
        
        # Upload standard image files to S3 (not ZIP files)
        if file_ext in ['png', 'jpg', 'jpeg', 'dcm', 'dicom'] and s3_service.is_configured():
            try:
                # Reopen file for S3 upload
                with open(file_path, 'rb') as f:
                    s3_result = s3_service.upload_file_to_s3(
                        f,
                        current_user.user_id,
                        filename,
                        content_type=f'image/{file_ext}'
                    )
                    
                    if s3_result['success']:
                        image.s3_url = s3_result['s3_url']
                        image.s3_key = s3_result['s3_key']
                        image.s3_bucket = s3_result['s3_bucket']
                        db.session.commit()
                        current_app.logger.info(f"Image uploaded to S3: {s3_result['s3_url']}")
                    else:
                        current_app.logger.warning(f"S3 upload failed: {s3_result.get('error')}")
            except Exception as e:
                current_app.logger.error(f"Error uploading to S3: {str(e)}")
        elif file_ext == 'zip':
            current_app.logger.info(f"ZIP file not uploaded to S3, will process locally: {filename}")
        
        return jsonify({
            'message': 'Image uploaded successfully',
            'image_id': image.image_id,
            'image': image.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@bp.route('/<int:image_id>', methods=['GET'])
@token_required
def get_image(current_user, image_id):
    """Get specific image details"""
    try:
        # Get image and verify user owns it
        image = TumorImage.query.filter_by(image_id=image_id, user_id=current_user.user_id).first()
        
        if not image:
            return jsonify({'error': 'Image not found or access denied'}), 404
        
        return jsonify({
            'message': 'Image retrieved successfully',
            'image': image.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve image: {str(e)}'}), 500


@bp.route('/<int:image_id>', methods=['DELETE'])
@token_required
def delete_image(current_user, image_id):
    """Delete an image with full-stack cleanup via ImageService"""
    try:
        # We delegate ALL the hard work to the ImageService!
        # It securely handles the S3 deletion, the local file, AND the Prediction cascade delete.
        ImageService.delete_image(image_id, current_user.user_id)
        
        return jsonify({'message': 'Image, predictions, and cloud files deleted successfully'}), 200
        
    except ValueError as e:
        # Catches "Image not found" from the service
        return jsonify({'error': str(e)}), 404
        
    except Exception as e:
        # Catches any catastrophic database/S3 errors
        return jsonify({'error': f'Failed to process deletion: {str(e)}'}), 500
