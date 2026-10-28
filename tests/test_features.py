"""Filesystem, commands, configuration and startup regression tests."""
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from src.config import load_config
from src.shell import Shell
from src.startup import run_script
from src.vfs import VFS

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class VFSTests(unittest.TestCase):
    """Check path handling, binary payloads and XML validation."""

    def setUp(self):
        self.vfs = VFS.load(EXAMPLES / "vfs.xml")
        self.shell = Shell(self.vfs)

    def test_binary(self):
        self.assertEqual(self.vfs.get("/binary.bin").data, b"\x00\x01\x02\xff")

    def test_dot_and_root_boundary(self):
        self.vfs.cwd = "/home/student"
        self.assertEqual(self.vfs.normalize("./docs/../hello.txt"),
                         "/home/student/hello.txt")
        self.assertEqual(self.vfs.normalize("../../../../"), "/")

    def test_ls(self):
        self.assertEqual(self.shell.execute("ls /empty").text, "")
        self.assertEqual(self.shell.execute("ls /readme.txt").text, "readme.txt")
        self.assertIn("student", self.shell.execute("ls /home").text)

    def test_cd(self):
        self.assertFalse(self.shell.execute("cd /home/student/docs").error)
        self.shell.execute("cd ..")
        self.assertEqual(self.vfs.cwd, "/home/student")
        self.assertTrue(self.shell.execute("cd /readme.txt").error)
        self.assertEqual(self.vfs.cwd, "/home/student")
        self.shell.execute("cd")
        self.assertEqual(self.vfs.cwd, "/")

    def test_missing_and_file_component(self):
        self.assertTrue(self.shell.execute("ls /missing").error)
        self.assertTrue(self.shell.execute("ls /readme.txt/child").error)

    def test_sizes(self):
        self.assertEqual(self.shell.execute("du -s /").text, "30\t/")
        self.assertEqual(self.shell.execute("du /binary.bin").text,
                         "4\t/binary.bin")
        self.assertIn("10\t/home/student/docs/notes.txt",
                      self.shell.execute("du /home").text)

    def test_tree(self):
        output = self.shell.execute("tree /home").text
        self.assertIn("`-- student", output)
        self.assertIn("notes.txt", output)
        self.assertEqual(self.shell.execute("tree /readme.txt").text,
                         "/readme.txt")

    def test_bad_options_and_arguments(self):
        for line in ["tree -z", "du -z", "ls -z", "tree a b", "rm", "rm -f a"]:
            with self.subTest(line=line):
                self.assertTrue(self.shell.execute(line).error)

    def test_remove_is_memory_only(self):
        path = EXAMPLES / "vfs.xml"
        before = path.read_bytes()
        self.assertFalse(self.shell.execute("rm /binary.bin").error)
        self.assertFalse(self.shell.execute("rm -r /home").error)
        self.assertTrue(self.shell.execute("ls /home").error)
        self.assertEqual(path.read_bytes(), before)
        self.assertTrue(VFS.load(path).get("/home").directory)

    def test_remove_guards(self):
        self.assertTrue(self.shell.execute("rm /home").error)
        self.assertTrue(self.shell.execute("rm -r /").error)
        self.shell.execute("cd /home/student/docs")
        self.assertTrue(self.shell.execute("rm -r /home").error)
        self.assertTrue(self.shell.execute("rm -r .").error)
        self.assertFalse(self.shell.execute("rm ../hello.txt").error)

    def test_multiple_remove(self):
        self.assertFalse(self.shell.execute("rm /readme.txt /binary.bin").error)
        self.assertEqual(self.vfs.size(self.vfs.root), 15)

    def test_all_vfs_examples(self):
        self.assertEqual(VFS.load(EXAMPLES / "minimal.xml").root.children, {})
        self.assertEqual(VFS.size(VFS.load(EXAMPLES / "files.xml").root), 8)

    def test_malformed_xml(self):
        invalid = ["<wrong/>", "<vfs><unknown name='x'/></vfs>",
                   "<vfs><file name='../x'/></vfs>",
                   "<vfs><file name='a'/><file name='a'/></vfs>",
                   "<vfs><file name='x' encoding='base64'>!?</file></vfs>",
                   "<vfs><file name='x' encoding='bad'/></vfs>"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.xml"
            for xml in invalid:
                with self.subTest(xml=xml):
                    path.write_text(xml, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        VFS.load(path)


class ConfigTests(unittest.TestCase):
    """Check exact YAML-over-CLI precedence and invalid configurations."""

    def test_cli(self):
        config = load_config(["--vfs", "a.xml", "--startup", "b.txt"])
        self.assertEqual(config.vfs, Path("a.xml").resolve())
        self.assertEqual(config.startup, Path("b.txt").resolve())

    def test_file_wins(self):
        config = load_config(["--vfs", "ignored", "--startup", "ignored",
                              "--config", str(EXAMPLES / "config.yaml")])
        self.assertEqual(config.vfs, EXAMPLES / "vfs.xml")
        self.assertEqual(config.startup, EXAMPLES / "startup.txt")

    def test_partial_override_and_invalid_yaml(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text("vfs: custom.xml", encoding="utf-8")
            config = load_config(["--config", str(path), "--startup", "a.txt"])
            self.assertEqual(config.vfs, path.parent / "custom.xml")
            self.assertEqual(config.startup, Path("a.txt").resolve())
            for data in ["[", "- list", "vfs: 4", "unknown: value", "", "vfs:"]:
                path.write_text(data, encoding="utf-8")
                with self.subTest(data=data), redirect_stderr(StringIO()):
                    with self.assertRaises(SystemExit):
                        load_config(["--config", str(path)])

    def test_missing_config(self):
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
            load_config(["--config", str(EXAMPLES / "missing.yaml")])


class ScriptTests(unittest.TestCase):
    """Startup execution stops at errors and exit."""

    def run_example(self, name):
        shell = Shell(VFS.load(EXAMPLES / "vfs.xml"))
        commands, output = [], []

        def execute(line):
            commands.append(line)
            return shell.execute(line)

        run_script(EXAMPLES / name, execute, output.append)
        return commands, output

    def test_stop_on_error(self):
        commands, output = self.run_example("errors.txt")
        self.assertEqual(commands, ["cd /missing"])
        self.assertIn("line 2", output[0])

    def test_stop_on_exit(self):
        commands, output = self.run_example("exit.txt")
        self.assertEqual(commands, ["exit"])
        self.assertEqual(output, [])

    def test_success_script(self):
        commands, output = self.run_example("startup.txt")
        self.assertGreater(len(commands), 10)
        self.assertEqual(output, [])

    def test_removal_script(self):
        commands, output = self.run_example("remove.txt")
        self.assertEqual(commands[-1], "rm")
        self.assertIn("stopped", output[0])

    def test_missing_script(self):
        output = []
        run_script(EXAMPLES / "absent.txt", lambda line: None, output.append)
        self.assertIn("cannot read", output[0])
