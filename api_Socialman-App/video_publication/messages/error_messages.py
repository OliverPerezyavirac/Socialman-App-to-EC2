ERROR_MESSAGES = {
    'INTERNAL_SERVER_ERROR': 'Internal server error occurred',
    'INVALID_JSON': 'Invalid JSON format in request body',
    'MISSING_VIDEO_ID': 'Video ID is required',
    'MISSING_PLATFORMS': 'At least one platform is required',
    'INVALID_VIDEO_ID_TYPE': 'Video ID must be a string or number',
    'PLATFORMS_MUST_BE_LIST': 'Platforms must be provided as a list',
    'VIDEO_NOT_FOUND': 'Video not found with the provided ID',
    'VIDEO_URL_INVALID': 'Video URL is invalid or not accessible',
    'INVALID_FILE_FORMAT': 'Invalid video file format',
    'INVALID_FILE_SIZE': 'Invalid or missing video file size',
    'PLATFORM_NOT_SUPPORTED': 'Platform not supported',
    'INVALID_REQUEST_FORMAT': 'Invalid request format',
    
    'INSTAGRAM_CREDENTIALS_MISSING': 'Instagram credentials not configured',
    'INSTAGRAM_UPLOAD_FAILED': 'Failed to upload video to Instagram',
    'INSTAGRAM_PUBLISH_FAILED': 'Failed to publish video to Instagram',
    'INSTAGRAM_MEDIA_PROCESSING_FAILED': 'Instagram media processing failed',
    'INSTAGRAM_MEDIA_TIMEOUT': 'Instagram media processing timeout',
    
    'TIKTOK_CREDENTIALS_MISSING': 'TikTok credentials not configured',
    'TIKTOK_UPLOAD_FAILED': 'Failed to upload video to TikTok',
    'TIKTOK_PUBLISH_FAILED': 'Failed to publish video to TikTok',
    'TIKTOK_INIT_FAILED': 'Failed to initialize TikTok video upload',
    
    'X_CREDENTIALS_MISSING': 'X (Twitter) credentials not configured',
    'X_UPLOAD_FAILED': 'Failed to upload video to X',
    'X_PUBLISH_FAILED': 'Failed to publish video to X',
    'X_MEDIA_PROCESSING_FAILED': 'X media processing failed',
    
    'FACEBOOK_CREDENTIALS_MISSING': 'Facebook credentials not configured',
    'FACEBOOK_UPLOAD_FAILED': 'Failed to upload video to Facebook',
    'FACEBOOK_PUBLISH_FAILED': 'Failed to publish video to Facebook',
    
    'AWS_CONNECTION_FAILED': 'Failed to connect to AWS services',
    'S3_OBJECT_NOT_FOUND': 'Video file not found in S3 bucket',
    'S3_ACCESS_DENIED': 'Access denied to S3 bucket or object',
    'RDS_CONNECTION_FAILED': 'Failed to connect to RDS database',
    'DATABASE_QUERY_FAILED': 'Database query execution failed',
    
    'FILE_SIZE_EXCEEDED': 'Video file size exceeds platform limits',
    'FILE_FORMAT_UNSUPPORTED': 'Video file format not supported by platform',
    'VIDEO_DURATION_EXCEEDED': 'Video duration exceeds platform limits',
    'CAPTION_LENGTH_EXCEEDED': 'Caption length exceeds platform limits',
    
    'CONFIGURATION_MISSING': 'Required configuration parameters missing',
    'ENVIRONMENT_VARIABLES_MISSING': 'Required environment variables not set',
    'CREDENTIALS_VALIDATION_FAILED': 'Platform credentials validation failed',
    'API_RATE_LIMIT_EXCEEDED': 'API rate limit exceeded for platform',
    'NETWORK_CONNECTION_ERROR': 'Network connection error occurred',
    'TIMEOUT_ERROR': 'Request timeout occurred',
    
    'PUBLICATION_ALREADY_EXISTS': 'Video already published to this platform',
    'PUBLICATION_NOT_FOUND': 'Publication record not found',
    'PUBLICATION_STATUS_UPDATE_FAILED': 'Failed to update publication status'
}
