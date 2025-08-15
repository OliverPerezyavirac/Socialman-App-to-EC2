from flask import Flask, request, jsonify
from flask_cors import CORS
from config.config import Config
from services.video_service import VideoService
from utils.exceptions import ValidationError, SocialMediaError
from models.responses import ApiResponse
from messages.error_messages import ERROR_MESSAGES
from messages.success_messages import SUCCESS_MESSAGES
import os
import logging

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

video_service = VideoService()

@app.route('/health', methods=['GET'])
def health_check():
    return ApiResponse.success(SUCCESS_MESSAGES['HEALTH_CHECK']).to_dict()

@app.route('/publish', methods=['POST'])
def publish_video():
    try:
        data = request.get_json()
        
        if not data:
            return ApiResponse.error(ERROR_MESSAGES['INVALID_JSON'], 400).to_dict()
        
        video_id = data.get('video_id')
        platforms = data.get('platforms', [])
        
        if not video_id:
            return ApiResponse.error(ERROR_MESSAGES['MISSING_VIDEO_ID'], 400).to_dict()
        
        if not platforms or not isinstance(platforms, list):
            return ApiResponse.error(ERROR_MESSAGES['MISSING_PLATFORMS'], 400).to_dict()
        
        result = video_service.publish_video(video_id, platforms)
        
        return ApiResponse.success(
            SUCCESS_MESSAGES['VIDEO_PUBLISHED_SUCCESS'], 
            result
        ).to_dict()
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return ApiResponse.error(str(e), 400).to_dict()
    
    except SocialMediaError as e:
        logger.error(f"Social media error: {str(e)}")
        return ApiResponse.error(str(e), 500).to_dict()
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return ApiResponse.error(ERROR_MESSAGES['INTERNAL_SERVER_ERROR'], 500).to_dict()

@app.route('/platforms', methods=['GET'])
def get_available_platforms():
    try:
        platforms = video_service.get_available_platforms()
        return ApiResponse.success(
            SUCCESS_MESSAGES['PLATFORMS_RETRIEVED'], 
            {'platforms': platforms}
        ).to_dict()
    
    except Exception as e:
        logger.error(f"Error retrieving platforms: {str(e)}")
        return ApiResponse.error(ERROR_MESSAGES['INTERNAL_SERVER_ERROR'], 500).to_dict()

@app.route('/status/<video_id>', methods=['GET'])
def get_publication_status(video_id):
    try:
        status = video_service.get_publication_status(video_id)
        return ApiResponse.success(
            SUCCESS_MESSAGES['STATUS_RETRIEVED'], 
            status
        ).to_dict()
    
    except Exception as e:
        logger.error(f"Error retrieving status: {str(e)}")
        return ApiResponse.error(ERROR_MESSAGES['INTERNAL_SERVER_ERROR'], 500).to_dict()

@app.route('/videos', methods=['GET'])
def list_videos():
    try:
        videos = video_service.list_videos()
        return ApiResponse.success(
            "Videos retrieved successfully",
            {"videos": videos}
        ).to_dict()
    except Exception as e:
        logger.error(f"Error retrieving videos: {str(e)}")
        return ApiResponse.error("Internal server error", 500).to_dict()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
