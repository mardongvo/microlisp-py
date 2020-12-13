import unittest
from microlisp import microlisp_compile, microlisp_dumps, microlisp_optimize, microlisp_is_expression
from microlisp_special import tree_generator, shrink_all, SPECIAL_LISP_FUNC, special_optimize

def func_stop_test(expr, elem):
    if microlisp_is_expression(expr):
        if expr[0] in ["eq", "not"]:
            return True
    return False
    
class TestMicroLispSpecial(unittest.TestCase):
    def test_shrink(self):
        for txt_src, txt_res in [("(or (eq A a b c) (eq A b c d) E)", "(or (eq A a b c d) E)"),
            ("(or (or (eq A a) (eq B b) (eq B c)))", "(or (eq A a) (eq B b c))"),
            ("(or (and (eq A a)) (eq A b))","(eq A a b)"),
            ("(or (and a (or a a) (and a a a)) b)", "(or a b)"),
            ("(or (eq a b) (eq a c ))", "(eq a b c)"),
            ]:
            expr = microlisp_compile( txt_src ) # sort + shrink
            e = special_optimize(SPECIAL_LISP_FUNC, expr)
            self.assertEqual( microlisp_dumps(e), txt_res)
    def test_addtotree1(self):
        addit = "a"
        code = "(f1 a b c)"
        expect = ["(or (f1 a b c) a)",
            "(and (f1 a b c) a)",
            "(f1 a (or a b) c)",
            "(f1 a (and a b) c)",
            "(f1 a b (or a c))",
            "(f1 a b (and a c))",
        ]
        expr = microlisp_compile(code)
        result = [microlisp_dumps(e) for e in tree_generator(SPECIAL_LISP_FUNC, expr, addit, lambda tree, e: (True, True), lambda tree, e: False)]
        for e in expect:
            self.assertIn(e, result)
        for e in result:
            self.assertIn(e, expect)
    def test_addtotree2(self):
        addit = "a"
        code = "(f1 a (f2 (or a d) b) c)"
        expect = ["(or (f1 a (f2 (or a d) b) c) a)",
            "(and (f1 a (f2 (or a d) b) c) a)",
            "(f1 a (f2 (or a d) b) c)", #`a' in depth (or a d), so after optimization we can get source expression
            "(f1 a (or (f2 (or a d) b) a) c)",
            "(f1 a (and (f2 (or a d) b) a) c)",
            "(f1 a (f2 (and (or a d) a) b) c)",
            "(f1 a (f2 (or (and a d) a) b) c)",
            "(f1 a (f2 (or a d) (and a b)) c)",
            "(f1 a (f2 (or a d) (or a b)) c)",
            "(f1 a (f2 (or a d) b) (and a c))",
            "(f1 a (f2 (or a d) b) (or a c))",
        ]
        expr = microlisp_compile(code)
        result = [microlisp_dumps(e) for e in tree_generator(SPECIAL_LISP_FUNC, expr, addit, lambda tree, e: (True, True), lambda tree, e: False)]
        for e in expect:
            self.assertIn(e, result)
        for e in result:
            self.assertIn(e, expect)

if __name__=='__main__':
	unittest.main()
