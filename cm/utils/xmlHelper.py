import xml.dom.minidom
import re

#REPLACEMENTS = [
#                ('<br>\s*</br>' , '<br />'),
#                ('<br>' , '<br />'),
#                ]
#def fix_xhtml(string):
#    """
#    Fix html from editor
#
#    >>> fix_xhtml('<b><br>  </br></b>')
#    '<b><br /></b>'
#    >>> fix_xhtml('<b><br>  </br></b><br>')
#    '<b><br /></b><br />'
#    """
#    res = string
#    for f,t in REPLACEMENTS:
#        res = re.sub(f,t,res)
#    return res
    
def fix_autoclosing_tags(string):
    """
    Fix autoclosing tags like <a />
    bug firefox in <a /> with 'name'
    
    >>> fix_autoclosing_tags('<a/>')
    '<a></a>'
    >>> fix_autoclosing_tags('<a />')
    '<a ></a>'
    >>> fix_autoclosing_tags('<a name="so what ?"/>')
    '<a name="so what ?"></a>'
    >>> fix_autoclosing_tags('<a name="test"/><span></span><br/>')
    '<a name="test"></a><span></span><br></br>'
    """
    return re.sub("<(?P<tag>\w+)(?P<space>\s*)(?P<rest>[^<^>]*?)/>","<\g<tag>\g<space>\g<rest>></\g<tag>>",string)

def linksShouldOpenInNewWindows_old(doc):
    ass = doc.getElementsByTagName("a")
    for a in ass :
        href = a.getAttribute("href").strip()
        target = a.getAttribute("target").strip()
        if href!='' and href.find("#") != 0 and target == '' :
            a.setAttribute("target", "new")
    return doc

def linksShouldOpenInNewWindows(soup):
    ass = soup.findAll('a')
    for a in ass :
        if a.has_key("href") :
            href = a["href"].strip()
            if not a.has_key("target") or a["target"].strip() == '':
                if href!='' and href.find("#") != 0 :
                    a["target"]="new"
    return soup

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    
    
def fix_bugs_old(string):
    """
    Fix various bugs in format that could cause domification to fail
    >>> fix_bugs('<p>sqd<o:p></o:p></p>')
    '<p>sqd</p>'
    """
    return string.replace('<o:p></o:p>','')
    