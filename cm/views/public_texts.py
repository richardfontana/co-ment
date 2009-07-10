from cm.models import Text, TextVersion
from math import ceil
from cm.views import BaseBlockForm, BlockForm
from cm.utils.cache import get_tag_cloud
from django.db import connection, transaction
from django.template.context import get_standard_processors
from django.template import RequestContext 
from django.views.generic.list_detail import object_list
from django import forms
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.utils.translation import ugettext_lazy
from tagging.models import Tag, TaggedItem
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage 

from cm.models import SEARCH_STRING_PARAM,TAGID_PARAM,TAGPAGE_PARAM,START_SEL_KEY,END_SEL_KEY

class SearchForm(BlockForm):    
    q = forms.CharField(
                            error_messages={'required': ugettext_lazy('Please enter a search term')},
                            required = True,
                            label = ugettext_lazy(u"search"),                        
                            max_length=100,
                            widget=forms.widgets.TextInput(attrs={'size' : 30}),
                            )


def list_public(request):
    
    public_texts = Text.objects.get_by_perm(None, "can_view_local_text").order_by('-created')
    public_last_version_ids = [t.get_latest_version().id for t in public_texts]
    tag_cloud = get_tag_cloud(TextVersion, filters = dict(id__in=public_last_version_ids))
    current_tag = None
    from_search = False
    tagged_text = []
    search_string = ''
    tag_id_str = ''
    tag_id = None
    search_form = SearchForm()
 
    paginator = Paginator(public_texts, 10)

    if request.GET :
        if SEARCH_STRING_PARAM in request.GET:
            from_search = True
            search_string = request.GET[SEARCH_STRING_PARAM]
            search_form = SearchForm(request.GET)
            qn = connection.ops.quote_name
            #texts = Text.objects.get_by_perm(None, "can_view_local_text")
            # format request
            public_texts = Text.objects.full_text_search(search_string, public_texts )
            paginator = Paginator(public_texts, 10)
                
        elif TAGID_PARAM in request.GET:
            tag_id_str = request.GET[TAGID_PARAM]
            try: 
                tag_id = int(tag_id_str)
                current_tag = get_object_or_404(Tag, id=tag_id)
                taggedTextVersions = TaggedItem.objects.get_intersection_by_model(TextVersion, [current_tag]).filter(id__in = public_last_version_ids).order_by('-created')
                tagged_text = [tv.text for tv in taggedTextVersions]
                paginator = Paginator(tagged_text, 10)
            except ValueError:
                raise Http404
        
    
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        pageobj = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pageobj = paginator.page(paginator.num_pages)
        
    texts_page_subset = pageobj.object_list
    for text in texts_page_subset :
        last_version = text.get_latest_version()
        nbcomments,nbreplies=last_version.get_visible_commentsandreplies_count(request.user)
        setattr(text,'nbcomments',nbcomments)
        setattr(text,'nbreplies',nbreplies)
    
            
    return render_to_response('texts/list_public.html',{
                            'texts'             : texts_page_subset,
                            'current_tag'       : current_tag,
                            'search_string'     : search_string, 
                            'from_search'       : from_search, 
                            'search_form'       : search_form,
                            'search_string'     : search_string,
                            'tag_id'            : tag_id,
                            'START_SEL_KEY'     : START_SEL_KEY,
                            'END_SEL_KEY'       : END_SEL_KEY,
                            'tag_cloud'         : tag_cloud,
                            'paginator'         : paginator,                           
                            'page'              : pageobj,                           
                           },
                          context_instance=RequestContext(request))
