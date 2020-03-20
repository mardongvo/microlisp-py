import re

#https://github.com/DerekHarter/python-lisp-parser/blob/master/src/Python-Lisp-Parser.ipynb
def tokenize(txt):
    tokens = re.split('(\s+|\(|\))', txt)
    return [t for t in tokens if len(t) and not t.isspace()]    

def lisp_parse(tokens):
    #NOTE: expressions like ((some expr) token token) not supported
    if len(tokens)==0:
        raise SyntaxError("lisp_parse: empty tokens list")
    if tokens[0]=="(":
        res = []
        tokens.pop(0)
        op = tokens.pop(0)
        if not is_atom(op):
            raise SyntaxError("lisp_parse: invalid atom "+op)
        res.append( op )
        while tokens[0] != ")":
            res.append( lisp_parse(tokens) )
            if len(tokens) == 0:
                raise SyntaxError("lisp_parse: missing ')'")
        if tokens[0] == ")":
            tokens.pop(0)
        else:
            raise SyntaxError("lisp_parse: missing ')'")
        return tuple(res)
    else:
        atom = tokens.pop(0)
        if not is_atom(atom):
            raise SyntaxError("lisp_parse: invalid atom "+atom)
        return decode_atom(atom)

def is_atom(s):
    return re.fullmatch('([A-Z]|[a-z]|[0-9]|[\\.\\+\\*])+',s) != None
    
def decode_atom(s):
    if s == 'true':
        return True
    if s == 'false':
        return False
    try:
        return int(s)
    except: pass
    try:
        return float(s)
    except: pass
    return s
