from cm.models import Text,TextVersion,Image
from cm.models import user_has_perm_on_text,number_has_perm_on_text,get_perm_by_name_or_perm
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.http import urlquote

login_url = settings.LOGIN_URL


def local_text_permission_required(perm, must_be_logged_in = False, redirect_field_name=REDIRECT_FIELD_NAME):    
    """
    decorator protection checking for perm for logged in user
    force logged in (i.e. redirect to connection screen if not if must_be_logged_in 
    """    
    def _dec(view_func):
        def _check_local_perm(request, *args, **kwargs):
            if not settings.CHECK_PERMISSIONS:
                # permission check disabled
                return view_func(request, *args, **kwargs)

            if must_be_logged_in and not request.user.is_authenticated():
                return HttpResponseRedirect('%s?%s=%s' % (login_url, redirect_field_name, urlquote(request.get_full_path())))
            #text = Text.objects.get(pk=kwargs['text_id'])
            if 'text_id' in kwargs: 
                text_id = kwargs['text_id']
            elif 'version_id' in kwargs:
                version_id = kwargs['version_id']
                version = get_object_or_404(TextVersion, pk = version_id)
                text_id = version.text.id
            elif 'image_id' in kwargs:
                image_id = kwargs['image_id']
                image = get_object_or_404(Image, pk = image_id)
                text_id = image.text_version.text.id
            else:
                raise Exception('no security check possible')
            permission = get_perm_by_name_or_perm(perm)                
            if user_has_perm_on_text(request.user,permission,text_id): 
                return view_func(request, *args, **kwargs)
            else:
                # if some user have the perm and not logged-in : redirect to login
                # TODO : test that
                if not request.user.is_authenticated() and number_has_perm_on_text(permission, text_id) > 0:
                    return HttpResponseRedirect('%s?%s=%s' % (login_url, redirect_field_name, urlquote(request.get_full_path())))                    
            # else : unauthorized
            redirect_url = reverse('unauthorized')
            return HttpResponseRedirect(redirect_url)
        _check_local_perm.__doc__ = view_func.__doc__
        _check_local_perm.__dict__ = view_func.__dict__

        return _check_local_perm
    return _dec

