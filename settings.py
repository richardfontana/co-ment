# Django settings for **co-ment** instance 

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "cm.context_processors.yui",
    "cm.context_processors.client_debug",
    "cm.context_processors.session_message",
    "cm.context_processors.isRegistrationAllowed",    
    "cm.context_processors.utils",    
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',    
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django_openidconsumer.middleware.OpenIDMiddleware',       
#    "django.middleware.transaction.TransactionMiddleware",
#    "django.middleware.cache.CacheMiddleware",
)

ROOT_URLCONF = 'urls' 

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
#    'django_openidconsumer',
#    'django_openidauth',    
    'cm', 
    'tagging', 
)

_ = lambda s: s

LANGUAGES = (
    ('fr', _('French')),
    ('en', _('English')),
)

AUTH_PROFILE_MODULE = "cm.profile"

# cache using local mem default timeout is 1 hour 
CACHE_BACKEND = 'locmem:///?timeout=3600&max_entries=400'

SITE_NAME = "co-ment"

#tagging
FORCE_LOWERCASE_TAGS = True

# security warning : disable this only for testing
CHECK_PERMISSIONS = True

# newsletter
HAS_NEWSLETTER = False
NEWSLETTER_ADR = '******** NOT USED ********'


DEFAULT_WORKFLOW_ID = 4

BLOG_DISPLAY = False
BLOG_FEED = "******** NOT USED ********"

CUST_ALLOWREGISTRATION = True

OPENID = False

try:
    from settings_local import *
except ImportError:
    pass

SERVER_EMAIL = DEFAULT_FROM_EMAIL
CONTACT_DEST = DEFAULT_FROM_EMAIL
MANAGERS = ADMINS
