from flask import Blueprint, request, jsonify
from app.models import TumorImage, User
from app.extensions import db
from app.utils.decorators import token_required

bp = Blueprint('images', __name__, url_prefix='/api/images')


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
    """Upload a tumor image (DICOM)"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'dcm', 'dicom'}
        file_ext = file.filename.lower().split('.')[-1]
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'Only DICOM files (.dcm, .dicom) are allowed. Got .{file_ext}'}), 400
        
        # Get file size
        file.seek(0, 2)  # Seek to end
        file_size_bytes = file.tell()
        file_size_mb = file_size_bytes / (1024 * 1024)
        file.seek(0)  # Seek back to start
        
        # Validate file size (max 50MB)
        max_size_mb = 50
        if file_size_mb > max_size_mb:
            return jsonify({'error': f'File size ({file_size_mb:.2f}MB) exceeds maximum ({max_size_mb}MB)'}), 413
        
        # Create database entry
        image = TumorImage(
            user_id=current_user.user_id,
            image_path=f'uploads/{current_user.user_id}/{file.filename}',
            file_extension=file_ext,
            file_size_mb=round(file_size_mb, 2),
            is_valid=True
        )
        
        db.session.add(image)
        db.session.commit()
        
        return jsonify({
            'message': 'Image uploaded successfully',
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
    """Delete an image"""
    try:
        # Get image and verify user owns it
        image = TumorImage.query.filter_by(image_id=image_id, user_id=current_user.user_id).first()
        
        if not image:
            return jsonify({'error': 'Image not found or access denied'}), 404
        
        # Delete database entry
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({'message': 'Image deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete image: {str(e)}'}), 500
