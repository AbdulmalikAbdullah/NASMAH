from flask import Blueprint, request, jsonify
from app.models import SystemLog, User
from app.extensions import db
from app.utils.decorators import token_required, admin_required
from datetime import datetime

bp = Blueprint('logs', __name__, url_prefix='/api/logs')


@bp.route('/', methods=['GET'])
@token_required
@admin_required
def get_logs(current_user):
    """Get system logs (admin only)"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        user_id = request.args.get('user_id', type=int)
        action = request.args.get('action')
        
        # Build query
        query = SystemLog.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if action:
            query = query.filter(SystemLog.action.ilike(f'%{action}%'))
        
        # Order by most recent
        query = query.order_by(SystemLog.log_time.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        logs_data = []
        for log in pagination.items:
            log_dict = log.to_dict()
            # Add user info if available
            if log.user_id:
                user = User.query.get(log.user_id)
                if user:
                    log_dict['user_email'] = user.email
                    log_dict['user_name'] = f"{user.Fname} {user.Lname}"
            logs_data.append(log_dict)
        
        return jsonify({
            'message': 'Logs retrieved successfully',
            'logs': logs_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/user/<int:user_id>', methods=['GET'])
@token_required
@admin_required
def get_user_logs(current_user, user_id):
    """Get logs for specific user (admin only)"""
    try:
        logs = SystemLog.query.filter_by(user_id=user_id).order_by(SystemLog.log_time.desc()).limit(100).all()
        
        return jsonify({
            'message': 'User logs retrieved successfully',
            'count': len(logs),
            'logs': [log.to_dict() for log in logs]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/actions', methods=['GET'])
@token_required
@admin_required
def get_log_actions(current_user):
    """Get list of all logged actions (admin only)"""
    try:
        # Get distinct actions
        actions = db.session.query(SystemLog.action).distinct().all()
        action_list = [action[0] for action in actions]
        
        return jsonify({
            'message': 'Log actions retrieved successfully',
            'actions': action_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
