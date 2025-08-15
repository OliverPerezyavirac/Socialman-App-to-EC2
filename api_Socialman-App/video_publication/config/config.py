import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    
    RDS_HOST = os.environ.get('RDS_HOST')
    RDS_DATABASE = os.environ.get('RDS_DATABASE')
    RDS_USERNAME = os.environ.get('RDS_USERNAME')
    RDS_PASSWORD = os.environ.get('RDS_PASSWORD')
    RDS_PORT = int(os.environ.get('RDS_PORT', 5432))
    
    INSTAGRAM_ACCESS_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
    INSTAGRAM_BUSINESS_ACCOUNT_ID = os.environ.get('INSTAGRAM_BUSINESS_ACCOUNT_ID')
    
    TIKTOK_CLIENT_KEY = os.environ.get('TIKTOK_CLIENT_KEY')
    TIKTOK_CLIENT_SECRET = os.environ.get('TIKTOK_CLIENT_SECRET')
    TIKTOK_ACCESS_TOKEN = os.environ.get('TIKTOK_ACCESS_TOKEN')
    
    X_API_KEY = os.environ.get('X_API_KEY')
    X_API_SECRET = os.environ.get('X_API_SECRET')
    X_ACCESS_TOKEN = os.environ.get('X_ACCESS_TOKEN')
    X_ACCESS_TOKEN_SECRET = os.environ.get('X_ACCESS_TOKEN_SECRET')
    
    FACEBOOK_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN')
    FACEBOOK_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID')
    
    MAX_VIDEO_SIZE_MB = int(os.environ.get('MAX_VIDEO_SIZE_MB', 100))
    ALLOWED_VIDEO_FORMATS = os.environ.get('ALLOWED_VIDEO_FORMATS', 'mp4,mov,avi').split(',')
    
    @classmethod
    def validate_config(cls):
        required_vars = ['S3_BUCKET_NAME', 'RDS_HOST', 'RDS_DATABASE', 'RDS_USERNAME', 'RDS_PASSWORD']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
