#####################
# DATABASE SETTINGS
#####################

#/**** your_settings *****/
DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#/**** your_settings *****/
DATABASE_NAME = 'cm'             # Or path to database file if using sqlite3. 
#/**** your_settings *****/
DATABASE_USER = 'user'             # Not used with sqlite3.
#/**** your_settings *****/
DATABASE_PASSWORD = 'pw'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.


##########################
# CONFIGURATION SETTINGS
##########################
#/**** your_settings *****/
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris' # ********** change to your timezone here *********

#/**** your_settings *****/
# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us' # ********** change to your timezone here *********

#/**** your_settings *****/
# Make this unique, and don't share it with anybody. (used to initial the random algorithm)
SECRET_KEY = 'FKDS21dJF2sqKDMdsFffdIFDFFMQ'

#/**** your_settings *****/
# url of development server 
SITE_URL = "http://127.0.0.1:8000"

#/**** your_settings *****/
DEFAULT_FROM_EMAIL = "******** YOUR EMAIL HERE ********"

#/**** your_settings *****/
EMAIL_HOST = "localhost"

#/**** your_settings *****/
# webserver writable directory to store images 
MEDIA_ROOT = '/var/lib/mysite/mydata'

#/**** your_settings *****/
# emails to warn in case of a software failure (used when DEBUG == False)  
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)


#####################
# DEBUG SETTINGS
#####################

DEBUG = True
TEMPLATE_DEBUG = DEBUG
CLIENT_DEBUG = DEBUG
EXT_DEBUG = DEBUG
YUI_DEBUG = DEBUG # use expanded js yui version (i.e. not -min)
YUI_DISTANT = not YUI_DEBUG
TEMPLATE_STRING_IF_INVALID = "NNNNNNNNNOOOOOOOOOOOOOOO"
SEND_BROKEN_LINK_EMAILS = False# used when DEBUG == False

