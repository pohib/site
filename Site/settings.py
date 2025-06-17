from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _
import dj_database_url

LANGUAGES = [
    ('ru', _('Russian')),
]

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-mc^q-u5kr)d)!04@r#f%!mxgnkfrzth-+gs6iyfc=v%krevz%('

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'analytics',
    'vacancies',
    'django_ckeditor_5',
    'adminsortable',
    'django_recaptcha',
    'django.contrib.sites',
    'users.apps.UsersConfig',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
]

AUTHENTICATION_BACKENDS = [
    'users.backends.TelegramBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'users:profile'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'  
ACCOUNT_LOGIN_REDIRECT_URL = 'users:profile'
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True 
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https' if not DEBUG else 'http'

TELEGRAM_BOT_NAME = 'oauthdjango_bot'
TELEGRAM_BOT_TOKEN = '7567724087:AAFeX8JZeT23DJsayatWhLcYZNdGpQleGN0'
TELEGRAM_LOGIN_REDIRECT_URL = '/profile/'
TELEGRAM_LOGIN_REDIRECT_URL_FAIL = '/login/'
TELEGRAM_LOGIN_SESSION_EXPIRATION = 86400

RECAPTCHA_PUBLIC_KEY = '6LfBTF8rAAAAAMP4Gd56VKGGI4wJxXyC8R6GYJ2p'
RECAPTCHA_PRIVATE_KEY = '6LfBTF8rAAAAANXxW53dCI4z3otqihAl_kT7iJIM'

CKEDITOR_5_CONFIGS = {
    'default': {
        'fontColor': '#000000',
        'fontSize': {
            'options': [
                'default',
                '10px', '12px', '14px', '16px', '18px', '20px', '24px', '28px', '32px'
            ],
        },
        'fontFamily': {
            'options': [
                'default',
                'Arial, sans-serif',
                'Courier New, Courier, monospace',
                'Georgia, serif',
                'Times New Roman, Times, serif',
                'Verdana, Geneva, sans-serif'
            ],
        },
        'uiColor': '#ffffff',
        'fontBackgroundColor': '#ffffff',
        'toolbar': [
            'heading',
            '|',
            'bold',
            'italic',
            'underline',
            'strikethrough',
            '|',
            'fontSize',
            'fontFamily',
            'fontColor',
            'fontBackgroundColor',
            '|',
            'alignment',
            '|',
            'bulletedList',
            'numberedList',
            '|',
            'link',
            'blockQuote',
            'imageUpload',
            '|',
            'undo',
            'redo'
        ],
        'language': 'ru',
        'contentsCss': [ 
            'https://cdn.ckeditor.com/ckeditor5/36.0.1/classic/contents.css',
            '/static/css/ckeditor5-custom.css'
        ],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                    'imageStyle:alignRight', 'imageStyle:alignCenter', 
                    'imageStyle:side', '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        }
    }
}

CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'csp.middleware.CSPMiddleware',
]

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "https://telegram.org",
    "https://*.telegram.org",
)
CSP_IMG_SRC = ("'self'", "data:", "https://*.telegram.org")
CSP_CONNECT_SRC = ("'self'", "https://telegram.org")
CSP_FRAME_SRC = ("'self'", "https://telegram.org")
CSP_FRAME_ANCESTORS = ("'self'", "https://*.telegram.org")


ROOT_URLCONF = 'Site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'core.context_processors.dynamic_pages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Site.wsgi.application'


DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres:postgres@localhost:5432/site',
        conn_max_age=600
    )
}



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


CKEDITOR_5_CUSTOM_CSS = 'css/ckeditor5/admin_dark_mode_fix.css'

STATIC_URL = '/static/'
if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

USE_L10N = False
DECIMAL_SEPARATOR = '.'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache'),
        'TIMEOUT': 86400,
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'vedenyov10@gmail.com'
EMAIL_HOST_PASSWORD = 'wsiw piwu szpa vbnx'
DEFAULT_FROM_EMAIL = 'vedenyov10@gmail.com'

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_SUBJECT_PREFIX = "127.0.0.1"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"


ACCOUNT_EMAIL_CONFIRMATION_TEMPLATE = "users/account/email/email_confirmation_message.html"
ACCOUNT_EMAIL_CONFIRMATION_SUBJECT = "users/account/email/email_confirmation_subject.txt"

SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"
