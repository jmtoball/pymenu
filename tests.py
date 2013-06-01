import unittest

from pymenu import PyMenu

class TestPathCompletions(unittest.TestCase):

    def setUp(self):
        self.pymenu = PyMenu()

    def test_files(self):
        self.assertEqual(self.pymenu.completePath("t"), ["tests.py", "tests"])

    def test_dirs(self):
        self.assertEqual(self.pymenu.completePath("tests/"), ["test1", "test2"])

    def test_nonexistent(self):
        self.assertEqual(self.pymenu.completePath("xyz"), [])

if __name__ == '__main__':
    unittest.main()
