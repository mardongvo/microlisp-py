# -*- coding: utf-8 -*-
from microlisp import microlisp_parse, microlisp_tokenize, microlisp_eval, microlisp_is_expression, microlisp_optimize, ml_sortkey, microlisp_dumps
import copy
from functools import partial

""" Generator and optimizator for systems with `and', `or', `eq'

"""

def eqop(funeval, o1, *o2):
    """ Equality function
    
    (eq a b1 [b2...]) mean (a == b1) or (a == b2) or ...
    """
    v1 = o1
    if microlisp_is_expression(o1):
        v1 = funeval(o1)
    for v2 in o2:
        if microlisp_is_expression(v2):
            if v1 == funeval(v2): return True
        else:
            if v1 == v2: return True
    return False

def andop(funeval, *aa):
    """ Lazy version of `and' """
    for a in aa:
        if not funeval(a): return False
    return True

def orop(funeval, *aa):
    """ Lazy version of `or' """
    for a in aa:
        if funeval(a): return True
    return False

SPECIAL_LISP_FUNC = {
"not": {"params_count": 1, "commutative": False, "associative": False, "func": (lambda funeval, a: not funeval(a) )},
"and": {"params_count": -1, "commutative": True, "associative": True, "func": andop},
"or": {"params_count": -1, "commutative": True, "associative": True, "func": orop},
"if": {"params_count": 3, "commutative": False, "associative": False, "func": (lambda funeval, a, b, c: funeval(b) if funeval(a) else funeval(c) )},
"eq": {"params_count": -1, "commutative": False, "associative": False, "func": eqop},
}

def shrink_andor(expr):
    if ((expr[0] == "or") or (expr[0] == "and")) and (len(expr)==2):
        return expr[1]
    return expr

def shrink_eq(expr):
    """ Shrink (or (eq a ...) (eq a ..)) to (eq a b1 b2 ...)"""
    if expr[0] != "or": return expr
    for i in range(1,len(expr)-1):
        for j in range(i+1,len(expr)):
            if microlisp_is_expression(expr[i]) and microlisp_is_expression(expr[j]) and \
                (expr[i][0] == "eq") and (expr[j][0] == "eq") and \
                (expr[i][1] == expr[j][1]):
                newsub = ["eq", expr[i][1]]
                for e in (expr[i][2:]+expr[j][2:]):
                    if e in newsub: continue
                    newsub.append(e)
                newexpr = copy.copy(expr)
                newexpr[i] = newsub
                del newexpr[j]
                return newexpr
    return expr

def shrink_all(expr):
    if microlisp_is_expression(expr):
        res = copy.copy(expr)
        for i in range(1, len(res)):
            res[i] = shrink_all(res[i])
        while True:
            e = shrink_eq(res)
            e = shrink_andor(e)
            if e == res: break
            else:
                res = e
        return res
    return expr

def special_sort(funcs, expr):
    if microlisp_is_expression(expr):
        if expr[0] == "and" or expr[0] == "or":
            lst = list(map(partial(special_sort, funcs), expr[1:]))
            lst.sort(key=ml_sortkey)
            return [expr[0]]+lst
        if expr[0] == "eq":
            lst = list(map(partial(special_sort, funcs), expr[2:]))
            lst.sort(key=ml_sortkey)
            return [expr[0], expr[1]]+lst
        return expr
    else:
        return expr

def special_optimize(funcs, expr):
    if not microlisp_is_expression(expr):
        return expr
    oldexpr = copy.deepcopy(expr)
    while True:
        e = microlisp_optimize(funcs, oldexpr)
        e = special_sort(funcs, e)
        e = shrink_all(e)
        if not microlisp_is_expression(e):
            return e
        res_param = []
        param = e[1:]
        for i in range(len(param)):
            p = special_optimize(funcs, param[i])
            if i==0:
                res_param.append(p)
            else:
                if p != res_param[-1]:
                    res_param.append(p)
        e = [e[0]]+res_param
        if e == oldexpr: break
        oldexpr = e
    return e

def tree_generator(funcs, expr, elem, func_allow, func_stop):
    """ Expressions generator 

    Recursive replace subtrees and nodes of `expr' by
    (and expr `elem')
    (or expr `elem')
    
    funcs: functions definition
    expr: expression tree
    
    func_allow: func_allow(expr, elem) return boolean (allow_and, allow_or)
    Allow or disallow combinations `expr' and `elem' with `and' or `or'
    
    func_stop: func_stop(expr, elem) return boolean
    Disallow or allow combinations with subnodes of `expr'
    """
    if not microlisp_is_expression(expr) and (expr == elem): return
    allow_add, allow_or = func_allow(expr, elem)
    if allow_add:
        yield special_optimize(funcs, ["and", expr, elem])
    if allow_or:
        yield special_optimize(funcs, ["or", expr, elem])
    if func_stop(expr, elem):
        return
    if microlisp_is_expression(expr):
        if len(expr) == 1:
            return
        for i in range(1, len(expr)):
            for e in tree_generator(funcs, expr[i], elem, func_allow, func_stop):
                ecopy = copy.deepcopy(expr)
                ecopy[i] = e
                yield special_optimize(funcs, ecopy)