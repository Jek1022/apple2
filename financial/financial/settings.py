"""
Django settings for financial project.

Generated by 'django-admin startproject' using Django 1.9.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

# Endless pagination
# from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
# TEMPLATE_CONTEXT_PROCESSORS += (
#     'django.core.context_processors.request',
# )

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1onuv+i2p=cfye9rfo=j%1e^tz$lktp0^3opwll_q2q5%hk!-_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'vat',
    'wtax',
    'mainunit',
    'unit',
    'typeofexpense',
    'currency',
    'industry',
    'bankaccounttype',
    'bankaccount',
    'mainproduct',
    'product',
    'ataxcode',
    'inputvat',
    'inputvattype',
    'kindofexpense',
    'mistype',
    'bank',
    'adtype',
    'bankbranch',
    'branch',
    'mainmodule',
    'module',
    'chartofaccount',
    'cvtype',
    'aptype',
    'ofsubtype',
    'oftype',
    'ortype',
    'paytype',
    'potype',
    'serviceclassification',
    'productgroup',
    'unitofmeasure',
    'suppliertype',
    'customertype',
    'creditterm',
    'customer',
    'artype',
    'advertisingcategory',
    'fxtype',
    'companyproduct',
    'circulationproduct',
    'circulationcategory',
    'maingroupproduct',
    'mrstype',
    'mainsupplier',
    'collector',
    'maininventory',
    'serviceinformation',
    'outputvat',
    'supplier',
    'mainsupplier_supplier',
    'company',
    'productbudget',
    'companyparameter',
    'department',
    'departmentbudget',
    'journalvoucher',
    'jvtype',
    'employee',
    'rep_chartofaccount',
    'rep_department',
    'rep_supplier',
    'rep_customer',
    'debitcreditmemosubtype',
    'acctentry',
    'purchaseorder',
    'acknowledgementreceipt',
    'requisitionform',
    'purchaserequisitionform',
    'inventoryitemtype',
    'inventoryitemclass',
    'inventoryitem',
    'canvasssheet',
    'rfprfapproval',
    'annoying',
    'debitcreditmemo',
    'agenttype',
    'agent',
    'mathfilters',
    'accountspayable',
    'bankbranchdisburse',
    'utils',
    'operationalfund',
    'endless_pagination',
    'checkvoucher',
    'replenish_pcv',
    'cvsubtype',
    'replenish_rfv',
    'cashdisbursement',
    'apsubtype',
    'jvsubtype',
    'outputvattype',
    'orsubtype',
    'creditcard',
    'officialreceipt',
    'user_employee',
    'processing_or',
    'arsubtype',
    'processing_data',
    'dcartype',
    'cmsadjustment',
    'processing_transaction',
    'locationcategory',
    'productgroupcategory',
    'circulationpaytype',
    'filemanagement',
    'dcclasstype',
    'processing_jv',
    'budgetapproverlevels',
    'generaljournalbook',
    'rep_generalledger',
    'reportdashboard',
    'rep_bir',
    'rep_master',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'financial.urls'

TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'financial.context_processors.usermodule',
            ],
        },
    },
]

WSGI_APPLICATION = 'financial.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases 

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.mysql',
        #'NAME': 'db_financial',
        'NAME': 'db_test',
        # 'HOST': 'localhost',
        'HOST': '128.1.44.22',
        'PORT': '3306',
        'USER': 'root',
        'PASSWORD': 'RootToor1!@#',
        #'PASSWORD': 'mysqld3vserver',
        'OPTIONS': {
            'init_command': 'SET default_storage_engine=INNODB',
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [STATIC_DIR]
STATIC_URL = '/static/'

# STATIC_ROOT = "/kenmolina/financial/static"
# WKHTMLTOPDF_CMD = "C:/Python27/Lib/site-packages/wkhtmltopdf"

MEDIA_DIR = os.path.join(BASE_DIR, 'media')
MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = '/media/'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'

ENDLESS_PAGINATION_PER_PAGE = 15

