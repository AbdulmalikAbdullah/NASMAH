import numpy as np
import cv2
import pydicom

class WebCTPreprocessor:
    """Preprocess raw DICOM scans to feed the model"""

    @staticmethod
    def load_dicom(file_path):
        """Load DICOM"""
        dicom = pydicom.dcmread(file_path)
        return dicom

    @staticmethod
    def dicom_to_array(dicom):
        """Convert DICOM pixels to HU (Hounsfield Units)"""
        image = dicom.pixel_array.astype(np.int16)
        slope = getattr(dicom, 'RescaleSlope', 1)
        intercept = getattr(dicom, 'RescaleIntercept', 0)
        hu_image = image * slope + intercept
        return hu_image

    @staticmethod
    def apply_lung_window(image, center=-600, width=1500):
        """Apply lung windowing"""
        lower = center - width // 2
        upper = center + width // 2
        image = np.clip(image, lower, upper)
        return image

    @staticmethod
    def normalize_image(image):
        """Normalize to [-1,1] like your training data"""
        image = (image - np.min(image)) / (np.max(image) - np.min(image))
        image = image * 2 - 1
        return image.astype(np.float32)

    @staticmethod
    def resize_image(image, target_size=(256,256)):
        """Resize to match training dataset"""
        return cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)

    @staticmethod
    def preprocess_for_model(file_path):
        """Full pipeline for web upload"""
        dicom = WebCTPreprocessor.load_dicom(file_path)
        image = WebCTPreprocessor.dicom_to_array(dicom)
        image = WebCTPreprocessor.apply_lung_window(image)
        image = WebCTPreprocessor.resize_image(image)
        image = WebCTPreprocessor.normalize_image(image)
        # Add channel + batch dimensions
        image = np.expand_dims(np.expand_dims(image, 0), 0)
        return image
    
    @staticmethod
    def validate_dicom(file_path):
        """Validate that file is a valid DICOM file"""
        try:
            dicom_data = pydicom.dcmread(file_path)
            
            # Check for essential attributes
            if not hasattr(dicom_data, 'pixel_array'):
                return False, "DICOM file does not contain pixel data"
            
            return True, None
        except Exception as e:
            return False, f"Invalid DICOM file: {str(e)}"
        