from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseSocialMediaPublisher(ABC):
    def __init__(self, platform_name):
        self.platform_name = platform_name
        self.logger = logger
    
    @abstractmethod
    def publish(self, video_data):
        pass
    
    @abstractmethod
    def validate_credentials(self):
        pass
    
    @abstractmethod
    def get_platform_requirements(self):
        pass
    
    def _validate_video_format(self, video_data, supported_formats):
        filename = video_data.get('filename', '').lower()
        file_extension = filename.split('.')[-1] if '.' in filename else ''
        
        if file_extension not in supported_formats:
            raise ValueError(f"Unsupported video format for {self.platform_name}. Supported formats: {supported_formats}")
    
    def _validate_video_size(self, video_data, max_size_mb):
        file_size_mb = video_data.get('file_size', 0) / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            raise ValueError(f"Video size ({file_size_mb:.2f}MB) exceeds {self.platform_name} limit ({max_size_mb}MB)")
    
    def _validate_video_duration(self, video_data, max_duration_seconds):
        duration = video_data.get('duration', 0)
        
        if duration > max_duration_seconds:
            raise ValueError(f"Video duration ({duration}s) exceeds {self.platform_name} limit ({max_duration_seconds}s)")
    
    def _prepare_description(self, video_data, max_length=None):
        title = video_data.get('title', '')
        description = video_data.get('description', '')
        tags = video_data.get('tags', [])
        
        content = f"{title}\n\n{description}"
        
        if tags:
            hashtags = ' '.join([f"#{tag.strip().replace(' ', '')}" for tag in tags if tag.strip()])
            content = f"{content}\n\n{hashtags}"
        
        if max_length and len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        return content.strip()
    
    def _log_publication_attempt(self, video_data):
        self.logger.info(f"Attempting to publish video '{video_data.get('title')}' to {self.platform_name}")
    
    def _log_publication_success(self, video_data, result):
        self.logger.info(f"Successfully published video '{video_data.get('title')}' to {self.platform_name}: {result}")
    
    def _log_publication_error(self, video_data, error):
        self.logger.error(f"Failed to publish video '{video_data.get('title')}' to {self.platform_name}: {error}")
