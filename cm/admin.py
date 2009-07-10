from django.contrib import admin
from cm.models import State, Workflow, Image, Profile, TextVersion, Text, Comment, DiscussionItem, Email

admin.site.register(State)
admin.site.register(Workflow)
admin.site.register(Image)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','user','preferred_language','created','service_level','is_temp')
    list_filter = ('is_temp','service_level')
admin.site.register(Profile, ProfileAdmin)

class TextVersionAdmin(admin.ModelAdmin):
#        list_display = ('title','created', 'modified', 'creator')
    list_display = ('title','created', 'modified',)
    ordering = ('-modified','-created') 
    search_fields = ['content']
admin.site.register(TextVersion, TextVersionAdmin)

class TextAdmin(admin.ModelAdmin):
#        list_display = ('__unicode__','creator','created', 'modified', 'get_versions_number','get_objectuserrole_number')
    list_display = ('__unicode__','created', 'modified', 'get_versions_number','get_objectuserrole_number')
    ordering = ('-modified','-created') 
admin.site.register(Text, TextAdmin)

class CommentAdmin(admin.ModelAdmin):
#        list_display = ('__unicode__','creator','username','created','text_version','start_word','end_word')
    list_display = ('__unicode__','username','created','start_word','end_word')
#        list_filter = ('creator',)
    ordering = ('-created',)
admin.site.register(Comment, CommentAdmin)

class DiscussionItemAdmin(admin.ModelAdmin):
#        list_display = ('__unicode__','creator','username','created',)
    list_display = ('__unicode__','username','created',)
#        list_filter = ('creator',)
    ordering = ('-created',)
admin.site.register(DiscussionItem, DiscussionItemAdmin)

class EmailAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','get_recipents_number','created')
    #list_filter = ('from_email',)
    ordering = ('-created',) 
admin.site.register(Email, EmailAdmin)



