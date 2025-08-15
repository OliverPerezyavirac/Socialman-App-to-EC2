from .base_publisher import BaseSocialMediaPublisher
from config.config import Config
import requests
import requests_oauthlib
import json

class XPublisher(BaseSocialMediaPublisher):
    def __init__(self):
        super().__init__("X")
        self.api_key = Config.X_API_KEY
        self.api_secret = Config.X_API_SECRET
        self.access_token = Config.X_ACCESS_TOKEN
        self.access_token_secret = Config.X_ACCESS_TOKEN_SECRET
        self.api_base_url = "https://api.twitter.com/2"
        self.upload_api_url = "https://upload.twitter.com/1.1"
    
    def validate_credentials(self):
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise ValueError("X (Twitter) credentials not configured")
        
        try:
            auth = requests_oauthlib.OAuth1(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_token_secret
            )
            
            url = f"{self.api_base_url}/users/me"
            response = requests.get(url, auth=auth)
            response.raise_for_status()
            
            return True
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"X credential validation failed: {str(e)}")
    
    def get_platform_requirements(self):
        return {
            'max_file_size_mb': 512,
            'max_duration_seconds': 140,
            'supported_formats': ['mp4', 'mov'],
            'max_caption_length': 280
        }
    
    def publish(self, video_data):
        try:
            self._log_publication_attempt(video_data)
            self.validate_credentials()
            
            requirements = self.get_platform_requirements()
            self._validate_video_format(video_data, requirements['supported_formats'])
            self._validate_video_size(video_data, requirements['max_file_size_mb'])
            self._validate_video_duration(video_data, requirements['max_duration_seconds'])
            
            media_id = self._upload_video(video_data)
            
            result = self._create_tweet(video_data, media_id)
            
            self._log_publication_success(video_data, result)
            
            return {
                'id': result['data']['id'],
                'url': f"https://x.com/user/status/{result['data']['id']}",
                'platform': self.platform_name,
                'status': 'published'
            }
            
        except Exception as e:
            self._log_publication_error(video_data, str(e))
            raise
    
    def _upload_video(self, video_data):
        try:
            auth = requests_oauthlib.OAuth1(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_token_secret
            )
            
            video_response = requests.get(video_data['video_url'])
            video_response.raise_for_status()
            video_bytes = video_response.content
            
            init_url = f"{self.upload_api_url}/media/upload.json"
            init_data = {
                'command': 'INIT',
                'media_type': 'video/mp4',
                'total_bytes': len(video_bytes),
                'media_category': 'tweet_video'
            }
            
            init_response = requests.post(init_url, data=init_data, auth=auth)
            init_response.raise_for_status()
            media_id = init_response.json()['media_id']
            
            chunk_size = 1024 * 1024
            segment_id = 0
            
            for i in range(0, len(video_bytes), chunk_size):
                chunk = video_bytes[i:i + chunk_size]
                
                append_url = f"{self.upload_api_url}/media/upload.json"
                append_data = {
                    'command': 'APPEND',
                    'media_id': media_id,
                    'segment_index': segment_id
                }
                append_files = {'media': chunk}
                
                append_response = requests.post(append_url, data=append_data, files=append_files, auth=auth)
                append_response.raise_for_status()
                
                segment_id += 1
            
            finalize_url = f"{self.upload_api_url}/media/upload.json"
            finalize_data = {
                'command': 'FINALIZE',
                'media_id': media_id
            }
            
            finalize_response = requests.post(finalize_url, data=finalize_data, auth=auth)
            finalize_response.raise_for_status()
            
            return media_id
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to upload video to X: {str(e)}")
    
    def _create_tweet(self, video_data, media_id):
        try:
            auth = requests_oauthlib.OAuth1(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_token_secret
            )
            
            text = self._prepare_description(
                video_data, 
                self.get_platform_requirements()['max_caption_length']
            )
            
            url = f"{self.api_base_url}/tweets"
            data = {
                'text': text,
                'media': {
                    'media_ids': [str(media_id)]
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, headers=headers, data=json.dumps(data), auth=auth)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create tweet: {str(e)}")
