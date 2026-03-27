import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from novels.s3_utils import upload_binary_to_s3

# caps the text length because polly's API accepts at most3k characters of input 
MAX_TEXT_LENGTH = 3000


def text_to_mp3_polly(text, s3_output_key, voice_id='Joanna', engine='neural'):
    """send up to max length characters of text to polly,
    receive the MP3 stream, and uploads it to S3 at s3_output_key.
    Returns a tuple of (success, s3_output_key) where success is a bool
    so the view can decide what template to render without exceptions"""
    try:
        # truncate rather than raise an error so the user still gets partial audio instead of a broken page
        truncated_text = text[:MAX_TEXT_LENGTH]

        polly_client = boto3.client(
            'polly',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        response = polly_client.synthesize_speech(
            Text=truncated_text,
            OutputFormat='mp3',
            VoiceId=voice_id,
            Engine=engine,
        )

        # read the entire audio stream into memory before uploading because the streaming body is not seekable
        audio_data = response['AudioStream'].read()

        success = upload_binary_to_s3(
            binary_data=audio_data,
            s3_key=s3_output_key,
            content_type='audio/mpeg',
        )

        if success:
            return True, s3_output_key
        else:
            return False, None

    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f'Polly text_to_mp3_polly ClientError {error_code}: {e}')
        return False, None
    except Exception as e:
        print(f'Polly text_to_mp3_polly unexpected error: {e}')
        return False, None


def check_polly_task_status(task_id):
    """checks the status of an asynchronous olly speech synthesis task
    by task ID and return a dict with status and output_uri keys.
    The synchronous API is used in this project so this function is provided
    for completeness"""
    try:
        polly_client = boto3.client(
            'polly',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        response = polly_client.get_speech_synthesis_task(TaskId=task_id)
        task = response.get('SynthesisTask', {})
        return {
            'status': task.get('TaskStatus', 'unknown'),
            'output_uri': task.get('OutputUri'),
            'task_id': task_id,
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f'Polly check_polly_task_status ClientError {error_code} for task {task_id}: {e}')
        return {'status': 'error', 'output_uri': None, 'task_id': task_id}
    except Exception as e:
        print(f'Polly check_polly_task_status unexpected error for task {task_id}: {e}')
        return {'status': 'error', 'output_uri': None, 'task_id': task_id}
