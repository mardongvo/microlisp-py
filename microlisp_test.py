import unittest
from microlisp import *

class TestMicroLisp(unittest.TestCase):
    def test_tokenizer_spaces(self):
        self.assertEqual( microlisp_tokenize(" (  + apples oranges )  "), ['(', '+', 'apples', 'oranges', ')'] )
    def test_tokenizer_bigger(self):
        self.assertEqual(microlisp_tokenize("(first (list 1 (+ 2 3) 9))"), 
                         ['(', 'first', '(', 'list', '1', '(', '+', '2', '3', ')', '9', ')', ')'])
    def test_parse_exception(self):
        try:
            toks = microlisp_tokenize("(list (of some (me large) 10 15.5)")
            microlisp_parse(toks)
            self.fail("expect exception")
        except SyntaxError:
            self.assertTrue(True)
    def test_parse_exception_invalid_atom(self):
        try:
            toks = microlisp_tokenize("(list' (of some))")
            microlisp_parse(toks)
            self.fail("expect exception")
        except SyntaxError:
            self.assertTrue(True)
    def test_parse_exception_invalid_atom2(self):
        try:
            toks = microlisp_tokenize("(list ())")
            microlisp_parse(toks)
            self.fail("expect exception")
        except SyntaxError:
            self.assertTrue(True)
    def test_parse_complex(self):
        self.assertEqual( microlisp_parse(microlisp_tokenize("(list (of some (me true false) (false again) 10) 15.5)"), 'tuple'),
            ('list', ('of', 'some', ('me', True, False), ('false', 'again'), 10), 15.5))
    def test_parse_simple(self):
        self.assertEqual( microlisp_parse(microlisp_tokenize("(list)"), 'tuple'),
            ('list',))
    def test_eval1(self):
        expr = microlisp_parse( microlisp_tokenize("(and true false)") )
        self.assertEqual( microlisp_eval(STANDART_LOGIC_FUNC, {}, expr), False)
    def test_eval2(self):
        expr = microlisp_parse( microlisp_tokenize("(and (or true false) false)") )
        self.assertEqual( microlisp_eval(STANDART_LOGIC_FUNC, {}, expr), False)
    def test_eval3(self):
        expr = microlisp_parse( microlisp_tokenize("(and (or true false) (not false))") )
        self.assertEqual( microlisp_eval(STANDART_LOGIC_FUNC, {}, expr), True)
    def test_eval4_exception(self):
        expr = microlisp_parse( microlisp_tokenize("(and (or true false) (booz false))") )
        try:
            microlisp_eval(STANDART_LOGIC_FUNC, {}, expr)
            self.fail("expect exception")
        except RuntimeError:
            self.assertTrue(True)
    def test_eval5_env(self):
        expr = microlisp_parse( microlisp_tokenize("(and (or true false) (not (env falsekey)))") )
        self.assertEqual( microlisp_eval(STANDART_LOGIC_FUNC, {"falsekey": False}, expr), True)
    def test_eval6_testif(self):
        expr = microlisp_parse( microlisp_tokenize("(if true 1 0)") )
        self.assertEqual( microlisp_eval(STANDART_LOGIC_FUNC, {}, expr), 1)
        expr = microlisp_parse( microlisp_tokenize("(if false 1 0)") )
        self.assertEqual( microlisp_eval(STANDART_LOGIC_FUNC, {}, expr), 0)
    def test_eval7_exception(self):
        expr = microlisp_parse( microlisp_tokenize("(and (or true false) (not a b))") )
        try:
            microlisp_eval(STANDART_LOGIC_FUNC, {}, expr)
            self.fail("expect exception")
        except RuntimeError:
            self.assertTrue(True)
    def test_eval8_env(self):
        myfuncs = {
            "+": {"params_count": 2, "func": (lambda funeval, a, b: funeval(a)+funeval(b) )},
        }
        expr = microlisp_parse( microlisp_tokenize("(+ (+ 1 2) (+ 2 (env param)))") )
        self.assertEqual( microlisp_eval(myfuncs, {"param": 3}, expr), 8)
    def test_eval9_return_as_atom(self):
        myfuncs = {
            "asis": {"params_count": 1, "func": (lambda funeval, a: a )},
            "+": {"params_count": 2, "func": (lambda funeval, a, b: funeval(a)+funeval(b) )},
        }
        expr = microlisp_parse( microlisp_tokenize("(+ (+ 1 2) (env (asis param)))") )
        self.assertEqual( microlisp_eval(myfuncs, {"param": 3}, expr), 6)
        expr = microlisp_parse( microlisp_tokenize("(env param)") )
        self.assertEqual( microlisp_eval(myfuncs, {"param": 3}, expr), 3)
    def test_eval10_deepenv(self):
        expr = microlisp_parse( microlisp_tokenize("(env (env key1))") )
        self.assertEqual( microlisp_eval({}, {"key1": "key2", "key2": "value"}, expr), "value")
    def test_eval11_function_any_param_count(self):
        myfuncs = {
            "sum": {"params_count": -1, "func": (lambda funeval, *a: sum(map(lambda x: funeval(x), a)) )},
            "+": {"params_count": 2, "func": (lambda funeval, a, b: funeval(a)+funeval(b) )},
        }
        expr = microlisp_parse( microlisp_tokenize("(sum (+ 1 2) 3 (sum 2 3 4) 4 5 6)") )
        self.assertEqual( microlisp_eval(myfuncs, {}, expr), 30)
    def test_eval12_dumps(self):
        for txt in ["(test (test2 boo zoo) (env key1) foo (bar))", "(test a b c)"]:
            expr = microlisp_parse( microlisp_tokenize(txt) )
            self.assertEqual( microlisp_dumps(expr), txt)
    def test_eval13_sort(self):
        for txt_src, txt_res in [("(and (b a c) a c b (a b c) (or b (or 3 2) a))",
            "(and (a b c) (b a c) (or (or 2 3) a b) a b c)")]:
            expr = microlisp_parse( microlisp_tokenize(txt_src) )
            e = microlisp_sort(STANDART_LOGIC_FUNC, expr)
            self.assertEqual( microlisp_dumps(e), txt_res)
    def test_eval14_optimize(self):
        for txt_src, txt_res in [("(or a b)", "(or a b)"),("(or (or a b) c)", "(or c a b)"),
            ("(and (and (and a c) b) c (or a b (or c d)))","(and c (or a b c d) b a c)")]:
            expr = microlisp_parse( microlisp_tokenize(txt_src) )
            e = microlisp_optimize(STANDART_LOGIC_FUNC, expr)
            self.assertEqual( microlisp_dumps(e), txt_res)
    def test_eval15_optimize_same_params(self):
        for txt_src, txt_res in [("(or a b c d a c)", "(or a b c d)"),("(or a (b c) d e (b c) a)", "(or (b c) a d e)")]:
            expr = microlisp_parse( microlisp_tokenize(txt_src) )
            e = microlisp_optimize(STANDART_LOGIC_FUNC, expr)
            e = microlisp_sort(STANDART_LOGIC_FUNC, e)
            res_param = []
            param = e[1:]
            for i in range(len(param)):
                if i==0:
                    res_param.append(param[i])
                else:
                    if param[i] != param[i-1]:
                        res_param.append(param[i])
            e = [e[0]]+res_param
            self.assertEqual( microlisp_dumps(e), txt_res)

if __name__=='__main__':
	unittest.main()
