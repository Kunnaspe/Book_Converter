import boto3
from botocore.exceptions import ClientError
from django.conf import settings

# Keep the bucket name in one place so every function below picks it
# up from settings rather than hardcoding it
BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'paul-final-bucket')


def get_s3_client():
    """Create and return a boto3 S3 client using the credentials stored
    in Django settings so callers do not have to build the client themselves."""
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )


def list_s3_files(prefix='raw/'):
    """List all objects in the bucket under the given prefix and return
    a list of dicts with key, size_kb and last_modified for each file.
    Returns an empty list if anything goes wrong so callers can show a
    friendly empty state instead of crashing."""
    try:
        client = get_s3_client()
        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix)
        files = []
        for page in pages:
            for obj in page.get('Contents', []):
                key = obj['Key']
                # Skip the prefix directory entry itself since it is not a real file
                if key == prefix:
                    continue
                files.append({
                    'key': key,
                    'size_kb': round(obj['Size'] / 1024, 1),
                    'last_modified': obj['LastModified'],
                })
        return files
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f'S3 list_s3_files ClientError {error_code}: {e}')
        return []
    except Exception as e:
        print(f'S3 list_s3_files unexpected error: {e}')
        return []


def read_s3_text_file(s3_key):
    """Download a text file from S3 by key and return its contents as a
    Python string decoded as UTF-8. Returns None if the file does not exist
    or any other error occurs so callers can show a 404-style message."""
    try:
        client = get_s3_client()
        response = client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
        body = response['Body'].read()
        return body.decode('utf-8', errors='replace')
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f'S3 read_s3_text_file ClientError {error_code} for key {s3_key}: {e}')
        return None
    except Exception as e:
        print(f'S3 read_s3_text_file unexpected error for key {s3_key}: {e}')
        return None


def upload_binary_to_s3(binary_data, s3_key, content_type='audio/mpeg'):
    """Upload raw binary data to S3 at the given key with the specified
    content type. Returns True on success and False on failure so callers
    can decide what to do without catching exceptions themselves."""
    try:
        client = get_s3_client()
        client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=binary_data,
            ContentType=content_type,
        )
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f'S3 upload_binary_to_s3 ClientError {error_code} for key {s3_key}: {e}')
        return False
    except Exception as e:
        print(f'S3 upload_binary_to_s3 unexpected error for key {s3_key}: {e}')
        return False


def generate_presigned_url(s3_key, expiration=3600):
    """Generate a presigned GET URL for the given S3 key so the browser
    can play or download the file directly without exposing credentials.
    Returns None if the URL cannot be generated."""
    try:
        client = get_s3_client()
        url = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=expiration,
        )
        return url
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f'S3 generate_presigned_url ClientError {error_code} for key {s3_key}: {e}')
        return None
    except Exception as e:
        print(f'S3 generate_presigned_url unexpected error for key {s3_key}: {e}')
        return None
