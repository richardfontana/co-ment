from django.core.cache import cache
from django.db.models.sql.datastructures import EmptyResultSet
from tagging.models import Tag
from tagging.utils import LOGARITHMIC, calculate_cloud

TAG_CLOUD_TIMEOUT = 60 * 60 * 24 # 1 day
TAG_CLOUD_KEY = 'tag_cloud_key'

MAX_NB_TAGS_IN_TEXT_CLOUD = 40
def get_tag_cloud(model, filters):
    tag_cloud = cache.get(TAG_CLOUD_KEY)
    if not tag_cloud:
        try:                         
            tags = list(Tag.objects.usage_for_model(model, counts=True, filters=filters))
        except EmptyResultSet:
            tags = []
        # get rid of tags less than 23 characters 
        tags =  [tag for tag in tags if len(tag.name) > 2]
        
        ordered_tags = sorted(tags, key=(lambda x : x.count), reverse = True)
        
#        tag_cloud = calculate_cloud(tags, steps, distribution)
         
        ordered_tags = ordered_tags[:MAX_NB_TAGS_IN_TEXT_CLOUD]
        alpha_ordered_tags =  sorted(ordered_tags, key=(lambda x : x.name))
         
        tag_cloud = calculate_cloud(alpha_ordered_tags, steps=8, distribution=LOGARITHMIC)
#        tag_cloud = list(to_be_computed_cloud)
        
        
        cache.set(TAG_CLOUD_KEY, tag_cloud, TAG_CLOUD_TIMEOUT)
    return tag_cloud

def tag_cloud_reset(**kwargs):
    cache.delete(TAG_CLOUD_KEY)



