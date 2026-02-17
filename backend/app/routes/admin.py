from flask import Blueprint, request, jsonify
from app.models import User, SystemLog, TumorImage, Prediction
from app.extensions import db
from app.utils.decorators import token_required, admin_required
from sqlalchemy import func

bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@bp.route('/users', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user):
    """Get all users (admin only)"""
    try:
        users = User.query.all()
        
        users_data = []
        for user in users:
            # Get user statistics
            image_count = TumorImage.query.filter_by(user_id=user.user_id).count()
            prediction_count = Prediction.query.filter_by(user_id=user.user_id).count()
            
            user_dict = user.to_dict()
            user_dict['image_count'] = image_count
            user_dict['prediction_count'] = prediction_count
            users_data.append(user_dict)
        
        return jsonify({
            'message': 'Users retrieved successfully',
            'count': len(users_data),
            'users': users_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
@admin_required
def get_user(current_user, user_id):
    """Get specific user details (admin only)"""
    try:
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get detailed statistics
        image_count = TumorImage.query.filter_by(user_id=user.user_id).count()
        prediction_count = Prediction.query.filter_by(user_id=user.user_id).count()
        
        user_dict = user.to_dict()
        user_dict['image_count'] = image_count
        user_dict['prediction_count'] = prediction_count
        
        return jsonify({
            'message': 'User retrieved successfully',
            'user': user_dict
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/users/<int:user_id>/activate', methods=['PUT'])
@token_required
@admin_required
def activate_user(current_user, user_id):
    """Activate/deactivate user (admin only)"""
    try:
        data = request.get_json()
        is_active = data.get('is_active')
        
        if is_active is None:
            return jsonify({'error': 'is_active field is required'}), 400
        
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent admin from deactivating themselves
        if user.user_id == current_user.user_id:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        
        user.is_active = is_active
        db.session.commit()
        
        return jsonify({
            'message': f'User {"activated" if is_active else "deactivated"} successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
@token_required
@admin_required
def get_statistics(current_user):
    """Get system statistics (admin only)"""
    try:
        # Total users
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(role='ADMIN').count()
        patient_users = User.query.filter_by(role='PATIENT').count()
        
        # Total images and predictions
        total_images = TumorImage.query.count()
        total_predictions = Prediction.query.count()
        
        # Predictions by stage
        stage_counts = db.session.query(
            Prediction.cancer_stage,
            func.count(Prediction.prediction_id)
        ).group_by(Prediction.cancer_stage).all()
        
        stages_dict = {stage: count for stage, count in stage_counts}
        
        # Average confidence
        avg_confidence = db.session.query(
            func.avg(Prediction.confidence)
        ).scalar() or 0.0
        
        # Recent activity (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_images = TumorImage.query.filter(
            TumorImage.uploaded_at >= thirty_days_ago
        ).count()
        
        recent_predictions = Prediction.query.filter(
            Prediction.created_at >= thirty_days_ago
        ).count()
        
        return jsonify({
            'message': 'Statistics retrieved successfully',
            'stats': {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'admins': admin_users,
                    'patients': patient_users
                },
                'images': {
                    'total': total_images,
                    'recent_30_days': recent_images
                },
                'predictions': {
                    'total': total_predictions,
                    'recent_30_days': recent_predictions,
                    'average_confidence': float(avg_confidence),
                    'by_stage': stages_dict
                }
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
