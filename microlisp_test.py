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
        expr = microlisp_parse( microlisp_tokenize("(and (or true false) (not falsekey))") )
        self.assertEqual( microlisp_eval(STANDART_LOGIC_FUNC, {"falsekey": False}, expr), True)
    def test_eval6_testif(self):
        expr = microlisp_parse( microlisp_tokenize("(if true 1 0)") )
        self.assertEqual( microlisp_eval(STANDART_LOGIC_FUNC, {}, expr), 1)
        expr = microlisp_parse( microlisp_tokenize("(if false 1 0)") )
        self.assertEqual( microlisp_eval(STANDART_LOGIC_FUNC, {}, expr), 0)
    def test_eval7_exception(self):
        expr = microlisp_parse( microlisp_tokenize("(and (or true false) )") )
        try:
            microlisp_eval(STANDART_LOGIC_FUNC, {}, expr)
            self.fail("expect exception")
        except RuntimeError:
            self.assertTrue(True)
    def test_eval8_env(self):
        myfuncs = {
            "+": {"params_count": 2, "func": (lambda funeval, a, b: funeval(a)+funeval(b) )},
        }
        expr = microlisp_parse( microlisp_tokenize("(+ (+ 1 2) (+ 2 param))") )
        self.assertEqual( microlisp_eval(myfuncs, {"param": 3}, expr), 8)

if __name__=='__main__':
	unittest.main()
