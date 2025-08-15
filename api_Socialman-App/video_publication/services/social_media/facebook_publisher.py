from .base_publisher import BaseSocialMediaPublisher
from config.config import Config
import requests

class FacebookPublisher(BaseSocialMediaPublisher):
    def __init__(self):
        super().__init__("Facebook")
        self.access_token = Config.FACEBOOK_ACCESS_TOKEN
        self.page_id = Config.FACEBOOK_PAGE_ID
        self.api_base_url = "https://graph.facebook.com/v18.0"
    
    def validate_credentials(self):
        if not self.access_token or not self.page_id:
            raise ValueError("Facebook credentials not configured")
        
        try:
            url = f"{self.api_base_url}/{self.page_id}"
            params = {'access_token': self.access_token}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return True
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Facebook credential validation failed: {str(e)}")
    
    def get_platform_requirements(self):
        return {
            'max_file_size_mb': 1024,
            'max_duration_seconds': 240,
            'supported_formats': ['mp4', 'mov', 'avi'],
            'max_caption_length': 63206
        }
    
    def publish(self, video_data):
        try:
            self._log_publication_attempt(video_data)
            self.validate_credentials()
            
            requirements = self.get_platform_requirements()
            self._validate_video_format(video_data, requirements['supported_formats'])
            self._validate_video_size(video_data, requirements['max_file_size_mb'])
            self._validate_video_duration(video_data, requirements['max_duration_seconds'])
            
            result = self._upload_and_publish_video(video_data)
            
            self._log_publication_success(video_data, result)
            
            return {
                'id': result['id'],
                'url': f"https://www.facebook.com/{result['id']}",
                'platform': self.platform_name,
                'status': 'published'
            }
            
        except Exception as e:
            self._log_publication_error(video_data, str(e))
            raise
    
    def _upload_and_publish_video(self, video_data):
        try:
            url = f"{self.api_base_url}/{self.page_id}/videos"
            
            description = self._prepare_description(
                video_data, 
                self.get_platform_requirements()['max_caption_length']
            )
            
            video_response = requests.get(video_data['video_url'])
            video_response.raise_for_status()
            
            data = {
                'description': description,
                'access_token': self.access_token,
                'published': 'true'
            }
            
            files = {
                'source': ('video.mp4', video_response.content, 'video/mp4')
            }
            
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to upload and publish video to Facebook: {str(e)}")
