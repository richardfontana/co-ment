import unittest
from cm.views.client import *
from cm.models import *

#/dev/workspace/coment$ python cm/tests/test_computeOccs.py
class TestComputeOccs(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_computeOccs(self):
        # inputs : attachs described as start, end, start, end ....
        startsEnds =         [[0,0,1,1,2,2],[0,0,0,1,0,2],          [0,2,1,1],            [1,3,5,7,5,7,2,7],             [0,1,1,2,2,3] ] ;
        
        # expected outputs : occs described as start, end, size, start, end, size, ....
        occStartsEndsNb =[ [0,2,1],     [0,0,3,1,1,2,2,2,1],    [0,0,1,1,1,2,2,2,1],  [1,1,1,2,3,2,4,4,1,5,7,3],     [0,0,1,1,2,2,3,3,1]] ;

        user1,_ = User.objects.get_or_create(username = "username1")
        text = Text.objects.create_text(user = user1, title = "title", content="content")
        for i in range(0, len(startsEnds)) :
            comments = [Comment.objects.create(start_word = startsEnds[i][j], end_word = startsEnds[i][j+1], text_version=text.get_latest_version()) for j in  range(0, len(startsEnds[i]), 2)]
            expectedResult = [Occ(occStartsEndsNb[i][j+2], occStartsEndsNb[i][j], occStartsEndsNb[i][j+1]) for j in  range(0, len(occStartsEndsNb[i]), 3)]

            occs = compute_occs(comments, -1, -1) ;
            
            self.assertEqual(len(occs), len(expectedResult))
            
            for j in  range(0, len(expectedResult)) :
                self.assertEqual(occs[j], expectedResult[j])
        
#        self.assertNotEqual(body,None)
#        self.assertNotEqual(css,None)

if __name__ == '__main__':
    unittest.main()
    
    
		
