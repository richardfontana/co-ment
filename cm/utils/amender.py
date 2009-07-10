from cm.utils.spannifier import Spannifier

class Amender :
    """ 
    xml utility class used to modify text with comment contents
    """
    
    def __init__(self):
        pass
    
    def amend(self, input, comments):
        spannifier = Spannifier() 
        soup = spannifier.get_the_soup(input)
        res = spannifier.spannify_new(soup)
        soup = spannifier.get_the_soup(res)
        for start, end, content in comments :
            inserted = False
            for word in range(start, end + 1) :
                spantoremove = soup.find(id="w_%s"%word)
                if not inserted :
                    # replace the first word with the comment's content  
                    spantoremove.replaceWith(content)
                    inserted = True
                else :
                    spantoremove.extract()
        return soup
        
