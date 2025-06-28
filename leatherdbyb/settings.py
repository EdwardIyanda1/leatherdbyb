import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = 'leatherdbyb.urls'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'core/static')]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',  # <-- This is the one causing your error
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'core',  # <-- Your app
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'core', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'core.context_processors.cart_context',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  
    'django.contrib.messages.middleware.MessageMiddleware',  
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'edwardiyanda60@gmail.com'
EMAIL_HOST_PASSWORD = 'kiss ujap vivn tezu'  # your app password
DEFAULT_FROM_EMAIL = 'LeatherdbyB <noreply@leatherdbyb.com>'

# settings.py
PAYSTACK_SECRET_KEY = 'pk_test_d82a6709cfd5fec170010103dd47c5b493cbc01a'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Static files settings
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'core/static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Authentication
LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Messages framework
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

DEBUG = True
ALLOWED_HOSTS = ['*']


SECRET_KEY = 'r(3g4)f$502+nojhb=xed_*yk^4-^7ktruoil)^2p^$+wa9vx8'
# Session settings
SESSION_COOKIE_AGE = 86400  # 1 day in seconds
SESSION_SAVE_EVERY_REQUEST = True

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'