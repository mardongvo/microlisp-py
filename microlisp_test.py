import unittest
from microlisp import *

class TestMicroLisp(unittest.TestCase):
    def test_tokenizer_spaces(self):
        self.assertEqual( tokenize(" (  + apples oranges )  "), ['(', '+', 'apples', 'oranges', ')'] )
    def test_tokenizer_bigger(self):
        self.assertEqual(tokenize("(first (list 1 (+ 2 3) 9))"), 
                         ['(', 'first', '(', 'list', '1', '(', '+', '2', '3', ')', '9', ')', ')'])
    def test_parse_exception(self):
        try:
            toks = tokenize("(list (of some (me large) 10 15.5)")
            lisp_parse(toks)
            self.fail("expect exception")
        except SyntaxError:
            self.assertTrue(True)
    def test_parse_exception_invalid_atom(self):
        try:
            toks = tokenize("(list' (of some))")
            lisp_parse(toks)
            self.fail("expect exception")
        except SyntaxError:
            self.assertTrue(True)
    def test_parse_exception_invalid_atom2(self):
        try:
            toks = tokenize("(list ())")
            lisp_parse(toks)
            self.fail("expect exception")
        except SyntaxError:
            self.assertTrue(True)
    def test_parse_complex(self):
        self.assertEqual( lisp_parse(tokenize("(list (of some (me true false) (false again) 10) 15.5)")),
            ('list', ('of', 'some', ('me', True, False), ('false', 'again'), 10), 15.5))
    def test_parse_simple(self):
        self.assertEqual( lisp_parse(tokenize("(list)")),
            ('list',))

if __name__=='__main__':
	unittest.main()
