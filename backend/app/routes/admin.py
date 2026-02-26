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
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # ===== USER METRICS =====
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        deactivated_users = User.query.filter_by(is_active=False).count()
        admin_users = User.query.filter_by(role='ADMIN').count()
        patient_users = User.query.filter_by(role='PATIENT').count()
        
        # New signups in last 30 days
        new_signups_30d = User.query.filter(
            User.created_at >= thirty_days_ago
        ).count()
        
        # ===== IMAGE METRICS =====
        total_images = TumorImage.query.count()
        valid_images = TumorImage.query.filter_by(is_valid=True).count()
        
        recent_images = TumorImage.query.filter(
            TumorImage.uploaded_at >= thirty_days_ago
        ).count()
        
        # ===== PREDICTION METRICS =====
        total_predictions = Prediction.query.count()
        
        recent_predictions = Prediction.query.filter(
            Prediction.created_at >= thirty_days_ago
        ).count()
        
        # Predictions by stage - ALWAYS return stages 0-4 (fill zeros for missing)
        stage_counts = db.session.query(
            Prediction.cancer_stage,
            func.count(Prediction.prediction_id)
        ).group_by(Prediction.cancer_stage).all()
        
        stages_dict = {str(stage): count for stage, count in stage_counts}
        
        # Ensure all stages 0-4 are present
        by_stage = {
            '0': stages_dict.get('0', 0),
            '1': stages_dict.get('1', 0),
            '2': stages_dict.get('2', 0),
            '3': stages_dict.get('3', 0),
            '4': stages_dict.get('4', 0)
        }
        
        # Average confidence (as percentage)
        avg_confidence = db.session.query(
            func.avg(Prediction.confidence)
        ).scalar() or 0.0
        avg_confidence_pct = round(float(avg_confidence) * 100, 2)
        
        # ===== AI HEALTH METRICS =====
        # Inference Success Rate: (valid images with ≥1 prediction) / (total valid images)
        # Using subquery to find valid images with predictions
        images_with_predictions = db.session.query(
            func.count(func.distinct(Prediction.image_id))
        ).join(
            TumorImage, Prediction.image_id == TumorImage.image_id
        ).filter(
            TumorImage.is_valid == True,
            Prediction.image_id.isnot(None)
        ).scalar() or 0
        
        inference_success_rate = 0.0
        if valid_images > 0:
            inference_success_rate = round((images_with_predictions / valid_images) * 100, 2)
        
        return jsonify({
            'message': 'Statistics retrieved successfully',
            'stats': {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'deactivated': deactivated_users,
                    'admins': admin_users,
                    'patients': patient_users,
                    'new_30_days': new_signups_30d
                },
                'images': {
                    'total': total_images,
                    'valid': valid_images,
                    'recent_30_days': recent_images
                },
                'predictions': {
                    'total': total_predictions,
                    'recent_30_days': recent_predictions,
                    'average_confidence': avg_confidence_pct,
                    'by_stage': by_stage
                },
                'ai': {
                    'inference_success_rate': inference_success_rate
                }
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
