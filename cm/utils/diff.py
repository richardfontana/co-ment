import difflib, string

def isatag(x): return x.startswith("<") and x.endswith(">")

def text_diff(a, b):
    res = []
    a, b = createlist(a), createlist(b)
    s = difflib.SequenceMatcher(isatag, a, b)
    for e in s.get_opcodes():
        if e[0] == "replace":
            res.append('<del class="diff modified">'+''.join(a[e[1]:e[2]]) + '</del><ins class="diff modified">'+''.join(b[e[3]:e[4]])+"</ins>")
        elif e[0] == "delete":
            res.append('<del class="diff">'+ ''.join(a[e[1]:e[2]]) + "</del>")
        elif e[0] == "insert":
            res.append('<ins class="diff">'+''.join(b[e[3]:e[4]]) + "</ins>")
        elif e[0] == "equal":
            res.append(''.join(b[e[3]:e[4]]))
        else: 
            raise "error parsing %s" %(e[0])
    return ''.join(res)

def createlist(x, b=0):
    mode = 'char'
    cur = ''
    out = []
    for c in x:
        if mode == 'tag':
            if c == '>': 
                if b: cur += ']'
                else: cur += c
                out.append(cur); cur = ''; mode = 'char'
            else: cur += c
        elif mode == 'char':
            if c == '<': 
                out.append(cur)
                if b: cur = '['
                else: cur = c
                mode = 'tag'
            elif c in string.whitespace: out.append(cur+c); cur = ''
            else: cur += c
    out.append(cur)
    return filter(lambda x: x is not '', out)
