"""REPL validation tests."""
import unittest
from src.shell import Shell


class ShellTests(unittest.TestCase):
    """Check blank input, errors and exit semantics."""

    def test_empty(self):
        self.assertEqual(Shell().execute("  ").text, "")

    def test_unknown(self):
        self.assertTrue(Shell().execute("invalid").error)

    def test_exit(self):
        self.assertTrue(Shell().execute("exit").exit)
        self.assertTrue(Shell().execute("exit extra").error)

    def test_argument_count(self):
        self.assertTrue(Shell().execute("cd a b").error)
