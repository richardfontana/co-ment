# -*- coding: utf-8 -*-

import re

# same as tagging.utils.find_tag_re  
tag_list_re = re.compile(r'[-\w]+', re.U)

def tag_list_validator(tag_string):
    """
    >>> tag_list_validator('aa, bb, cc')
    True
    >>> tag_list_validator(',,,, aa,, bb, cc ,,,,,,,,  ,')
    True
    >>> tag_list_validator('uuuuuu, aa, jj, sdfsdf , hhh, sdqsd, qzedqsd, thqsdouqsd, emlmlk, ffd, qsdfk, $$$êêê$$$, ££££¨%µµ%µ%')
    False
    """
    ctags = tag_string.split(',')
    tags = []
    for t in ctags :
        tags += t.split(' ')
    for t in tags :
        if t and not tag_list_re.match(t) :
            return False
    return True


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
