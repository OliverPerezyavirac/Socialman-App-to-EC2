from datetime import datetime
from messages.general_messages import GENERAL_MESSAGES

class ApiResponse:
    def __init__(self, success=True, message=None, data=None, error=None, status_code=200):
        self.success = success
        self.message = message
        self.data = data
        self.error = error
        self.status_code = status_code
        self.timestamp = datetime.utcnow().isoformat()
        self.service = GENERAL_MESSAGES['SERVICE_NAME']
        self.version = GENERAL_MESSAGES['SERVICE_VERSION']
    
    @classmethod
    def success(cls, message, data=None, status_code=200):
        return cls(
            success=True,
            message=message,
            data=data,
            status_code=status_code
        )
    
    @classmethod
    def error(cls, message, status_code=500, error_details=None):
        return cls(
            success=False,
            message=message,
            error=error_details,
            status_code=status_code
        )
    
    @classmethod
    def warning(cls, message, data=None, status_code=200):
        return cls(
            success=True,
            message=message,
            data=data,
            status_code=status_code
        )
    
    def to_dict(self):
        response = {
            'success': self.success,
            'message': self.message,
            'timestamp': self.timestamp,
            'service': self.service,
            'version': self.version
        }
        
        if self.data is not None:
            response['data'] = self.data
        
        if self.error is not None:
            response['error'] = self.error
        
        return response, self.status_code

class PublicationResponse:
    def __init__(self, video_id, results):
        self.video_id = video_id
        self.results = results
        self.timestamp = datetime.utcnow().isoformat()
        
        self.successful_publications = results.get('successful_publications', [])
        self.failed_publications = results.get('failed_publications', [])
        self.total_platforms = results.get('total_platforms', 0)
        self.successful_count = results.get('successful_count', 0)
        self.failed_count = results.get('failed_count', 0)
    
    @property
    def success_rate(self):
        if self.total_platforms == 0:
            return 0
        return (self.successful_count / self.total_platforms) * 100
    
    @property
    def overall_status(self):
        if self.successful_count == self.total_platforms:
            return GENERAL_MESSAGES['STATUS_SUCCESS']
        elif self.successful_count > 0:
            return GENERAL_MESSAGES['STATUS_PARTIAL']
        else:
            return GENERAL_MESSAGES['STATUS_FAILED']
    
    def to_dict(self):
        return {
            'video_id': self.video_id,
            'overall_status': self.overall_status,
            'success_rate': round(self.success_rate, 2),
            'total_platforms': self.total_platforms,
            'successful_count': self.successful_count,
            'failed_count': self.failed_count,
            'successful_publications': self.successful_publications,
            'failed_publications': self.failed_publications,
            'timestamp': self.timestamp
        }

class PlatformStatus:
    def __init__(self, platform, status, message=None, publication_id=None, url=None, error=None):
        self.platform = platform
        self.status = status
        self.message = message
        self.publication_id = publication_id
        self.url = url
        self.error = error
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self):
        result = {
            'platform': self.platform,
            'status': self.status,
            'timestamp': self.timestamp
        }
        
        if self.message:
            result['message'] = self.message
        if self.publication_id:
            result['publication_id'] = self.publication_id
        if self.url:
            result['url'] = self.url
        if self.error:
            result['error'] = self.error
            
        return result

class HealthCheckResponse:
    def __init__(self):
        self.service = GENERAL_MESSAGES['SERVICE_NAME']
        self.version = GENERAL_MESSAGES['SERVICE_VERSION']
        self.status = GENERAL_MESSAGES['API_RESPONSE_OK']
        self.timestamp = datetime.utcnow().isoformat()
        self.uptime = self._get_uptime()
        self.components = self._check_components()
    
    def _get_uptime(self):
        return "Available"
    
    def _check_components(self):
        return {
            'database': 'healthy',
            'aws_s3': 'healthy',
            'social_platforms': 'configured'
        }
    
    def to_dict(self):
        return {
            'service': self.service,
            'version': self.version,
            'status': self.status,
            'timestamp': self.timestamp,
            'uptime': self.uptime,
            'components': self.components
        }
