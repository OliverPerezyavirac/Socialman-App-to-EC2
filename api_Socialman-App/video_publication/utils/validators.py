from utils.exceptions import ValidationError
from messages.error_messages import ERROR_MESSAGES
from config.config import Config
import os

class VideoValidator:
    def __init__(self):
        self.max_file_size = Config.MAX_VIDEO_SIZE_MB * 1024 * 1024
        self.allowed_formats = Config.ALLOWED_VIDEO_FORMATS
    
    def validate_video_for_publishing(self, video_data):
        if not video_data:
            raise ValidationError(ERROR_MESSAGES['VIDEO_NOT_FOUND'])
        
        self._validate_required_fields(video_data)
        self._validate_file_exists(video_data)
        self._validate_file_format(video_data)
        self._validate_file_size(video_data)
        
        return True
    
    def _validate_required_fields(self, video_data):
        required_fields = ['id', 'filename', 's3_key', 'video_url']
        
        for field in required_fields:
            if not video_data.get(field):
                raise ValidationError(f"Missing required field: {field}")
    
    def _validate_file_exists(self, video_data):
        video_url = video_data.get('video_url')
        if not video_url:
            raise ValidationError(ERROR_MESSAGES['VIDEO_URL_INVALID'])
    
    def _validate_file_format(self, video_data):
        filename = video_data.get('filename', '').lower()
        
        if not filename:
            raise ValidationError(ERROR_MESSAGES['INVALID_FILE_FORMAT'])
        
        file_extension = filename.split('.')[-1] if '.' in filename else ''
        
        if file_extension not in self.allowed_formats:
            raise ValidationError(
                f"Unsupported video format. Allowed formats: {', '.join(self.allowed_formats)}"
            )
    
    def _validate_file_size(self, video_data):
        file_size = video_data.get('file_size', 0)
        
        if file_size <= 0:
            raise ValidationError(ERROR_MESSAGES['INVALID_FILE_SIZE'])
        
        if file_size > self.max_file_size:
            max_size_mb = self.max_file_size / (1024 * 1024)
            current_size_mb = file_size / (1024 * 1024)
            raise ValidationError(
                f"File size ({current_size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb}MB)"
            )

class PlatformValidator:
    SUPPORTED_PLATFORMS = ['instagram', 'tiktok', 'x', 'facebook']
    
    @classmethod
    def validate_platforms(cls, platforms):
        if not platforms:
            raise ValidationError(ERROR_MESSAGES['MISSING_PLATFORMS'])
        
        if not isinstance(platforms, list):
            raise ValidationError(ERROR_MESSAGES['PLATFORMS_MUST_BE_LIST'])
        
        unsupported_platforms = [p for p in platforms if p not in cls.SUPPORTED_PLATFORMS]
        
        if unsupported_platforms:
            raise ValidationError(
                f"Unsupported platforms: {', '.join(unsupported_platforms)}. "
                f"Supported platforms: {', '.join(cls.SUPPORTED_PLATFORMS)}"
            )
        
        return True

class RequestValidator:
    @staticmethod
    def validate_publish_request(data):
        if not isinstance(data, dict):
            raise ValidationError(ERROR_MESSAGES['INVALID_REQUEST_FORMAT'])
        
        video_id = data.get('video_id')
        if not video_id:
            raise ValidationError(ERROR_MESSAGES['MISSING_VIDEO_ID'])
        
        if not isinstance(video_id, (str, int)):
            raise ValidationError(ERROR_MESSAGES['INVALID_VIDEO_ID_TYPE'])
        
        platforms = data.get('platforms', [])
        PlatformValidator.validate_platforms(platforms)
        
        return True
