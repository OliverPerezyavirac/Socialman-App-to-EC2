#!/bin/bash

# SocialMan Video Publishing Service - EC2 Deployment Script
# This script automates the deployment of the video publishing service to EC2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
SERVICE_NAME="socialman-video-publisher"
SERVICE_PORT="5001"
DOCKER_IMAGE_NAME="socialman/video-publishing-service"
CONTAINER_NAME="socialman-video-publisher"
ENV_FILE=".env"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking system requirements..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if nginx is installed (for reverse proxy)
    if ! command -v nginx &> /dev/null; then
        log_warn "Nginx is not installed. Installing nginx..."
        sudo apt-get update
        sudo apt-get install -y nginx
    fi
    
    # Check if certbot is installed (for SSL)
    if ! command -v certbot &> /dev/null; then
        log_warn "Certbot is not installed. Installing certbot..."
        sudo apt-get install -y certbot python3-certbot-nginx
    fi
    
    log_info "Requirements check completed."
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        log_error ".env file not found. Please create one based on .env.example"
        exit 1
    fi
    
    # Create necessary directories
    sudo mkdir -p /opt/socialman
    sudo mkdir -p /var/log/socialman
    sudo mkdir -p /etc/nginx/sites-available
    sudo mkdir -p /etc/nginx/sites-enabled
    
    # Copy service files
    sudo cp -r . /opt/socialman/video-publishing-service/
    sudo chown -R $USER:$USER /opt/socialman/
    
    log_info "Environment setup completed."
}

build_and_deploy() {
    log_info "Building and deploying the service..."
    
    cd /opt/socialman/video-publishing-service/
    
    # Stop existing containers
    docker-compose down || true
    
    # Remove old images
    docker image prune -f || true
    
    # Build and start the service
    docker-compose up --build -d
    
    # Wait for service to be ready
    log_info "Waiting for service to be ready..."
    sleep 30
    
    # Health check
    if curl -f http://localhost:$SERVICE_PORT/health > /dev/null 2>&1; then
        log_info "Service is running and healthy!"
    else
        log_error "Service health check failed!"
        docker-compose logs
        exit 1
    fi
}

setup_nginx() {
    log_info "Setting up Nginx reverse proxy..."
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/socialman-video-publisher > /dev/null <<EOF
server {
    listen 80;
    server_name \$host;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://localhost:$SERVICE_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:$SERVICE_PORT/health;
        access_log off;
    }
}
EOF
    
    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/socialman-video-publisher /etc/nginx/sites-enabled/
    
    # Remove default site if exists
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    if sudo nginx -t; then
        log_info "Nginx configuration is valid."
        sudo systemctl reload nginx
    else
        log_error "Nginx configuration is invalid!"
        exit 1
    fi
}

setup_ssl() {
    read -p "Do you want to setup SSL certificate? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your domain name: " domain
        if [ ! -z "$domain" ]; then
            log_info "Setting up SSL certificate for $domain..."
            sudo certbot --nginx -d $domain --non-interactive --agree-tos --email admin@$domain
        fi
    fi
}

setup_monitoring() {
    log_info "Setting up service monitoring..."
    
    # Create systemd service for monitoring
    sudo tee /etc/systemd/system/socialman-video-publisher-monitor.service > /dev/null <<EOF
[Unit]
Description=SocialMan Video Publisher Monitor
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/opt/socialman/video-publishing-service/monitor.sh
User=$USER

[Install]
WantedBy=multi-user.target
EOF
    
    # Create monitoring script
    tee /opt/socialman/video-publishing-service/monitor.sh > /dev/null <<'EOF'
#!/bin/bash
cd /opt/socialman/video-publishing-service/
if ! curl -f http://localhost:5001/health > /dev/null 2>&1; then
    echo "Service is down, restarting..."
    docker-compose restart
fi
EOF
    
    chmod +x /opt/socialman/video-publishing-service/monitor.sh
    
    # Create systemd timer
    sudo tee /etc/systemd/system/socialman-video-publisher-monitor.timer > /dev/null <<EOF
[Unit]
Description=Run SocialMan Video Publisher Monitor every 5 minutes
Requires=socialman-video-publisher-monitor.service

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
EOF
    
    # Enable and start the timer
    sudo systemctl daemon-reload
    sudo systemctl enable socialman-video-publisher-monitor.timer
    sudo systemctl start socialman-video-publisher-monitor.timer
    
    log_info "Monitoring setup completed."
}

setup_log_rotation() {
    log_info "Setting up log rotation..."
    
    sudo tee /etc/logrotate.d/socialman-video-publisher > /dev/null <<EOF
/var/log/socialman/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 $USER $USER
    postrotate
        docker-compose -f /opt/socialman/video-publishing-service/docker-compose.yml restart > /dev/null 2>&1 || true
    endscript
}
EOF
    
    log_info "Log rotation setup completed."
}

main() {
    log_info "Starting SocialMan Video Publishing Service deployment..."
    
    check_requirements
    setup_environment
    build_and_deploy
    setup_nginx
    setup_ssl
    setup_monitoring
    setup_log_rotation
    
    log_info "Deployment completed successfully!"
    log_info "Service is available at: http://$(curl -s http://checkip.amazonaws.com):$SERVICE_PORT"
    log_info "Health check: http://$(curl -s http://checkip.amazonaws.com):$SERVICE_PORT/health"
    log_info ""
    log_info "Useful commands:"
    log_info "  View logs: docker-compose -f /opt/socialman/video-publishing-service/docker-compose.yml logs -f"
    log_info "  Restart service: docker-compose -f /opt/socialman/video-publishing-service/docker-compose.yml restart"
    log_info "  Stop service: docker-compose -f /opt/socialman/video-publishing-service/docker-compose.yml down"
}

main "$@"
