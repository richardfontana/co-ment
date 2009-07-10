# -*- coding: utf-8 -*-
import unittest
from cm.utils.commentPositioning import CommentPositionComputer

#
# aa bbb ccc with a comment on bbb
#



# previous_word_list    
# new_word_list
# startendlist       : [[1 based index of start word, 1 based index of end word], ...]
# expected_result    : [[] : for comments that are not valid anymore
#                       [1 based index of new start word, 1 based index of new end word] : for comments that have moved 
#                      , ...]
tests_input = [    
        [
            #0      1     2           3            4       5            6
            ["ceci","est","todelete1","todelete2", "test", "todelete3", "ouais"], 
            #0      1     2       3
            ["ceci","est","test", "ouais"], 
            [[1,2], [3,3],[3,4],[4,4],[4,5],[6,6]],
            [[],    [],   [],   [2,2],[],   [3,3]]
        ],
        [
            #0      1     2      3
            ["ceci","est", "un", "test"], 
            #0      1     2           3           4    5      6
            ["ceci","est","inserted1","inserted2","un","test","inserted3",], 
            [[1,1],[2,3],[1,2],[3,3]],
            [[1,1],[4,5],[],   [5,5]]
        ],
        [
            #0      1     2    3        4       5
            ["ceci","est","un","super", "test", "ouais"], 
            #0      1     2    3           4           5       6
            ["ceci","est","un","replaced1","replaced2","test", "ouais"], 
            [[1,2],[3,3],[4,4],[4,5]],
            [[1,2],[],   [5,5],[5,6]]
            
        ],
        [
                #0   1   2   3       4   5       6   7   8   9   10  11  12  13  14  15          16
            [    "a","b","c","d",    "e","f",    "g","h","i","j","k","l","m","n","o","p",        "q"], 
            #0   1       2   3   4   5   6   7   8   9       10  11      12      13  14  15  16 17  18 
            ["0","a",    "c","x","x","e","f","y","g","x",    "j","x",    "m",    "o","p","x","x","x","q"], 
            [[0,1],[1,1],[1,2],[2,2],[3,4],[4,4],[4,5],[4,6],[6,6],[8,8],[8,9],[12,12],[14,15],[14,16],[16,16]],
            [[],   [],   [],   [2,2],[],   [5,5],[5,6],[],   [8,8],[],   [],   [12,12],[13,14],[],     [18,18]]
        ]
]

class TestCommentPositionComputer(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_compute(self):
        
        for previous_wl, new_wl, startendlist, expected_result in tests_input :
            startendlistwithids = [[0,i,j] for i, j in startendlist]

            computer = CommentPositionComputer(previous_wl, new_wl, startendlistwithids)
            res = computer.compute()
            
            self.assertEqual(len(res), len(expected_result))
            
            for i in xrange(0, len(res)) :
                id, initial_start, initial_end, computed_start, computed_end, valid = res[i]
                  
                if valid :
                    self.assertEqual([computed_start, computed_end], expected_result[i])
                else :
                    self.assertEqual([], expected_result[i])
#                self.asserEqual(valid, expected_result[i][2])

if __name__ == '__main__':
    unittest.main()