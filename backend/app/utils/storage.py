import boto3
import os
from botocore.exceptions import NoCredentialsError

class StorageClient:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=os.getenv('S3_ENDPOINT_URL'),
            aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY'),
            region_name=os.getenv('S3_REGION_NAME', 'auto')
        )
        self.bucket = os.getenv('S3_BUCKET_NAME', 'notuma-assets')

    def upload_file(self, file_path, object_name=None):
        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            self.s3.upload_file(file_path, self.bucket, object_name)
            return f"{os.getenv('S3_PUBLIC_URL', '')}/{object_name}"
        except NoCredentialsError:
            print("Credentials not available")
            return None

    def get_signed_url(self, object_name, expiration=3600):
        try:
            response = self.s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': self.bucket,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
            return response
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None

storage_client = StorageClient()
