import unittest
import os

from pymenu import PyMenuCompletions

class TestPathCompletions(unittest.TestCase):

    def setUp(self):
        self.pymenu = PyMenuCompletions()

    def test_files(self):
        self.assertEqual(self.pymenu.completePath("tes"), ["tests.py", "tests"])

    def test_dirs(self):
        self.assertEqual(self.pymenu.completePath("tests/t"), ["test1", "test2"])

    def test_nonexistent(self):
        self.assertEqual(self.pymenu.completePath("xyz"), [])


class TestOSCommandCompletion(unittest.TestCase):

    def setUp(self):
        self.pymenu = PyMenuCompletions()

    # dir is hopefully always available on all target platforms,
    # although its functionality might be different
    def test_name(self):
        self.assertTrue("dir" in self.pymenu.completeCommand("di"))


class TestCommandCompletion(unittest.TestCase):

    def setUp(self):
        self.pymenu = PyMenuCompletions()
        self.pymenu.binpaths = [os.path.join(os.path.dirname(__file__), "tests")]

    def test_name(self):
        self.assertEqual(self.pymenu.completeCommand("di"), ["dir"])

    def test_nonexitent(self):
        self.assertFalse("xyzlolo" in self.pymenu.completeCommand("xyzlolo"))

if __name__ == '__main__':
    unittest.main()
