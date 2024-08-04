"""
Django settings for NOC project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
MAIN_DIR = os.path.dirname(os.path.dirname(__file__))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-gwms2q)u^e+)26_6(_x!1w&y+)kx(v184_$#mz39a+a0^q8otx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOWED_ORIGINS = ['https://noc.mitsgwalior.in','http://noc.mitsgwalior.in']
CSRF_TRUSTED_ORIGINS = ['https://*.mitsgwalior.in']
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'nocrest.apps.NocrestConfig',
    'corsheaders',
    'blog',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'social_django',
    'allauth.socialaccount.providers.google',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',      # CorsMiddleware should be after CSRF middleware
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF middleware should be before CorsMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'NOC.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'nocrest/','Static/'),os.path.join(BASE_DIR,'nocrest/','Templates/'),],
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

print(os.path.join(BASE_DIR,'Static/'),os.path.join(BASE_DIR,'Templates/'))

AUTHENTICATION_BACKENDS = [
    # 'django.contrib.auth.backends.ModelBackend',
    # 'allauth.account.auth_backends.AuthenticationBackend',

'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]
WSGI_APPLICATION = 'NOC.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': { 'ENGINE': 'django.db.backends.mysql', 'NAME': 'nocdata', 'USER': 'root', 'PASSWORD': '1234', 'HOST': 'localhost', 'PORT': '3306', }
# }
DATABASES = {
    'default': { 'ENGINE': 'django.db.backends.mysql', 'NAME': 'nocdata', 'USER': 'root', 'PASSWORD': '1234', 'HOST': 'localhost', 'PORT': '3306', }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/Static/'
STATICFILES_DIRS = (os.path.join(MAIN_DIR,'nocrest/','Static/'),)

print(os.path.join(MAIN_DIR,'nocrest/','Static/'))

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ORIGIN_ALLOW_ALL = True


EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'sdc@mitsgwalior.in'
# EMAIL_HOST_PASSWORD = 'wznfsucdzrutcfvb'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'suyashu1606.agarwal@gmail.com'
EMAIL_HOST_PASSWORD = 'qogm rmdf yjeq npxh'
EMAIL_USE_TLS = True


# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '1009503756046-5gbljupodd8ipp5pq9kfc0f7bo102ujd.apps.googleusercontent.com'
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'


SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '1074957629956-s8j5emjrlb30d1cqhhv6ioajbubmqscm.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['profile', 'email']

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'home'  # Redirect to this URL after successful login
LOGOUT_REDIRECT_URL = 'api/frontpage'  # Redirect to this URL after logout


STATIC_URL = '/Static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR,'nocrest/', 'Static/')]

MEDIA_URL = '/pdfs/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'pdfs')  # Set the path where media files will be stored

import logging

LOGGING = {
    'version': 1,
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
