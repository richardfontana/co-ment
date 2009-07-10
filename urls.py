from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
)

# jsI18n
js_info_dict = {
    'packages': ('mysite.cm', ), # **************** change mysite to you project's name
}

urlpatterns += patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

admin.autodiscover()

urlpatterns += patterns('',
     (r'^admin/(.*)', admin.site.root),
     (r'', include('cm.urls')),     
)

