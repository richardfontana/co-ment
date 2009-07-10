from django.conf.urls.defaults import *
from django.contrib import admin

from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^mysite/', include('mysite.foo.urls')),

    # Uncomment this for admin:
    # $$$$ RBE  TODO test it !!
#      (r'^admin/(.*)', admin.site.root),

)


from cm.views import texts
from cm.views import texts_settings
from cm.views import site
from cm.views import i18n
from cm.views import alerts

urlpatterns += patterns('',
     url(r'^$', site.index, name="index"),
     url(r'^contact/$', site.contact, name="contact"),
     url(r'^contact/(?P<topic_str>\w+)/$', site.contact_topic, name="contact-topic"),
     
     url(r'^unauthorized/$', site.unauthorized, name="unauthorized"),
     url(r'^embeded_unauthorized/$', site.embeded_unauthorized, name="embeded_unauthorized"),


#     (r'^i18n/setlang/$', 'i18n.set_language'),
     url(r'^i18n/setlang/(?P<lang_code>\w+)/$', i18n.set_language, name="setlang"),
     
     url(r'^texts/(?P<user_id>\d+)/$', texts.user, name="texts-user"),
#     (r'^texts/search/(?P<search_string>\.+)/$', 'texts.search'),

     url(r'^text/(?P<text_id>\d+)/(?P<version_id>\d+)/$', texts.viewandcommentversion, name="text-viewandcommentversion"),
     url(r'^text/(?P<text_id>\d+)/$', texts.viewandcommentversion, name="text-viewandcomment"),
     url(r'^text/(?P<text_id>\d+)/invite/(?P<invite_str>.+)/$', texts.invite, name="text-invite"),     
     url(r'^text/(?P<text_id>\d+)/edit/$', texts.edit, name="text-edit"),
     url(r'^text/(?P<text_id>\d+)/settings/$', texts_settings.settings, name="text-settings"),
     url(r'^text/(?P<text_id>\d+)/versions/$', texts.versions, name="text-versions"),
     url(r'^version/(?P<version_id>\d+)/$', texts.version_content, name="text-content"),
     url(r'^text/(?P<text_id>\d+)/duplicate/$', texts.duplicate, name="text-duplicate"),
     url(r'^text/(?P<text_id>\d+)/delete/$', texts.delete, name="text-delete"),
     # refactor to avoid text_id : not useful
     url(r'^text_versions/(?P<rev_2_id>\d+)/(?P<rev_1_id>\d+)/diff/$', texts.diff_versions, name="text-diffversions"),
     url(r'^text_version/(?P<version_id>\d+)/revert/$', texts.revert_to_version, name="text-reverttoversion"),
     url(r'^text_version/(?P<version_id>\d+)/delete/$', texts.delete_version, name="text-deleteversion"),
     
     url(r'^text_version/(?P<version_id>\d+)/precreate/$', texts.precreate_version, name="text-precreate"),
     
     url(r'^text_version_css/(?P<version_id>\d+)/$', texts.version_css, name="text-versioncss"),

     url(r'^text/add/$', texts.add, name="text-add"),
     url(r'^text/upload/$', 'cm.views.text_upload.upload', name="text-upload"),

     # email alert
     url(r'^emailalertremove/(?P<key>\w+)/$',alerts.emailalert_remove, name="emailalert-remove"),

     # we need to put the images in the db for checking permissions
     url(r'^text/image/(?P<image_id>\d+)/$', texts.image, name="text-image"),

     url(r'^debug-trace/$', site.debug_trace, name="debug-trace"),

#     (r'^text/(?P<object_id>\d+)/(?P<rev_id>\d+)/$', 'text.rev_viewandcomment'),
#     (r'^text/(?P<object_id>\d+)/(?P<rev_id>\d+)/edit/$', 'text.rev_edit'),
#     (r'^text/(?P<object_id>\d+)/(?P<rev_id>\d+)/duplicate/$', 'text.rev_duplicate'),
#     (r'^text/(?P<object_id>\d+)/(?P<rev_id>\d+)/settings/$', 'text.rev_settings'),
     
#     (r'^text/(?P<object_id>\d+)/versions/$', 'text.versions_view'),
)

