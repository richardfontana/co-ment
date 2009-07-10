import uuid
import xml.dom.minidom
import re
from cm.lib.BeautifulSoup import Comment, BeautifulSoup, NavigableString
INTERNALTOK = "CoMeNtXzXz"
NONSPACE = re.compile(r'\S+') # \S Matches any non-whitespace character

class Spannifier :
    """ 
    xml utility class used to surround words in xml text nodes with a <span id="w_xxx"></span>
    """
    
    def __init__(self):
        pass

    def retrieveTextNodeChildren(self, node, ss):
        """
        retrieves text nodes in node. recursive.
        """
        for nn in node.childNodes:
            if nn.nodeType == xml.dom.Node.TEXT_NODE:    
                ss.add(nn)
            else :
                ss = self.retrieveTextNodeChildren(nn, ss)
        return ss

    def splitWords(self, text):
        """
        gathers spaces and words in returned list
        """
        iterator = NONSPACE.finditer(text)
        words = []
        start = 0
        for match in iterator:
            spaceBeforeWord = text[start:match.start()]
            if spaceBeforeWord :
                words.append(spaceBeforeWord)
            
            word = text[match.start():match.end()]
            words.append(word)
            
            start = match.end() 
    
        if start != 0 :
            spaceAfterWord = text[start:]
            if spaceAfterWord :
                words.append(spaceAfterWord)
                
        return words
            
#    def spannify(self, doc):
#        """ 
#        surround words in xml text nodes with a <span id="w_xxx"></span> 
#        """
#        textNodes = self.retrieveTextNodeChildren(doc, set([]))
#    
#        replac = {} 
#        joiner = '</span><span id="' + INTERNALTOK + '">'
#         
#        marker = str(uuid.uuid4())
#        j = 0
#        for textNode in textNodes :
#            words = self.splitWords(textNode.nodeValue)
#            if words :
#                index = str(j)
#                j = j + 1
#                textNode.nodeValue = marker + index + marker 
#                replac[index] = '<span id="' + INTERNALTOK + '">' + joiner.join(words) + '</span>'
#            
#        mixed = doc.toxml().split(marker)
#        tt = []
#        for i in range(len(mixed)) :
#            if i % 2 == 0:
#                tt.append(mixed[i])
#            else :
#                tt.append(replac[mixed[i]])
#                
#        # another version of minidom puts a \n after xml header
#        tokXml = "".join(tt).replace('<?xml version="1.0" ?>\n','')        
#        tokXml = tokXml.replace('<?xml version="1.0" ?>','')
#        
#        output = ""
#
#        tt = []
#        ss = tokXml.split(INTERNALTOK)
#        
#        d = 1
#        for s in ss[:-1] :
#            tt.append('%s%s%d' % (s, 'w_', d))
#            d = d+1
#        if ss :
#            tt.append(ss[-1])
#            output = "".join(tt)
#             
#        return output    
#            
    def get_text_nodes(self, soup):
        return soup(text=lambda text:not isinstance(text, Comment))

    def is_real_text_node(self, textNode):
        return not textNode.findParent('style') 

    def word_list(self, soup):
        ret = []
        textNodes = self.get_text_nodes(soup)
        for textNode in textNodes :
            if self.is_real_text_node(textNode) :
                words = self.splitWords(textNode.string)
                if words :
                    ret.extend(words)
        return ret

    def get_the_soup(self, input):
        return BeautifulSoup(input, convertEntities=["xml", "html"])
                     
    def spannify_new(self, soup):
        """ 
        surround words in xml text nodes with a <span id="w_xxx"></span> 
        """

        textNodes = self.get_text_nodes(soup)
        joiner = '</span><span id="' + INTERNALTOK + '">'
        for textNode in textNodes :
            if self.is_real_text_node(textNode) :
                words = self.splitWords(textNode.string)
                if words :
                    textNode.replaceWith('<span id="' + INTERNALTOK + '">' + joiner.join(words) + '</span>')                    

        output = ""
        tt = []
        ss = unicode(soup).split(INTERNALTOK)
        
        d = 1
        for s in ss[:-1] :
            tt.append('%s%s%d' % (s, 'w_', d))
            d = d+1
        if ss :
            tt.append(ss[-1])
            output = "".join(tt)
             
        return output

    def unspannify_new(self, soup):
        """ 
        surround words in xml text nodes with a <span id="w_xxx"></span> 
        """
        spanNodes = soup.findAll('span', id=re.compile("w_[0-9]+"))
        for spanNode in spanNodes :
            # has proven to be possible TODO check why with text 589            
            if len(spanNode.contents) == 0 :
                spanNode.extract()  
            else :
                spanNode.replaceWith(spanNode.contents[0])
        return soup    
            
