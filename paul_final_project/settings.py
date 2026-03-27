from pathlib import Path
from decouple import config

# sets the base directory to the root of the Django project so all relative paths resolve correctly regardless of where the server runs
BASE_DIR = Path(__file__).resolve().parent.parent

# pulls the secret key from the env so it doesn't lives in the version control
SECRET_KEY = config('SECRET_KEY')

# defaults DEBUG to False so my missing .env on production stays safe
DEBUG = config('DEBUG', default=False, cast=bool)

# allows the EC2 public ip along with localhost so both dev and prod requests are accepted without changing the code
ALLOWED_HOSTS = [
    config('EC2_PUBLIC_IP', default='localhost'),
    'localhost',
    '127.0.0.1',
]

# includes storages so django can talk to S3 and novels for the app
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

# keeps the full default middleware stack so sessions, CSRF and security headers all work 
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

# points the template loader at the apps directory so each app carries its own template folder
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

# use sqlite for simplicity since my project does not require a full relational  database for its novel data
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# pull all four AWS credentials from env so thebucket name and keys never end up in source code
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='paul-final-bucket')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')

# sets ACL to None because the bucket policy handles access instead of the ACLs, which avoid the access control list error
AWS_DEFAULT_ACL = None

# disables file overwrite so a second upload with the same key does not replace the first one
AWS_S3_FILE_OVERWRITE = False

# turns off query string auth so presigned URL logic is handled explicitlyin code rather than automatically by django-storages
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

# served static files from the standard /static/ URL path
STATIC_URL = '/static/'

# collect all static files into this directory when running collectstatic before deploying to prod
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
