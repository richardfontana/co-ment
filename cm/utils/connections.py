import urllib

def register_mailman(email, mailman_adr, fullname=''):
    """
    register email into given mailman adr 
    """
    params = urllib.urlencode({'email': email, 'fullname': fullname})
    try:
        f = urllib.urlopen(mailman_adr,params)
        f.read()
        return True
    except:
        return False