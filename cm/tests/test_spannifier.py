# -*- coding: utf-8 -*-
import unittest
import xml.dom.minidom
from cm.utils.spannifier import Spannifier
from cm.lib.BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

# python manage.py test 
#       
# python manage.py test cm.TestSpannify.test_spannify

string_tests= [

[u"""<body>kk</body>""", 
u"""<body><span id="w_1">kk</span></body>"""],

[u"""<body>k k</body>""", 
u"""<body><span id="w_1">k</span><span id="w_2"> </span><span id="w_3">k</span></body>"""],

[u"""<body> k k</body>""", 
u"""<body><span id="w_1"> </span><span id="w_2">k</span><span id="w_3"> </span><span id="w_4">k</span></body>"""],

[u"""<body>k k </body>""", 
u"""<body><span id="w_1">k</span><span id="w_2"> </span><span id="w_3">k</span><span id="w_4"> </span></body>"""],

[u"""<body><b>této <c>kk</c></b></body>""", 
u"""<body><b><span id="w_1">této</span><span id="w_2"> </span><c><span id="w_3">kk</span></c></b></body>"""],
[u"""<body><b>této <c>kk</c>titi</b></body>""", 
u"""<body><b><span id="w_1">této</span><span id="w_2"> </span><c><span id="w_3">kk</span></c><span id="w_4">titi</span></b></body>"""],

]

file_tests = ["simple.html",]

class TestSpannify(unittest.TestCase):
    
    def setUp(self):
        #self.file1 = file('tests/data/simple_html.html')
        pass
    
    # BUG FIX : adjacent whitespaces were replaced with single whitespace   
    # this is necessary for unspannify_new (used in apply_amendments)
    def test_beautifulsoup_preserve_spanned_whitespaces(self):
        spannifier = Spannifier() 
        test = unicode("<span>        </span>") 
        self.assertEqual(test, unicode(spannifier.get_the_soup(test))) 
            
    def test_spannify(self):
        spannifier = Spannifier() 
        
        for [expectedResult, input] in string_tests :
            soup = spannifier.get_the_soup(input)
            res2 = spannifier.unspannify_new(soup)
            self.assertEqual(unicode(res2),expectedResult)
            
            
#        for [input, expectedResult] in string_tests :
#            
#            doc = xml.dom.minidom.parseString(input)
#            soup = spannifier.get_the_soup(input)
#            
#            res = spannifier.spannify(doc)
#            res2 = spannifier.spannify_new(soup)
#            
##            print res
##            print res2
##            print expectedResult
#            
#            self.assertEqual(res,unicode(expectedResult, 'utf-8'))
##            self.assertEqual(res,res2)
#            
        for filename in file_tests :
            if filename[:5] == "span_" :
                doc = xml.dom.minidom.parse('cm/tests/data/%s' % filename)
                soup = BeautifulSoup('cm/tests/data/%s' % filename, convertEntities=["xml", "html"])
                
                res = spannifier.spannify(doc)
                res2 = spannifier.spannify_new(soup)
                
                expectedResult = file('cm/tests/data/res_%s' % filename).read()
#                print res
                self.assertEqual(res2,expectedResult)



#        doc = xml.dom.minidom.parse('cm/tests/data/livreblanc.html')
#        res = spannifier.spannify_old(doc)

if __name__ == '__main__':
#    import psyco
#    psyco.full()        
#    import cProfile
#    cProfile.run('unittest.main()', 'fooprof3')
    unittest.main()