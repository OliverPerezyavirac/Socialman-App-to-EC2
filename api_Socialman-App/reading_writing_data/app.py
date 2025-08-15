import os
import psycopg2
import boto3
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

# Carga las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# --- Configuración de la base de datos ---
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT')
}

def get_db_connection():
    """Establece y devuelve una conexión a la base de datos."""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

# --- Configuración de AWS S3 ---
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# --- Funciones para la base de datos ---
def create_tables():
    """Crea las tablas de la base de datos si no existen."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            video_id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            s3_key VARCHAR(255) NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_published BOOLEAN DEFAULT FALSE
        );
        CREATE TABLE IF NOT EXISTS tags (
            tag_id SERIAL PRIMARY KEY,
            tag_name VARCHAR(255) UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS video_tags (
            video_id INT REFERENCES videos(video_id) ON DELETE CASCADE,
            tag_id INT REFERENCES tags(tag_id) ON DELETE CASCADE,
            PRIMARY KEY (video_id, tag_id)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Llama a la función para crear las tablas al iniciar la aplicación
create_tables()

# --- Rutas de la API ---
@app.route('/upload', methods=['POST'])
def upload_video():
    
    if 'video' not in request.files:
        return jsonify({'error': 'No video file part'}), 400

    video_file = request.files['video']
    title = request.form.get('title')
    tags = request.form.get('tags', '').split(',')

    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        
        s3_key = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{video_file.filename}"
        
        
        s3_client.upload_fileobj(video_file, S3_BUCKET_NAME, s3_key)

        
        conn = get_db_connection()
        cur = conn.cursor()

        
        cur.execute(
            "INSERT INTO videos (title, s3_key) VALUES (%s, %s) RETURNING video_id;",
            (title, s3_key)
        )
        video_id = cur.fetchone()[0]

        
        for tag_name in tags:
            tag_name = tag_name.strip()
            if tag_name:
                cur.execute(
                    "INSERT INTO tags (tag_name) VALUES (%s) ON CONFLICT (tag_name) DO NOTHING RETURNING tag_id;",
                    (tag_name,)
                )
                tag_id = cur.fetchone()
                if tag_id:
                    tag_id = tag_id[0]
                else:
                    cur.execute("SELECT tag_id FROM tags WHERE tag_name = %s;", (tag_name,))
                    tag_id = cur.fetchone()[0]

                cur.execute(
                    "INSERT INTO video_tags (video_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                    (video_id, tag_id)
                )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            'message': 'Video uploaded and metadata saved successfully',
            'video_id': video_id,
            's3_key': s3_key
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/videos', methods=['GET'])
def list_videos():
    """Ruta para listar, buscar y ordenar videos."""
    order_by = request.args.get('order_by', 'upload_date')
    search_query = request.args.get('search', '')

    allowed_orders = ['upload_date', 'title']
    if order_by not in allowed_orders:
        order_by = 'upload_date'

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = f"SELECT v.video_id, v.title, v.s3_key, v.upload_date, ARRAY_AGG(t.tag_name) FROM videos v LEFT JOIN video_tags vt ON v.video_id = vt.video_id LEFT JOIN tags t ON vt.tag_id = t.tag_id WHERE v.title ILIKE %s GROUP BY v.video_id ORDER BY {order_by} DESC;"

        cur.execute(query, (f"%{search_query}%",))
        videos_data = cur.fetchall()
        cur.close()
        conn.close()

        videos_list = []
        for video in videos_data:
            videos_list.append({
                'video_id': video[0],
                'title': video[1],
                's3_url': f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{video[2]}",
                'upload_date': video[3].isoformat(),
                'tags': video[4] if video[4] and video[4] != [None] else []
            })

        return jsonify(videos_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)