import os
os.environ['DEVELOPMENT'] = '1'
os.environ.setdefault('SECRET_KEY', 'test-only-key')
from .settings import *
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
STRIPE_SECRET_KEY = 'sk_test_mock'
STRIPE_WH_SECRET = 'whsec_test_mock'
STRIPE_PUBLIC_KEY = 'pk_test_mock'