if False :# so_
    urlpatterns += patterns('',
       url(r'^so_text/(?P<text_id>\d+)/(?P<version_id>\d+)/$', texts.so_viewandcommentversion, name="so-text-viewandcommentversion"),
       url(r'^so_text/(?P<text_id>\d+)/$', texts.so_viewandcommentversion, name="so-text-viewandcomment"),
       url(r'^so_version/(?P<version_id>\d+)/$', texts.version_content, kwargs={'so_b':True}, name="so-text-content"),
    )

from cm.views import public_texts
urlpatterns += patterns('',
     url(r'^list_public/$', public_texts.list_public, name="list-public"),
)

# feeds
from cm.views import feeds
urlpatterns += patterns('',
     url(r'^text/(?P<text_id>\d+)/feeds/$', feeds.page, name="text-feeds"),
     url(r'^text/(?P<text_id>\d+)/feeds/reset_key/$', feeds.reset, name="text-feeds-reset-key"),
     url(r'^feed/text/(?P<text_id>\d+)/$', feeds.text_feed, name="feed-text"),
     url(r'^feed/text/(?P<text_id>\d+)/(?P<private_key>\w+)/$', feeds.private_text_feed, name="private-feed-text"),
)

from cm.views import embed
urlpatterns += patterns('',
     url(r'^text/(?P<text_id>\d+)/embed/$', embed.page, name="text-embed"),
     url(r'^embed/(?P<text_id>\d+)/(?P<type>\w+)/$', embed.embed, name="embed"),
#     url(r'^embed/(?P<text_id>\d+)/$', embed.embed, name="embed"),
)


from cm.views import accounts
urlpatterns += patterns('',
    url(r'^contact_user/(?P<user_id>\w+)/$', accounts.contact_user, name="contact-user"),
    url(r'^accounts/profile/$', accounts.profile_view, name="profile"),
    url(r'^accounts/login/$', accounts.login_view, name="login"),
    url(r'^accounts/logout/$', accounts.logout_view, name="logout"),
    url(r'^accounts/password/reset/$', accounts.password_reset_view, name="password-reset"),
    url(r'^accounts/password/reset-pw/(?P<activation_key>\w+)/$', accounts.password_reset_real_view, name="password-reset-real"),
    
    url(r'^activate/(?P<activation_key>\w+)/$',accounts.activate_view_rl, name="activate"),    
    url(r'^activate/(?P<activation_key>\w+)/next(?P<next_activate>.+)/$',accounts.activate_view_next, name="activate-next"),    
    url(r'^activate/(?P<activation_key>\w+)/(?P<row_level_role_id>\d+)/(?P<user_id>\d+)/$',accounts.activate_view, name="activate-rl"),    
    url(r'^activate/(?P<activation_key>\w+)/t(?P<text_id>\d+)/(?P<user_id>\d+)/$',accounts.activate_view_t, name="activate-t"),    
)

if settings.CUST_ALLOWREGISTRATION : 
    urlpatterns += patterns('',
        url(r'^accounts/register/$', accounts.register_view, name="register"),
    )

from cm.views import client
urlpatterns += patterns('',
    url(r'^client/$', client.client_exchange),
    url(r'^versionprint/(?P<version_id>\d+)/$', client.version_print, name="version-print"),
    url(r'^versionexport/(?P<version_id>\d+)/$', client.version_export, name="version-export"),
)

if settings.DEBUG:
	 urlpatterns += patterns('',
     (r'^themedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
                          
     (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'cm/media/'}),
     (r'^client_tests/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'cm/tests/client'}),
     (r'^robots.txt$', 'django.views.static.serve', {'document_root': 'cm/media/', 'path':'robots.txt'}),
     (r'^favicon.ico$', 'django.views.static.serve', {'document_root': 'cm/media/', 'path':'favicon.ico'}),
)

# openid
if settings.OPENID:
    urlpatterns += patterns('',
        url(r'^openid/$', 'django_openidconsumer.views.begin', name='openid'),
        (r'^openid/with-sreg/$', 'django_openidconsumer.views.begin', {
            'sreg': 'email,nickname',
            'redirect_to': '/openid/complete/',
        }),
        url(r'^openid/complete/$', 'django_openidconsumer.views.complete', name='openid-complete'),
        (r'^openid/signout/$', 'django_openidconsumer.views.signout'),
    #    (r'^next-works/$', views.next_works),
    )



if settings.DEBUG:
    from django.contrib import databrowse
    urlpatterns += patterns('',
                            (r'^databrowse/(.*)', databrowse.site.root),                          
                            )


    
    from django.contrib import databrowse
    from cm.models import Profile
    
    databrowse.site.register(Profile)
