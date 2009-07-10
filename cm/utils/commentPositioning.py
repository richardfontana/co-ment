# -*- coding: utf-8 -*-
from difflib import SequenceMatcher
from cm.utils.spannifier import Spannifier


class CommentPositionComputer :
    """ 
    designed to place comments in modified versions : 
    """
    previousVersionWordsList = []
    newVersionWordsList = []
    
    def __init__(self, previousVersionWordsList, newVersionWordsList, startendList):
        self.previousVersionWordsList = previousVersionWordsList
        self.newVersionWordsList = newVersionWordsList
        # comments here are [initial_start, initial_end, computed_start, computed_end, valid ]
        self.computationResults = [[id, start_word, end_word, start_word, end_word, True] for id, start_word, end_word in startendList]
        self.sm = SequenceMatcher(None, self.previousVersionWordsList, self.newVersionWordsList)
        pass

    def compute(self):
        """ 
        returns a list of : 
        [initial_start, initial_end, computed_start, computed_end, valid]
        where 
        initial_start:start_word of comment in previous version
        initial_end:end_word of comment in previous version
        computed_start:computed start_word of comment in next version
        computed_end:computed end_word of comment in next version
        valid:describes wether comment has been impacted by new version. 
        in case valid == False, computed_start and computed_end are not be considered.
        
        TODO (?) : computation is quite simple here, if text has changed in comment's scope comment has valid False.
        initial comment, an enhanced version could be done where a status would have a value among 
        TRUNCATED, AUGMENTED, UNCHANGED, CHANGED ... 
  
        """
        # get_opcodes doc :
        # Return list of 5-tuples describing how to turn a into b. Each tuple is of the form (tag, i1, i2, j1, j2). The first tuple has i1 == j1 == 0, and remaining tuples have i1 equal to the i2 from the preceding tuple, and, likewise, j1 equal to the previous j2.
        #
        #The tag values are strings, with these meanings:
        #
        #Value     Meaning
        #'replace'     a[i1:i2] should be replaced by b[j1:j2].
        #'delete'     a[i1:i2] should be deleted. Note that j1 == j2 in this case.
        #'insert'     b[j1:j2] should be inserted at a[i1:i1]. Note that i1 == i2 in this case.
        #'equal'     a[i1:i2] == b[j1:j2] (the sub-sequences are equal).

        opcodes = self.sm.get_opcodes()
        for tag, i1, i2, j1, j2 in opcodes:
            #print ("%7s a[%d:%d] (%s) b[%d:%d] (%s)" % (tag, i1, i2, self.previousVersionWordsList[i1:i2], j1, j2, self.newVersionWordsList[j1:j2]))

            for i in xrange(0, len(self.computationResults)) : # TODO be clever instead of going through all comments
                id, initial_start, initial_end, computed_start, computed_end, valid = self.computationResults[i]
                #print initial_start, initial_end, computed_start, computed_end, valid
                
                if tag != 'equal' : # test10
                    if initial_start >= i2 : 
                        computed_start += ((j2 - j1) - (i2 - i1))
                        computed_end += ((j2 - j1) - (i2 - i1))
                    elif initial_end >= i1 :
                        valid = False

                self.computationResults[i] = [id, initial_start, initial_end, computed_start, computed_end, valid]
        
#        print self.previousVersionWordsList
#        print self.newVersionWordsList
#        print self.computationResults

        return self.computationResults
    
def compute_word_list(versionContent):
    spannifier = Spannifier() 
    soup = spannifier.get_the_soup(versionContent)
    word_list = spannifier.word_list(soup)
    return word_list

# when submitting from edition page for validation (through xhtml request) content contains \n instead of \r\n
def handle_special_cases(word_list):
    for i in xrange(0, len(word_list)) :
        word_list[i] = word_list[i].replace('\r\n', '\n') 
        
def compute_new_comment_positions(previousVersionContent, newVersionContent, commentList):
    previous_version_word_list = compute_word_list(previousVersionContent)
    new_version_word_list = compute_word_list(newVersionContent)

    handle_special_cases(previous_version_word_list)
    handle_special_cases(new_version_word_list)
    
    # convert comments start and ends from 1 based index to 0 base index
    startendList = [[comment.id, comment.start_word - 1, comment.end_word - 1] for comment in commentList]
    
    comments = dict(((comment.id, comment) for comment in commentList))
    computer = CommentPositionComputer(previous_version_word_list, 
                                       new_version_word_list, 
                                       startendList)
    computationResults = computer.compute()
    ret_tomodify_comments = []
    ret_toremove_comments = []
    for i in xrange(0, len(computationResults)) : 
        id, initial_start, initial_end, computed_start, computed_end, valid = computationResults[i]
        if valid :
            # convert comments start and ends from 0 based index to 1 base index
            comments[id].start_word = computed_start + 1
            comments[id].end_word = computed_end + 1
            ret_tomodify_comments.append(comments[id]) 
            
        else :
            ret_toremove_comments.append(comments[id]) 
    
    return [ret_tomodify_comments, ret_toremove_comments]

        
