import re
from functools import partial, reduce

#https://github.com/DerekHarter/python-lisp-parser/blob/master/src/Python-Lisp-Parser.ipynb
def microlisp_tokenize(txt):
    tokens = re.split('(\s+|\(|\))', txt)
    return [t for t in tokens if len(t) and not t.isspace()]    

def microlisp_parse(tokens, typ='list'):
    #NOTE: expressions like ((some expr) token token) not supported
    if len(tokens)==0:
        raise SyntaxError("microlisp_parse: empty tokens list")
    if tokens[0]=="(":
        res = []
        tokens.pop(0)
        op = tokens.pop(0)
        if not microlisp_is_atom(op):
            raise SyntaxError("microlisp_parse: invalid atom "+op)
        res.append( op )
        while tokens[0] != ")":
            res.append( microlisp_parse(tokens, typ) )
            if len(tokens) == 0:
                raise SyntaxError("microlisp_parse: missing ')'")
        if tokens[0] == ")":
            tokens.pop(0)
        else:
            raise SyntaxError("microlisp_parse: missing ')'")
        if typ == 'list':
            return res
        if typ == 'tuple':
            return tuple(res)
    else:
        atom = tokens.pop(0)
        if not microlisp_is_atom(atom):
            raise SyntaxError("lisp_parse: invalid atom "+atom)
        return microlisp_decode_atom(atom)

def microlisp_is_atom(s):
    return re.fullmatch('([A-Z]|[a-z]|[0-9]|[\\.\\+\\*])+',s) != None
    
def microlisp_decode_atom(s):
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

def microlisp_is_expression(s):
    if isinstance(s, tuple) or isinstance(s, list):
        return True
    return False

STANDART_LOGIC_FUNC = {
"not": {"params_count": 1, "commutative": False, "associative": False, "func": (lambda funeval, a: not funeval(a) )},
"and": {"params_count": -1, "commutative": True, "associative": True, "func": (lambda funeval, *aa: reduce(lambda x,y: funeval(x) and funeval(y), aa) )},
"or": {"params_count": -1, "commutative": True, "associative": True, "func": (lambda funeval, *aa: reduce(lambda x,y: funeval(x) or funeval(y), aa) )},
"if": {"params_count": 3, "commutative": False, "associative": False, "func": (lambda funeval, a, b, c: funeval(b) if funeval(a) else funeval(c) )},
}    
    
def microlisp_eval(funcs, env, expr):
    if microlisp_is_expression(expr):
        #env <param> - get value from environment by key <param>, <param> may be result of function
        if expr[0] == "env":
            if len(expr[1:]) != 1:
                raise RuntimeError("invalid parameters count for "+expr[0])
            try:
                return env[microlisp_eval(funcs, env, expr[1])]
            except KeyError:
                raise RuntimeError("unknown atom "+expr)
        else:
            if expr[0] not in funcs:
                raise RuntimeError("unknown function "+expr[0])
            func_def = funcs[expr[0]]
            if (len(expr[1:]) != func_def["params_count"]) and (func_def["params_count"]!=-1):
                raise RuntimeError("invalid parameters count for "+expr[0])
            return func_def["func"]( partial(microlisp_eval, funcs, env), *expr[1:] )
    return expr

def microlisp_dumps(expr):
    if microlisp_is_expression(expr):
        return "("+expr[0]+(" " if len(expr)>1 else "")+(" ".join(list(map(microlisp_dumps,expr[1:]))) )+")"
    else:
        return str(expr)
    
def ml_sortkey(expr):
    if microlisp_is_expression(expr):
        return "0-"+expr[0]+("".join(list(map(ml_sortkey, expr[1:]))))
    else:
        return "1-"+str(expr)

def microlisp_sort(funcs, expr):
    if microlisp_is_expression(expr):
        lst = list(map(partial(microlisp_sort,funcs), expr[1:]))
        if (expr[0] in funcs) and funcs[expr[0]]["commutative"]:
            lst.sort(key=ml_sortkey)
        return [expr[0]]+lst
    else:
        return expr

def microlisp_optimize(funcs, expr):
    if microlisp_is_expression(expr):
        params = list(map(partial(microlisp_optimize, funcs), expr[1:]))
        if (expr[0] in funcs):
            func_def = funcs[expr[0]]
            if (func_def["params_count"] == -1) and func_def["associative"]:
                do_optimize = True
                while do_optimize:
                    do_optimize = False
                    for i in range(len(params)):
                        p = params[i]
                        if not microlisp_is_expression(p): continue
                        if p[0] == expr[0]:
                            do_optimize = True
                            params.extend(p[1:])
                            del params[i:i+1]
        return [expr[0]]+params
    else:
        return expr