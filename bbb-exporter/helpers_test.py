import unittest

from helpers import str_integer_to_int


class StrIntegerToIntTest(unittest.TestCase):
    def test_something(self):
        self.assertEqual(str_integer_to_int("0"), 0)
        self.assertEqual(str_integer_to_int("11"), 11)
        self.assertEqual(str_integer_to_int("-123"), -123)
        self.assertEqual(str_integer_to_int(""), 0)
        self.assertEqual(str_integer_to_int("1,234"), 1234)
        self.assertEqual(str_integer_to_int("-1,234"), -1234)
        self.assertEqual(str_integer_to_int("1.234"), 1)
        self.assertEqual(str_integer_to_int("-1.234"), -1)
        self.assertEqual(str_integer_to_int("1,223.234"), 1223)
        self.assertEqual(str_integer_to_int("-1,223.234"), -1223)


if __name__ == '__main__':
    unittest.main()
