CREATE DATABASE IF NOT EXISTS socialman_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE socialman_db;

CREATE TABLE IF NOT EXISTS videos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(500) NOT NULL,
    title VARCHAR(255),
    description TEXT,
    tags TEXT,
    file_size BIGINT NOT NULL,
    duration INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_s3_key (s3_key)
);

CREATE TABLE IF NOT EXISTS video_publications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    video_id INT NOT NULL,
    platform ENUM('instagram', 'tiktok', 'x', 'facebook') NOT NULL,
    status ENUM('pending', 'processing', 'success', 'failed') NOT NULL DEFAULT 'pending',
    publication_data JSON,
    error_message TEXT,
    publication_id VARCHAR(255),
    publication_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
    INDEX idx_video_platform (video_id, platform),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    UNIQUE KEY unique_video_platform (video_id, platform)
);

CREATE TABLE IF NOT EXISTS publication_attempts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    video_publication_id INT NOT NULL,
    attempt_number INT NOT NULL DEFAULT 1,
    status ENUM('pending', 'processing', 'success', 'failed') NOT NULL,
    error_message TEXT,
    response_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_publication_id) REFERENCES video_publications(id) ON DELETE CASCADE,
    INDEX idx_video_publication (video_publication_id),
    INDEX idx_attempt_status (status)
);

CREATE TABLE IF NOT EXISTS platform_configurations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    platform ENUM('instagram', 'tiktok', 'x', 'facebook') NOT NULL UNIQUE,
    is_enabled BOOLEAN DEFAULT true,
    max_file_size_mb INT DEFAULT 100,
    max_duration_seconds INT DEFAULT 300,
    supported_formats JSON,
    api_rate_limit_per_hour INT DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO platform_configurations (platform, max_file_size_mb, max_duration_seconds, supported_formats, api_rate_limit_per_hour) VALUES
('instagram', 100, 60, '["mp4", "mov"]', 200),
('tiktok', 128, 180, '["mp4", "mov", "avi"]', 100),
('x', 512, 140, '["mp4", "mov"]', 300),
('facebook', 1024, 240, '["mp4", "mov", "avi"]', 200)
ON DUPLICATE KEY UPDATE
max_file_size_mb = VALUES(max_file_size_mb),
max_duration_seconds = VALUES(max_duration_seconds),
supported_formats = VALUES(supported_formats),
api_rate_limit_per_hour = VALUES(api_rate_limit_per_hour);

CREATE TABLE IF NOT EXISTS service_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    service_name VARCHAR(100) NOT NULL,
    log_level ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL,
    message TEXT NOT NULL,
    context_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_service_level (service_name, log_level),
    INDEX idx_created_at (created_at)
);

CREATE OR REPLACE VIEW publication_summary AS
SELECT 
    v.id as video_id,
    v.title,
    v.filename,
    COUNT(vp.id) as total_publications,
    SUM(CASE WHEN vp.status = 'success' THEN 1 ELSE 0 END) as successful_publications,
    SUM(CASE WHEN vp.status = 'failed' THEN 1 ELSE 0 END) as failed_publications,
    GROUP_CONCAT(CASE WHEN vp.status = 'success' THEN vp.platform END) as successful_platforms,
    v.created_at as video_created_at,
    MAX(vp.updated_at) as last_publication_attempt
FROM videos v
LEFT JOIN video_publications vp ON v.id = vp.video_id
GROUP BY v.id, v.title, v.filename, v.created_at;

CREATE OR REPLACE VIEW platform_statistics AS
SELECT 
    platform,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_attempts,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_attempts,
    ROUND(SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate,
    MIN(created_at) as first_publication,
    MAX(created_at) as last_publication
FROM video_publications
GROUP BY platform;
