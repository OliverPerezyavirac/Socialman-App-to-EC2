import os
import psycopg2
import requests
import tempfile
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import boto3

load_dotenv()

app = Flask(__name__)

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT')
}

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def create_publications_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS publications (
            publication_id SERIAL PRIMARY KEY,
            video_id INT,
            platform VARCHAR(50) NOT NULL,
            platform_post_id VARCHAR(255),
            status VARCHAR(50) DEFAULT 'pending',
            published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error_message TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

create_publications_table()

def download_video_from_s3(s3_key):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        s3_client.download_fileobj(S3_BUCKET_NAME, s3_key, temp_file)
        return temp_file.name

def publish_to_instagram(video_path, caption):
    try:
        access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        business_account_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        
        with open(video_path, 'rb') as video_file:
            create_url = f"https://graph.facebook.com/v18.0/{business_account_id}/media"
            create_data = {
                'caption': caption,
                'media_type': 'VIDEO',
                'access_token': access_token
            }
            create_files = {'video': video_file}
            
            create_response = requests.post(create_url, data=create_data, files=create_files)
            create_result = create_response.json()
            
            if 'id' not in create_result:
                return False, f"Error creating media: {create_result}"
            
            media_id = create_result['id']
            
            publish_url = f"https://graph.facebook.com/v18.0/{business_account_id}/media_publish"
            publish_data = {
                'creation_id': media_id,
                'access_token': access_token
            }
            
            publish_response = requests.post(publish_url, data=publish_data)
            publish_result = publish_response.json()
            
            if 'id' in publish_result:
                return True, publish_result['id']
            else:
                return False, f"Error publishing: {publish_result}"
                
    except Exception as e:
        return False, str(e)

def publish_to_facebook(video_path, caption):
    try:
        access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        page_id = os.getenv('FACEBOOK_PAGE_ID')
        
        with open(video_path, 'rb') as video_file:
            url = f"https://graph.facebook.com/v18.0/{page_id}/videos"
            data = {
                'description': caption,
                'access_token': access_token
            }
            files = {'file': video_file}
            
            response = requests.post(url, data=data, files=files)
            result = response.json()
            
            if 'id' in result:
                return True, result['id']
            else:
                return False, f"Error: {result}"
                
    except Exception as e:
        return False, str(e)

def publish_to_tiktok(video_path, caption):
    try:
        access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
        
        with open(video_path, 'rb') as video_file:
            url = "https://open-api.tiktok.com/share/video/upload/"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            data = {
                'post_info': {
                    'title': caption,
                    'privacy_level': 'SELF_ONLY',
                    'disable_duet': False,
                    'disable_comment': False,
                    'disable_stitch': False,
                    'video_cover_timestamp_ms': 1000
                },
                'source_info': {
                    'source': 'FILE_UPLOAD',
                    'video_size': os.path.getsize(video_path),
                    'chunk_size': 10000000,
                    'total_chunk_count': 1
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if result.get('data', {}).get('share_id'):
                return True, result['data']['share_id']
            else:
                return False, f"Error: {result}"
                
    except Exception as e:
        return False, str(e)

def publish_to_twitter(video_path, caption):
    try:
        import tweepy
        
        api_key = os.getenv('X_API_KEY')
        api_secret = os.getenv('X_API_SECRET')
        access_token = os.getenv('X_ACCESS_TOKEN')
        access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET')
        
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
        api = tweepy.API(auth)
        
        media = api.media_upload(video_path)
        tweet = client.create_tweet(text=caption, media_ids=[media.media_id])
        
        return True, str(tweet.data['id'])
        
    except Exception as e:
        return False, str(e)

@app.route('/videos/available', methods=['GET'])
def get_available_videos():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT v.video_id, v.title, v.s3_key, v.upload_date, 
                   ARRAY_AGG(t.tag_name) as tags
            FROM videos v 
            LEFT JOIN video_tags vt ON v.video_id = vt.video_id 
            LEFT JOIN tags t ON vt.tag_id = t.tag_id 
            WHERE v.is_published = FALSE 
            GROUP BY v.video_id, v.title, v.s3_key, v.upload_date 
            ORDER BY v.upload_date DESC;
        """)
        
        videos_data = cur.fetchall()
        cur.close()
        conn.close()
        
        videos_list = []
        for video in videos_data:
            videos_list.append({
                'video_id': video[0],
                'title': video[1],
                's3_key': video[2],
                's3_url': f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{video[2]}",
                'upload_date': video[3].isoformat(),
                'tags': video[4] if video[4] and video[4] != [None] else []
            })
        
        return jsonify(videos_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/publish', methods=['POST'])
def publish_video():
    data = request.get_json()
    video_id = data.get('video_id')
    platforms = data.get('platforms', [])
    caption = data.get('caption', '')
    
    if not video_id or not platforms:
        return jsonify({'error': 'video_id and platforms are required'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT title, s3_key FROM videos WHERE video_id = %s", (video_id,))
        video_data = cur.fetchone()
        
        if not video_data:
            return jsonify({'error': 'Video not found'}), 404
        
        title, s3_key = video_data
        video_path = download_video_from_s3(s3_key)
        
        results = {}
        
        for platform in platforms:
            platform = platform.lower()
            
            if platform == 'instagram':
                success, post_id = publish_to_instagram(video_path, caption or title)
            elif platform == 'facebook':
                success, post_id = publish_to_facebook(video_path, caption or title)
            elif platform == 'tiktok':
                success, post_id = publish_to_tiktok(video_path, caption or title)
            elif platform == 'twitter' or platform == 'x':
                success, post_id = publish_to_twitter(video_path, caption or title)
            else:
                results[platform] = {'success': False, 'error': 'Unsupported platform'}
                continue
            
            status = 'published' if success else 'failed'
            error_message = None if success else post_id
            platform_post_id = post_id if success else None
            
            cur.execute("""
                INSERT INTO publications (video_id, platform, platform_post_id, status, error_message)
                VALUES (%s, %s, %s, %s, %s)
            """, (video_id, platform, platform_post_id, status, error_message))
            
            results[platform] = {
                'success': success,
                'post_id': platform_post_id if success else None,
                'error': error_message if not success else None
            }
        
        if any(result['success'] for result in results.values()):
            cur.execute("UPDATE videos SET is_published = TRUE WHERE video_id = %s", (video_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        os.unlink(video_path)
        
        return jsonify({
            'message': 'Publication process completed',
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/publications/history', methods=['GET'])
def get_publications_history():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT p.publication_id, p.video_id, v.title, p.platform, 
                   p.platform_post_id, p.status, p.published_date, p.error_message
            FROM publications p
            JOIN videos v ON p.video_id = v.video_id
            ORDER BY p.published_date DESC;
        """)
        
        publications_data = cur.fetchall()
        cur.close()
        conn.close()
        
        publications_list = []
        for pub in publications_data:
            publications_list.append({
                'publication_id': pub[0],
                'video_id': pub[1],
                'video_title': pub[2],
                'platform': pub[3],
                'platform_post_id': pub[4],
                'status': pub[5],
                'published_date': pub[6].isoformat(),
                'error_message': pub[7]
            })
        
        return jsonify(publications_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
