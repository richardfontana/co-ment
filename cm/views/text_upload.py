from cm.models import Profile,Text, TextVersion, Role,ObjectUserRole, Image,user_can_create_text
from cm.security import local_text_permission_required 
from cm.utils.mail import EmailMessage
from cm.utils.ooconvert import convert,fix_img_path,extract_css_body
from cm.views import BaseBlockForm, BlockForm
import chardet
from django import forms
from django.conf import settings as dj_settings
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext 
from django.template.context import get_standard_processors
from django.template.defaultfilters import urlencode
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.decorators.cache import cache_page
from urlparse import urlparse

class UploadForm(BlockForm):
    file = forms.FileField(
                           label= ugettext_lazy(u"File"),
                           )


def cleanup_extension(name):
    if len(name) > 4 and name[-4] == ".":
        return name[:-4]
    else:
        return name

# TODO : http://code.djangoproject.com/ticket/5925
# use reverse('uauthorized') 
@user_passes_test(lambda u: user_can_create_text(u),login_url = '/unauthorized')
def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            file_name = data['file'].name
            file_content = data['file'].read()
            try:
                html_res_content,images = convert(file_content,'html')
                xhtml_res_content,_not_used_ = convert(file_content,'xhtml')
            except:                
                if dj_settings.DEBUG:
                    raise
                else:
                    # TODO : manage errors : warn admins & co
                    pass
                request.session['message'] = _(u"Error uploading text.")
                workspace_url = reverse('texts-user',args=[request.user.id])            
                return HttpResponseRedirect(workspace_url)            
            text = Text.objects.create_text(user=request.user, title=cleanup_extension(file_name), content="")
            rev = text.get_latest_version()

            iimg = {}
            # save images
            for img_name,img_content in images.items():
                new_img_name = str(text.id) + "_" + img_name
                
                image = Image.objects.create_image(rev, new_img_name,img_content)
                                
                slash_path = image.get_url()                
                iimg[img_name] = slash_path 
            
            # figure out the encoding
            # for some reason : same doc : dev -> utf8 / prod -> latin2
            enc = chardet.detect(html_res_content)['encoding']
            try_encodings = [enc,'utf8','latin1']
            res_content = None
            for encoding in try_encodings:
                try:
                    res_content = fix_img_path(unicode(html_res_content,encoding),
                                               unicode(xhtml_res_content,encoding),
                                               iimg)
                    break;
                except UnicodeDecodeError:
                    pass
            if not res_content:
                raise Exception('UnicodeDecodeError could not decode')
            css,body = extract_css_body(res_content)
            rev = text.get_latest_version()
            rev.content = body
            rev.css = css
            rev.save() 
            request.session['message'] = _(u"Text Uploaded.")
            #workspace_url = reverse('texts-user',args=[request.user.id])            
            #return HttpResponseRedirect(workspace_url)
            edit_url = reverse('text-edit',args=[text.id])
            return HttpResponseRedirect(edit_url)
    else:
        form = UploadForm()
    return render_to_response('texts/upload.html', {'form': form }, context_instance=RequestContext(request))
