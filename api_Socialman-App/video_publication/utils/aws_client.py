import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from config.config import Config
import pymysql
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class AWSClient:
    def __init__(self):
        try:
            self.s3_client = boto3.client('s3', region_name=Config.AWS_REGION)
            self.bucket_name = Config.S3_BUCKET_NAME
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
    
    def generate_presigned_url(self, s3_key, expiration=3600):
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL for {s3_key}: {str(e)}")
            raise
    
    def check_object_exists(self, s3_key):
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
    
    def get_object_metadata(self, s3_key):
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return {
                'size': response.get('ContentLength', 0),
                'last_modified': response.get('LastModified'),
                'content_type': response.get('ContentType')
            }
        except ClientError as e:
            logger.error(f"Error getting object metadata for {s3_key}: {str(e)}")
            raise

class DatabaseClient:
    def __init__(self):
        self.config = {
            'host': Config.RDS_HOST,
            'user': Config.RDS_USERNAME,
            'password': Config.RDS_PASSWORD,
            'database': Config.RDS_DATABASE,
            'port': Config.RDS_PORT,
            'charset': 'utf8mb4',
            'autocommit': True
        }
    
    @contextmanager
    def get_connection(self):
        connection = None
        try:
            connection = pymysql.connect(**self.config)
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query, params=None, fetch=True):
        with self.get_connection() as connection:
            try:
                with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(query, params)
                    
                    if fetch:
                        if query.strip().upper().startswith('SELECT'):
                            return cursor.fetchall()
                        else:
                            return cursor.fetchone()
                    else:
                        connection.commit()
                        return cursor.rowcount
                        
            except Exception as e:
                logger.error(f"Query execution error: {str(e)}")
                raise
    
    def execute_many(self, query, params_list):
        with self.get_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.executemany(query, params_list)
                    connection.commit()
                    return cursor.rowcount
                    
            except Exception as e:
                logger.error(f"Batch query execution error: {str(e)}")
                raise
    
    def test_connection(self):
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
