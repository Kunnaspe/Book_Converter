from pathlib import Path
from decouple import config

# Set the base directory to the root of the Django project so all
# relative paths resolve correctly regardless of where the server runs
BASE_DIR = Path(__file__).resolve().parent.parent

# Pull the secret key from the environment so it never lives in version control
SECRET_KEY = config('SECRET_KEY')

# Default DEBUG to False so a missing .env on production stays safe
DEBUG = config('DEBUG', default=False, cast=bool)

# Allow the EC2 public IP along with localhost so both dev and prod requests
# are accepted without changing code
ALLOWED_HOSTS = [
    config('EC2_PUBLIC_IP', default='localhost'),
    'localhost',
    '127.0.0.1',
]

# Include storages so Django can talk to S3 and novels for the app itself
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'novels',
    'django.contrib.humanize',
]

# Keep the full default middleware stack so sessions, CSRF and security
# headers all work out of the box
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'paul_final_project.urls'

# Point the template loader at the apps directory so each app can carry
# its own templates folder
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'paul_final_project.wsgi.application'

# Use SQLite for simplicity since this project does not require a
# full relational database for its novel data
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Pull all four AWS credentials from environment variables so the
# bucket name and keys never end up in source code
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='paul-final-bucket')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')

# Set ACL to None because the bucket policy handles access instead of
# per-object ACLs, which avoids the AccessControlListNotSupported error
AWS_DEFAULT_ACL = None

# Disable file overwrite so a second upload with the same key does not
# silently replace the first one
AWS_S3_FILE_OVERWRITE = False

# Turn off query string auth so presigned URL logic is handled explicitly
# in code rather than automatically by django-storages
AWS_QUERYSTRING_AUTH = False

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Serve static files from the standard /static/ URL path
STATIC_URL = '/static/'

# Collect all static files into this directory when running collectstatic
# before deploying to production
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
