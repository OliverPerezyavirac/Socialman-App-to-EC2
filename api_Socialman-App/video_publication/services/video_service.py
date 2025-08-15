from utils.aws_client import AWSClient, DatabaseClient
from services.social_media.instagram_publisher import InstagramPublisher
from services.social_media.tiktok_publisher import TikTokPublisher
from services.social_media.x_publisher import XPublisher
from services.social_media.facebook_publisher import FacebookPublisher
from utils.validators import VideoValidator
from utils.exceptions import ValidationError, SocialMediaError
from messages.error_messages import ERROR_MESSAGES
from messages.success_messages import SUCCESS_MESSAGES
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self):
        self.aws_client = AWSClient()
        self.db_client = DatabaseClient()
        self.validator = VideoValidator()
        
        self.publishers = {
            'instagram': InstagramPublisher(),
            'tiktok': TikTokPublisher(),
            'x': XPublisher(),
            'facebook': FacebookPublisher()
        }
    
    def publish_video(self, video_id, platforms):
        try:
            video_data = self._get_video_data(video_id)
            
            if not video_data:
                raise ValidationError(ERROR_MESSAGES['VIDEO_NOT_FOUND'])
            
            self.validator.validate_video_for_publishing(video_data)
            
            results = {}
            successful_publications = []
            failed_publications = []
            
            for platform in platforms:
                if platform not in self.publishers:
                    failed_publications.append({
                        'platform': platform,
                        'error': ERROR_MESSAGES['PLATFORM_NOT_SUPPORTED']
                    })
                    continue
                
                try:
                    publisher = self.publishers[platform]
                    publication_result = publisher.publish(video_data)
                    
                    self._save_publication_record(video_id, platform, publication_result, 'success')
                    
                    successful_publications.append({
                        'platform': platform,
                        'status': 'success',
                        'publication_id': publication_result.get('id'),
                        'url': publication_result.get('url')
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to publish to {platform}: {str(e)}")
                    self._save_publication_record(video_id, platform, {'error': str(e)}, 'failed')
                    
                    failed_publications.append({
                        'platform': platform,
                        'error': str(e)
                    })
            
            results = {
                'video_id': video_id,
                'successful_publications': successful_publications,
                'failed_publications': failed_publications,
                'total_platforms': len(platforms),
                'successful_count': len(successful_publications),
                'failed_count': len(failed_publications)
            }
            
            return results
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error publishing video {video_id}: {str(e)}")
            raise SocialMediaError(f"Publication failed: {str(e)}")
    
    def get_available_platforms(self):
        return list(self.publishers.keys())
    
    def get_publication_status(self, video_id):
        try:
            query = """
            SELECT platform, status, publication_data, created_at 
            FROM video_publications 
            WHERE video_id = %s
            ORDER BY created_at DESC
            """
            
            results = self.db_client.execute_query(query, (video_id,))
            
            publications = []
            for result in results:
                publication_data = json.loads(result['publication_data']) if result['publication_data'] else {}
                
                publications.append({
                    'platform': result['platform'],
                    'status': result['status'],
                    'publication_data': publication_data,
                    'published_at': result['created_at'].isoformat() if result['created_at'] else None
                })
            
            return {
                'video_id': video_id,
                'publications': publications
            }
            
        except Exception as e:
            logger.error(f"Error retrieving publication status for video {video_id}: {str(e)}")
            raise
    
    def _get_video_data(self, video_id):
        try:
            query = """
            SELECT id, filename, s3_key, title, description, tags, file_size, duration, created_at
            FROM videos 
            WHERE id = %s
            """
            
            results = self.db_client.execute_query(query, (video_id,))
            
            if not results:
                return None
            
            video = results[0]
            video_url = self.aws_client.generate_presigned_url(video['s3_key'])
            
            return {
                'video_id': video['id'],
                's3_key': video['s3_key'],
                'message': 'Video uploaded and metadata saved successfully'
            }
            
        except Exception as e:
            logger.error(f"Error retrieving video data for ID {video_id}: {str(e)}")
            raise
    
    def _save_publication_record(self, video_id, platform, publication_data, status):
        try:
            query = """
            INSERT INTO video_publications (video_id, platform, status, publication_data, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            """
            
            self.db_client.execute_query(
                query, 
                (video_id, platform, status, json.dumps(publication_data)),
                fetch=False
            )
            
        except Exception as e:
            logger.error(f"Error saving publication record: {str(e)}")
            raise
    
    def list_videos(self):
        try:
            query = """
            SELECT id, filename, title, description, tags, file_size, duration, created_at
            FROM videos
            ORDER BY created_at DESC
            """
            results = self.db_client.execute_query(query)
            videos = []
            for video in results:
                videos.append({
                    'video_id': video['id'],
                    's3_key': video.get('s3_key'),
                    'message': 'Video uploaded and metadata saved successfully'
                })
            return videos
        except Exception as e:
            logger.error(f"Error listing videos: {str(e)}")
            raise
        
