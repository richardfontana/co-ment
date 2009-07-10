import math
from tagging.utils import LOGARITHMIC, LINEAR
from tagging import utils 
from tagging import utils
from cm.lib.BeautifulSoup import BeautifulSoup


#PATCH 1
########
# patching tagging module waiting for a bug fix [http://code.google.com/p/django-tagging/issues/detail?id=91]
def _coment_calculate_tag_weight(weight, max_weight, distribution):
    """
    Logarithmic tag weight calculation is based on code from the
    `Tag Cloud`_ plugin for Mephisto, by Sven Fuchs.

    .. _`Tag Cloud`: http://www.artweb-design.de/projects/mephisto-plugin-tag-cloud
    """
    if distribution == LINEAR or max_weight == 1:
        return weight
    elif distribution == LOGARITHMIC:
        # this is the cm's modification 
        return min((max_weight, math.log(weight) * max_weight / math.log(max_weight)))
    raise ValueError(_('Invalid distribution algorithm specified: %s.') % distribution)

# actual monkey patch
utils._calculate_tag_weight = _coment_calculate_tag_weight

#PATCH 2 
########
# patching BeautifulSoup :
# cf TestSpannify.test_beautifulsoup_preserve_spanned_whitespaces  
BeautifulSoup.PRESERVE_WHITESPACE_TAGS.add('span')
 
#PATCH 3 
########
