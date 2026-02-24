# # Image preprocessing utilities

# import numpy as np
# from PIL import Image
# import pydicom


# class ImagePreprocessor:
#     """Handles DICOM image preprocessing for AI model"""
    
#     @staticmethod
#     def load_dicom(file_path):
#         """Load DICOM file"""
#         try:
#             dicom_data = pydicom.dcmread(file_path)
#             return dicom_data
#         except Exception as e:
#             raise ValueError(f"Failed to load DICOM file: {str(e)}")
    
#     @staticmethod
#     def extract_dicom_metadata(dicom_data):
#         """Extract metadata from DICOM file"""
#         metadata = {}
        
#         try:
#             # Image dimensions
#             if hasattr(dicom_data, 'PixelSpacing'):
#                 pixel_spacing = dicom_data.PixelSpacing
#                 metadata['width_mm'] = pixel_spacing[0] * dicom_data.Rows
#                 metadata['height_mm'] = pixel_spacing[1] * dicom_data.Columns
            
#             if hasattr(dicom_data, 'SliceThickness'):
#                 metadata['depth_mm'] = dicom_data.SliceThickness
            
#             # Patient info (optional)
#             if hasattr(dicom_data, 'PatientID'):
#                 metadata['patient_id'] = dicom_data.PatientID
            
#             if hasattr(dicom_data, 'StudyDate'):
#                 metadata['study_date'] = dicom_data.StudyDate
            
#         except Exception as e:
#             print(f"Warning: Could not extract all metadata: {str(e)}")
        
#         return metadata
    
#     @staticmethod
#     def dicom_to_array(dicom_data):
#         """Convert DICOM to numpy array"""
#         try:
#             pixel_array = dicom_data.pixel_array
#             return pixel_array
#         except Exception as e:
#             raise ValueError(f"Failed to extract pixel data: {str(e)}")
    
#     @staticmethod
#     def normalize_image(image_array):
#         """Normalize image pixel values to 0-1 range"""
#         min_val = np.min(image_array)
#         max_val = np.max(image_array)
        
#         if max_val - min_val == 0:
#             return image_array
        
#         normalized = (image_array - min_val) / (max_val - min_val)
#         return normalized
    
#     @staticmethod
#     def resize_image(image_array, target_size=(224, 224)):
#         """Resize image to target size"""
#         # Convert to PIL Image
#         image = Image.fromarray(image_array)
        
#         # Resize
#         resized = image.resize(target_size, Image.LANCZOS)
        
#         # Convert back to numpy array
#         return np.array(resized)
    
#     @staticmethod
#     def preprocess_for_model(file_path, target_size=(224, 224)):
#         """Complete preprocessing pipeline for AI model"""
#         # Load DICOM
#         dicom_data = ImagePreprocessor.load_dicom(file_path)
        
#         # Extract metadata
#         metadata = ImagePreprocessor.extract_dicom_metadata(dicom_data)
        
#         # Convert to array
#         image_array = ImagePreprocessor.dicom_to_array(dicom_data)
        
#         # Normalize
#         normalized = ImagePreprocessor.normalize_image(image_array)
        
#         # Resize
#         resized = ImagePreprocessor.resize_image(normalized, target_size)
        
#         # Add batch and channel dimensions
#         # Shape: (1, 1, height, width) for grayscale medical images
#         preprocessed = np.expand_dims(np.expand_dims(resized, 0), 0)
        
#         return preprocessed, metadata
    
#     @staticmethod
#     def validate_dicom(file_path):
#         """Validate that file is a valid DICOM file"""
#         try:
#             dicom_data = pydicom.dcmread(file_path)
            
#             # Check for essential attributes
#             if not hasattr(dicom_data, 'pixel_array'):
#                 return False, "DICOM file does not contain pixel data"
            
#             return True, None
#         except Exception as e:
#             return False, f"Invalid DICOM file: {str(e)}"


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
        