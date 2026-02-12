# Service layer for AI prediction logic

from app.models import Prediction, TumorImage
from app.extensions import db
from flask import current_app


class PredictionService:
    """Handles AI prediction business logic"""
    
    @staticmethod
    def make_prediction(image_id, user_id):
        """Make a prediction on an image"""
        # Get image
        image = TumorImage.query.filter_by(image_id=image_id, user_id=user_id).first()
        
        if not image:
            raise ValueError('Image not found')
        
        if not image.is_valid:
            raise ValueError('Image is not valid for prediction')
        
        # TODO: Load AI model
        # TODO: Preprocess image
        # TODO: Make prediction
        
        # Placeholder prediction
        cancer_stage = '0'  # This should come from AI model
        confidence = 0.85  # This should come from AI model
        model_name = current_app.config['MODEL_NAME']
        
        # Create prediction record
        prediction = Prediction(
            user_id=user_id,
            image_id=image_id,
            cancer_stage=cancer_stage,
            confidence=confidence,
            model_name=model_name
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        return prediction
    
    @staticmethod
    def get_user_predictions(user_id, limit=None):
        """Get all predictions for a user"""
        query = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_prediction_by_id(prediction_id, user_id=None):
        """Get prediction by ID, optionally filter by user_id"""
        query = Prediction.query.filter_by(prediction_id=prediction_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()
    
    @staticmethod
    def get_prediction_statistics(user_id):
        """Get prediction statistics for a user"""
        predictions = Prediction.query.filter_by(user_id=user_id).all()
        
        if not predictions:
            return {
                'total': 0,
                'stages': {},
                'average_confidence': 0
            }
        
        stages = {}
        total_confidence = 0
        
        for pred in predictions:
            stage = pred.cancer_stage
            stages[stage] = stages.get(stage, 0) + 1
            total_confidence += pred.confidence
        
        return {
            'total': len(predictions),
            'stages': stages,
            'average_confidence': total_confidence / len(predictions)
        }
