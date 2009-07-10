# -*- coding: utf-8 -*-
import unittest
from cm.utils.spannifier import Spannifier
from cm.utils.amender import Amender

tests_input= [
               [u"""<body>ceci est un test.</body>""",
               [[1,1, u"totolitoto"]],
               u"""<body>totolitoto est un test.</body>"""],
               [u"""<body><b>céci est</b><span>un</span><b></b> test.</body>""",
               [[1,1, u"totoli toto"],[3,4, u"était <h1>une</h1>"],[6,6, u"tutulitutu."]],
               u"""<body><b>totoli toto était <h1>une</h1></b><span></span><b></b> tutulitutu.</body>"""],
]

class TestAmender(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_amend(self):
        computer = Amender()
        spannifier = Spannifier()
        
        for input, comments, expectedResult in tests_input :
            res = computer.amend(input, comments)
            res = spannifier.unspannify_new(res)
            self.assertEqual(unicode(res),unicode(expectedResult))
            #self.assertEqual(res,unicode(expectedResult, 'utf-8'))

if __name__ == '__main__':
    unittest.main()