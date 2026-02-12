# AI Model loader and inference

import torch
import torch.nn as nn
from flask import current_app
import os


class LungCancerModel(nn.Module):
    """
    Placeholder CNN model for lung cancer classification
    Replace this with your actual trained model architecture
    """
    def __init__(self, num_classes=5):
        super(LungCancerModel, self).__init__()
        
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        
        self.classifier = nn.Sequential(
            nn.Dropout(),
            nn.Linear(128 * 28 * 28, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(256, num_classes),
        )
    
    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x


class ModelLoader:
    """Handles AI model loading and inference"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one model instance"""
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    def load_model(self, model_path=None):
        """Load the trained model"""
        if self._model is not None:
            return self._model
        
        if model_path is None:
            model_path = current_app.config['MODEL_PATH']
        
        # Check if model file exists
        if not os.path.exists(model_path):
            print(f"Warning: Model file not found at {model_path}")
            print("Using untrained model for demonstration purposes")
            self._model = LungCancerModel(num_classes=5)
            return self._model
        
        try:
            # Load the model
            self._model = LungCancerModel(num_classes=5)
            self._model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            self._model.eval()
            
            print(f"Model loaded successfully from {model_path}")
            return self._model
        
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            print("Using untrained model for demonstration purposes")
            self._model = LungCancerModel(num_classes=5)
            return self._model
    
    def predict(self, image_tensor):
        """
        Make prediction on preprocessed image
        
        Args:
            image_tensor: PyTorch tensor of shape (1, 1, height, width)
        
        Returns:
            tuple: (predicted_stage, confidence)
        """
        if self._model is None:
            self.load_model()
        
        with torch.no_grad():
            # Convert to PyTorch tensor if needed
            if not isinstance(image_tensor, torch.Tensor):
                image_tensor = torch.FloatTensor(image_tensor)
            
            # Make prediction
            outputs = self._model(image_tensor)
            
            # Apply softmax to get probabilities
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            
            # Get predicted class and confidence
            confidence, predicted = torch.max(probabilities, 1)
            
            predicted_stage = str(predicted.item())
            confidence_score = confidence.item()
            
            return predicted_stage, confidence_score
    
    def get_all_probabilities(self, image_tensor):
        """
        Get probabilities for all cancer stages
        
        Args:
            image_tensor: PyTorch tensor of shape (1, 1, height, width)
        
        Returns:
            dict: Stage probabilities
        """
        if self._model is None:
            self.load_model()
        
        with torch.no_grad():
            if not isinstance(image_tensor, torch.Tensor):
                image_tensor = torch.FloatTensor(image_tensor)
            
            outputs = self._model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            
            # Convert to dictionary
            stage_probs = {
                '0': probabilities[0][0].item(),
                '1': probabilities[0][1].item(),
                '2': probabilities[0][2].item(),
                '3': probabilities[0][3].item(),
                '4': probabilities[0][4].item(),
            }
            
            return stage_probs
    
    def unload_model(self):
        """Unload model from memory"""
        self._model = None
        torch.cuda.empty_cache()


# Global model loader instance
model_loader = ModelLoader()
