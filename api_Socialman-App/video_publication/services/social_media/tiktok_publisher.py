from .base_publisher import BaseSocialMediaPublisher
from config.config import Config
import requests
import json

class TikTokPublisher(BaseSocialMediaPublisher):
    def __init__(self):
        super().__init__("TikTok")
        self.client_key = Config.TIKTOK_CLIENT_KEY
        self.client_secret = Config.TIKTOK_CLIENT_SECRET
        self.access_token = Config.TIKTOK_ACCESS_TOKEN
        self.api_base_url = "https://open.tiktokapis.com/v2"
    
    def validate_credentials(self):
        if not self.client_key or not self.client_secret or not self.access_token:
            raise ValueError("TikTok credentials not configured")
        
        try:
            url = f"{self.api_base_url}/user/info/"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return True
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"TikTok credential validation failed: {str(e)}")
    
    def get_platform_requirements(self):
        return {
            'max_file_size_mb': 128,
            'max_duration_seconds': 180,
            'supported_formats': ['mp4', 'mov', 'avi'],
            'max_caption_length': 150
        }
    
    def publish(self, video_data):
        try:
            self._log_publication_attempt(video_data)
            self.validate_credentials()
            
            requirements = self.get_platform_requirements()
            self._validate_video_format(video_data, requirements['supported_formats'])
            self._validate_video_size(video_data, requirements['max_file_size_mb'])
            self._validate_video_duration(video_data, requirements['max_duration_seconds'])
            
            upload_url = self._initialize_video_upload()
            
            self._upload_video(upload_url, video_data)
            
            result = self._publish_video(upload_url, video_data)
            
            self._log_publication_success(video_data, result)
            
            return {
                'id': result.get('publish_id'),
                'url': result.get('share_url', ''),
                'platform': self.platform_name,
                'status': 'published'
            }
            
        except Exception as e:
            self._log_publication_error(video_data, str(e))
            raise
    
    def _initialize_video_upload(self):
        try:
            url = f"{self.api_base_url}/post/publish/video/init/"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'post_info': {
                    'privacy_level': 'PUBLIC_TO_EVERYONE',
                    'disable_duet': False,
                    'disable_comment': False,
                    'disable_stitch': False,
                    'video_cover_timestamp_ms': 1000
                },
                'source_info': {
                    'source': 'PULL_FROM_URL',
                    'video_size': 50 * 1024 * 1024,
                    'chunk_size': 10 * 1024 * 1024,
                    'total_chunk_count': 5
                }
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            
            result = response.json()
            return result['data']['upload_url']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to initialize TikTok video upload: {str(e)}")
    
    def _upload_video(self, upload_url, video_data):
        try:
            video_response = requests.get(video_data['video_url'])
            video_response.raise_for_status()
            
            headers = {
                'Content-Type': 'video/mp4',
                'Content-Length': str(len(video_response.content))
            }
            
            upload_response = requests.put(upload_url, headers=headers, data=video_response.content)
            upload_response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to upload video to TikTok: {str(e)}")
    
    def _publish_video(self, upload_url, video_data):
        try:
            url = f"{self.api_base_url}/post/publish/video/commit/"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            caption = self._prepare_description(
                video_data, 
                self.get_platform_requirements()['max_caption_length']
            )
            
            data = {
                'post_info': {
                    'title': caption,
                    'privacy_level': 'PUBLIC_TO_EVERYONE',
                    'disable_duet': False,
                    'disable_comment': False,
                    'disable_stitch': False,
                    'video_cover_timestamp_ms': 1000
                }
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            
            return response.json()['data']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to publish video to TikTok: {str(e)}")
