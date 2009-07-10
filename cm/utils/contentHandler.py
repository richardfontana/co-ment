import xml.dom.minidom
from xml.parsers.expat import ExpatError
from cm.utils.xmlHelper import fix_autoclosing_tags, fix_bugs_old, linksShouldOpenInNewWindows, linksShouldOpenInNewWindows_old
from cm.lib.BeautifulSoup import BeautifulSoup
from cm.utils.spannifier import Spannifier


def processContent(content):
        # for : immediate closing of autoclosing tags like <a name=="xxx" /> 
        ss = fix_autoclosing_tags(content.encode('utf8'))
        
        soup = BeautifulSoup(ss) 
        
        soup = linksShouldOpenInNewWindows(soup)
        
        spannedContent_new = Spannifier().spannify_new(soup)
        
        return fix_autoclosing_tags(spannedContent_new)

def processContent_old(content):
    
    # for : immediate closing of autoclosing tags like <a name=="xxx" /> 
    ss = fix_autoclosing_tags(content.encode('utf8'))
    
    ss = fix_bugs_old(ss)
    
    # for : invalid xhtml tags to be converted (<img> for example) 
    # for : entities conversion 
    soup = BeautifulSoup(ss, convertEntities=["xml", "html"]) 
    ss = str(soup) 
    
    # TODO : we must add a main tag for xml conformance
    doc = xml.dom.minidom.parseString('<x>' + ss + '</x>')
    
    doc = linksShouldOpenInNewWindows_old(doc)
    
    # for : textnode are replaced with span nodes around each word
    spannedContent = Spannifier().spannify(doc)
    
    return fix_autoclosing_tags(spannedContent[3:-4])
