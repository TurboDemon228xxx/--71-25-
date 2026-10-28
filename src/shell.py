"""Space-separated command parser and REPL."""
from dataclasses import dataclass
from src.vfs import VFS


@dataclass
class Result:
    """Command output and control flags."""
    text: str = ""
    error: bool = False
    exit: bool = False


class Shell:
    """Process commands without executing host OS commands."""

    def __init__(self, vfs=None):
        self.vfs = vfs or VFS()

    def execute(self, line: str) -> Result:
        """Parse and execute a command."""
        tokens = line.split()
        if not tokens:
            return Result()
        command, *args = tokens
        if command == "exit":
            if args:
                return Result("exit: arguments are not supported", error=True)
            return Result(exit=True)
        handlers = {"ls": self.ls, "cd": self.cd,
                    "du": self.du, "tree": self.tree, "rm": self.rm}
        if command not in handlers:
            return Result(f"{command}: unknown command", error=True)
        try:
            return Result(handlers[command](args))
        except ValueError as exc:
            return Result(f"{command}: {exc}", error=True)

    @staticmethod
    def one_path(args):
        """Validate the supported single optional path argument."""
        if len(args) > 1:
            raise ValueError("too many arguments")
        if args and args[0].startswith("-"):
            raise ValueError(f"unsupported option: {args[0]}")
        return args[0] if args else "."

    def ls(self, args):
        """List a directory or a single file."""
        path = self.one_path(args)
        node = self.vfs.get(path)
        if not node.directory:
            return self.vfs.normalize(path).rsplit("/", 1)[-1]
        return "  ".join(sorted(node.children))

    def cd(self, args):
        """Change the in-memory working directory; default to root."""
        path = self.one_path(args) if args else "/"
        if not self.vfs.get(path).directory:
            raise ValueError(f"not a directory: {path}")
        self.vfs.cwd = self.vfs.normalize(path)
        return ""

    def du(self, args):
        """Show recursive payload sizes in bytes; -s gives only a total."""
        summary = bool(args and args[0] == "-s")
        path = self.one_path(args[1:] if summary else args)
        node = self.vfs.get(path)
        lines = []

        def visit(current, label):
            if current.directory and not summary:
                for name, child in sorted(current.children.items()):
                    visit(child, label.rstrip("/") + "/" + name)
            lines.append(f"{self.vfs.size(current)}\t{label}")

        visit(node, self.vfs.normalize(path))
        return "\n".join(lines)

    def tree(self, args):
        """Display a sorted directory tree with ASCII branches."""
        path = self.one_path(args)
        node = self.vfs.get(path)
        lines = [self.vfs.normalize(path)]

        def visit(current, prefix):
            items = sorted(current.children.items())
            for index, (name, child) in enumerate(items):
                last = index == len(items) - 1
                lines.append(prefix + ("`-- " if last else "|-- ") + name)
                if child.directory:
                    visit(child, prefix + ("    " if last else "|   "))

        if node.directory:
            visit(node, "")
        return "\n".join(lines)

    def rm(self, args):
        """Remove files or recursively remove directories in memory."""
        recursive = bool(args and args[0] in ("-r", "-R"))
        paths = args[1:] if recursive else args
        if not paths:
            raise ValueError("missing operand")
        for path in paths:
            if path.startswith("-"):
                raise ValueError(f"unsupported option: {path}")
            absolute = self.vfs.normalize(path)
            if absolute == "/":
                raise ValueError("cannot remove root")
            if (self.vfs.cwd == absolute
                    or self.vfs.cwd.startswith(absolute + "/")):
                raise ValueError("cannot remove working directory or its parent")
            node = self.vfs.get(absolute)
            if node.directory and not recursive:
                raise ValueError(f"is a directory (use -r): {path}")
            parent, name = absolute.rsplit("/", 1)
            del self.vfs.get(parent or "/").children[name]
        return ""
