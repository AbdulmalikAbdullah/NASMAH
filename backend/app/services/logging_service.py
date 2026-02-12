# Service layer for logging

from app.models import SystemLog
from app.extensions import db
from datetime import datetime


class LoggingService:
    """Handles system logging business logic"""
    
    @staticmethod
    def log_action(action, user_id=None):
        """Create a system log entry"""
        log = SystemLog(
            user_id=user_id,
            action=action
        )
        
        db.session.add(log)
        db.session.commit()
        
        return log
    
    @staticmethod
    def get_logs(limit=100, user_id=None, action_filter=None):
        """Get system logs with optional filters"""
        query = SystemLog.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if action_filter:
            query = query.filter(SystemLog.action.like(f'%{action_filter}%'))
        
        query = query.order_by(SystemLog.log_time.desc()).limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_user_logs(user_id, limit=50):
        """Get logs for a specific user"""
        return SystemLog.query.filter_by(user_id=user_id).order_by(SystemLog.log_time.desc()).limit(limit).all()
    
    @staticmethod
    def get_distinct_actions():
        """Get list of all unique actions logged"""
        actions = db.session.query(SystemLog.action).distinct().all()
        return [action[0] for action in actions]
