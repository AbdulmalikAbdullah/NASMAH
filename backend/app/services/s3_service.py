"""
AWS S3 Service for secure file uploads and presigned URL generation
Implements singleton pattern with timeout configuration to prevent WinError 10038
"""
import os
import uuid
import logging
from datetime import datetime
import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

# Singleton instance
_s3_service_instance = None


class S3Service:
    """
    AWS S3 Service for handling file uploads and presigned URL generation.
    
    Features:
    - Singleton pattern ensures one boto3 client per application
    - Timeout configuration prevents socket hangs (WinError 10038)
    - Supports BytesIO and file-like objects
    - Generates unique S3 keys with timestamp and UUID
    - Creates presigned URLs for private bucket access
    """
    
    def __init__(self):
        """Initialize S3 client with environment configuration"""
        self.access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
        
        # Check if S3 is configured
        self._is_configured = all([
            self.access_key,
            self.secret_key,
            self.region,
            self.bucket_name
        ])
        
        if not self._is_configured:
            logger.warning(
                "S3 not fully configured. Missing one or more environment variables: "
                "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_S3_BUCKET"
            )
            self.s3_client = None
            return
        
        # Configure boto3 with timeouts to prevent socket hangs
        config = Config(
            connect_timeout=30,  # 30 seconds to establish connection
            read_timeout=30,     # 30 seconds to read response
            retries={
                'max_attempts': 3,
                'mode': 'standard'
            }
        )
        
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
                config=config
            )
            logger.info(f"S3 client initialized successfully for bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            self.s3_client = None
            self._is_configured = False
    
    def is_configured(self):
        """Check if S3 service is properly configured"""
        return self._is_configured and self.s3_client is not None
    
    def upload_file_to_s3(self, file_obj, user_id, filename, content_type='image/png'):
        """
        Upload file to S3 with unique key generation.
        
        Args:
            file_obj: File-like object (FileStorage, BytesIO, etc.)
            user_id: User ID for folder organization
            filename: Original filename
            content_type: MIME type (default: image/png)
        
        Returns:
            dict: {
                'success': bool,
                's3_url': str (if success),
                's3_key': str (if success),
                's3_bucket': str (if success),
                'error': str (if failure)
            }
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'S3 service not configured'
            }
        
        try:
            # Generate unique S3 key: users/<user_id>/<timestamp>_<uuid>_<filename>
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = uuid.uuid4().hex[:8]
            s3_key = f"users/{user_id}/{timestamp}_{unique_id}_{filename}"
            
            # Reset file pointer to start if possible
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
            
            # Construct S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            logger.info(f"File uploaded successfully to S3: {s3_key}")
            
            return {
                'success': True,
                's3_url': s3_url,
                's3_key': s3_key,
                's3_bucket': self.bucket_name
            }
            
        except ClientError as e:
            error_msg = f"AWS ClientError during S3 upload: {e.response['Error']['Message']}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except BotoCoreError as e:
            error_msg = f"BotoCoreError during S3 upload: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error during S3 upload: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def generate_presigned_url(self, s3_key, expiration=3600):
        """
        Generate presigned URL for secure temporary access to private S3 objects.
        
        Args:
            s3_key: S3 object key path
            expiration: URL validity in seconds (default: 3600 = 1 hour)
        
        Returns:
            str: Presigned URL with signature, or None if generation fails
        """
        if not self.is_configured():
            logger.warning("Cannot generate presigned URL: S3 not configured")
            return None
        
        if not s3_key:
            logger.warning("Cannot generate presigned URL: s3_key is empty")
            return None
        
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            
            logger.debug(f"Presigned URL generated for key: {s3_key}")
            return presigned_url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {s3_key}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {str(e)}")
            return None
    
    def delete_file_from_s3(self, s3_key):
        """
        Delete a file from S3 bucket to prevent storage bloat.
        
        Args:
            s3_key: S3 object key path
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_configured() or not s3_key:
            return False
            
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"Successfully deleted file from S3: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete {s3_key} from S3: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting from S3: {str(e)}")
            return False


def get_s3_service():
    """
    Factory function to get or create S3Service singleton instance.
    
    Returns:
        S3Service: Singleton instance
    """
    global _s3_service_instance
    
    if _s3_service_instance is None:
        _s3_service_instance = S3Service()
    
    return _s3_service_instance
