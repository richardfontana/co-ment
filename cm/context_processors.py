from django.conf import settings
from cm.models import user_has_perm_on_text, Text
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

if not settings.YUI_DISTANT:
    YAHOO_BASE_URL = "/site_media/lib/yui"
else:
    YAHOO_BASE_URL = settings.YUI_DISTANT_URL + settings.YUI_VERSION
     
if settings.YUI_DEBUG and not settings.YUI_DISTANT:
    YAHOO_EXTENSION = ""
else:
    YAHOO_EXTENSION = "-min"

if settings.EXT_DEBUG:
    EXT_EXTENSION = "-debug"
else:
    EXT_EXTENSION = ""

def yui(request):
    """
    add the yui path according to settings
    YUI_DEBUG = True
    YUI_DISTANT = False
    YUI_DISTANT_URL = "http://yui.yahooapis.com"
    places YAHOO_BASE_URL and YAHOO_EXTENSION in template    
    """    
    return {'YAHOO_BASE_URL' : YAHOO_BASE_URL, 'YAHOO_EXTENSION' : YAHOO_EXTENSION, 'EXT_EXTENSION' : EXT_EXTENSION}

def client_debug(request):
    """
    add the client_debug in template    
    """    
    return {'CLIENT_DEBUG' : settings.CLIENT_DEBUG}

SESSION_MESSAGE_KEY = 'message'

def session_message(request):
    """
    makes request.session[SESSION_MESSAGE_KEY] available in template display if present
    removes it from session
    """
    if SESSION_MESSAGE_KEY in request.session:
        message = request.session[SESSION_MESSAGE_KEY]
        del request.session[SESSION_MESSAGE_KEY]
        return {SESSION_MESSAGE_KEY : message }
    return {}

from django.utils.translation.trans_real import translation
def do_translate(message, translation_function, lang_code):
    """
    Translates 'message' using the given 'translation_function' name -- which
    will be either gettext or ugettext. It uses the current thread to find the
    translation object to use. If no current translation is activated, the
    message will be run through the default translation object.
    """
    t = _active.get(currentThread(), None)
    if t is not None:
        result = getattr(t, translation_function)(message)
    else:
        if _default is None:
            from django.conf import settings
            _default = translation(lang_code)
        result = getattr(_default, translation_function)(message)
    if isinstance(message, SafeData):
        return mark_safe(result)
    return result

LOCAL_LANGUAGES = []
for code, value in settings.LANGUAGES:
    t = translation(code)
    trans_value = getattr(t, 'gettext')(value)
    LOCAL_LANGUAGES.append((code, trans_value))

def utils(request):
    """
    all utils objects:
    - 'intelligent' language object
    - OpenID
    """
    return {
            'LOCAL_LANGUAGES' : LOCAL_LANGUAGES,
            'OPENID' : settings.OPENID,
            }

 
def isRegistrationAllowed(request):
    return {'CUST_ALLOWREGISTRATION' : settings.CUST_ALLOWREGISTRATION}

