import unittest
from hw3 import remove_comments, parse_constants, parse_dict, evaluate_prefix

class TestFunctions(unittest.TestCase):

    def test_single_remove_comments(self):
        text = """:: Это комментарий
        a = 5
        b = 10
        c = 15"""
        expected = """
        a = 5
        b = 10
        c = 15"""
        self.assertEqual(remove_comments(text).strip(), expected.strip())
    def test_multi_remove_comments(self):
        text = """
        a = 5
        b = 10
        {
        это многострочный
        комментарий
        }
        c = 15"""
        expected = """
        a = 5
        b = 10
        
        c = 15"""
        self.assertEqual(remove_comments(text).strip(), expected.strip())

    def test_parse_constants(self):
        text = """a = 5
        b = [+ a 2]
        c = 10"""
        constants, remaining = parse_constants(text)
        expected_constants = {'a': 5, 'b': 7, 'c': 10}  
        self.assertEqual(constants, expected_constants)
        self.assertEqual(remaining, "")  

    def test_parse_dict(self):
        text = """table(
            c => 10,
            d => 20
        )"""
        constants = {}
        parsed_data = parse_dict(text, constants)
        expected_data = {'c': 10, 'd': 20}
        self.assertEqual(parsed_data, expected_data)

    def test_plus_evaluate_prefix(self):
        constants = {'a': 3, 'b': 6}
        expression = "[+ a 2]"
        result = evaluate_prefix(expression, constants)
        self.assertEqual(result, 5)

    def test_minus_evaluate_prefix(self):
        constants = {'a': 3, 'b': 6}
        expression = "[- b a]"
        result = evaluate_prefix(expression, constants)
        self.assertEqual(result, 3)

    def test_mul_evaluate_prefix(self):
        constants = {'a': 3, 'b': 6}
        expression = "[* a b]"
        result = evaluate_prefix(expression, constants)
        self.assertEqual(result, 18)

    def test_div_evaluate_prefix(self):
        constants = {'a': 3, 'b': 6}
        expression = "[/ b a]"
        result = evaluate_prefix(expression, constants)
        self.assertEqual(result, 2)

    def test_pow_evaluate_prefix(self):
        constants = {'a': 3, 'b': 6}
        expression = "[pow a 2]"
        result = evaluate_prefix(expression, constants)
        self.assertEqual(result, 9)
if __name__ == '__main__':
    unittest.main()
