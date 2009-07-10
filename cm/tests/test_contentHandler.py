import unittest
import xml.dom.minidom
from cm.utils.contentHandler import processContent

#rbernard@noze:~/dev/workspace/coment$ export PYTHONPATH=.
#rbernard@noze:~/dev/workspace/coment$ python cm/tests/test_contentHandler.py

string_tests= [
# check we'd close tags like <img>

["""<img>""", 
"""<img></img>"""],

# check we'd correctly handle <a name='x'/>

["""<a name="">""", 
"""<a name=""></a>"""],

["""<bb><a name="x"/>x<cc>x</cc>x</bb>""", 
"""<bb><a name="x"></a><span id="w_1">x</span><cc><span id="w_2">x</span></cc><span id="w_3">x</span></bb>"""],

# check we'd correctly handle entities (both html and xml)
["""&apos;&gt;""", 
"""<span id="w_1">\'></span>"""],

# check we'd open links in new windows
["""<div><a href="http://www.lemonde.fr">firstlink</a><a href="#xxxx">secondlink</a></div>""", 
"""<span id="w_1">\'></span>"""],
        ]

class TestContentHandler(unittest.TestCase):
    
    def setUp(self):
        pass

    # TODO : fails !
    def xxtest_contentHandler(self):
        for [input, expectedResult] in string_tests :
            output = processContent(input)
            #print '|',output,'|',expectedResult,'|'
            self.assertEqual(output,expectedResult)
          
    def xxx_to_long_test_long_contentHandler(self):
        content = file('cm/tests/data/long_content.html').read()
        output = processContent(content.decode('utf8'))
            
if __name__ == '__main__':
    unittest.main()