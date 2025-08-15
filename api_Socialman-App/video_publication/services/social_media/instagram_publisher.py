from .base_publisher import BaseSocialMediaPublisher
from config.config import Config
import requests
import time

class InstagramPublisher(BaseSocialMediaPublisher):
    def __init__(self):
        super().__init__("Instagram")
        self.access_token = Config.INSTAGRAM_ACCESS_TOKEN
        self.business_account_id = Config.INSTAGRAM_BUSINESS_ACCOUNT_ID
        self.api_base_url = "https://graph.facebook.com/v18.0"
    
    def validate_credentials(self):
        if not self.access_token or not self.business_account_id:
            raise ValueError("Instagram credentials not configured")
        
        try:
            url = f"{self.api_base_url}/{self.business_account_id}"
            params = {'access_token': self.access_token}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return True
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Instagram credential validation failed: {str(e)}")
    
    def get_platform_requirements(self):
        return {
            'max_file_size_mb': 100,
            'max_duration_seconds': 60,
            'supported_formats': ['mp4', 'mov'],
            'max_caption_length': 2200
        }
    
    def publish(self, video_data):
        try:
            self._log_publication_attempt(video_data)
            self.validate_credentials()
            
            requirements = self.get_platform_requirements()
            self._validate_video_format(video_data, requirements['supported_formats'])
            self._validate_video_size(video_data, requirements['max_file_size_mb'])
            self._validate_video_duration(video_data, requirements['max_duration_seconds'])
            
            media_container_id = self._create_media_container(video_data)
            
            result = self._publish_media_container(media_container_id)
            
            self._log_publication_success(video_data, result)
            
            return {
                'id': result['id'],
                'url': f"https://www.instagram.com/p/{result['id']}/",
                'platform': self.platform_name,
                'status': 'published'
            }
            
        except Exception as e:
            self._log_publication_error(video_data, str(e))
            raise
    
    def _create_media_container(self, video_data):
        try:
            url = f"{self.api_base_url}/{self.business_account_id}/media"
            
            caption = self._prepare_description(
                video_data, 
                self.get_platform_requirements()['max_caption_length']
            )
            
            data = {
                'video_url': video_data['video_url'],
                'media_type': 'REELS',
                'caption': caption,
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            return result['id']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create Instagram media container: {str(e)}")
    
    def _publish_media_container(self, container_id):
        try:
            max_attempts = 10
            attempt = 0
            
            while attempt < max_attempts:
                status_url = f"{self.api_base_url}/{container_id}"
                status_params = {'fields': 'status_code', 'access_token': self.access_token}
                
                status_response = requests.get(status_url, params=status_params)
                status_response.raise_for_status()
                
                status_data = status_response.json()
                status_code = status_data.get('status_code')
                
                if status_code == 'FINISHED':
                    break
                elif status_code == 'ERROR':
                    raise Exception("Instagram media processing failed")
                
                attempt += 1
                time.sleep(5)
            
            if attempt >= max_attempts:
                raise Exception("Instagram media processing timeout")
            
            publish_url = f"{self.api_base_url}/{self.business_account_id}/media_publish"
            publish_data = {
                'creation_id': container_id,
                'access_token': self.access_token
            }
            
            publish_response = requests.post(publish_url, data=publish_data)
            publish_response.raise_for_status()
            
            return publish_response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to publish Instagram media: {str(e)}")
