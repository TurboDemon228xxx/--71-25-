"""XML virtual filesystem stored entirely in memory."""
import base64
import binascii
from dataclasses import dataclass, field
from pathlib import Path
import posixpath
import xml.etree.ElementTree as ET


@dataclass
class Node:
    """Directory or binary file."""
    directory: bool
    data: bytes = b""
    children: dict[str, "Node"] = field(default_factory=dict)


class VFS:
    """Resolve POSIX paths without accessing host filesystem paths."""

    def __init__(self, name="VFS"):
        self.name = name
        self.root = Node(True)
        self.cwd = "/"

    @classmethod
    def load(cls, path: Path):
        """Read XML once; never extract or write its contents."""
        element = ET.parse(path).getroot()
        if element.tag != "vfs":
            raise ValueError("XML root must be <vfs>")
        vfs = cls(element.get("name") or path.stem)
        vfs.root = cls._directory(element)
        return vfs

    @classmethod
    def _directory(cls, element):
        """Validate and recursively construct an XML directory."""
        node = Node(True)
        for child in element:
            name = child.get("name", "")
            if not name or name in (".", "..") or "/" in name:
                raise ValueError(f"invalid VFS name: {name!r}")
            if name in node.children:
                raise ValueError(f"duplicate VFS name: {name}")
            if child.tag == "directory":
                value = cls._directory(child)
            elif child.tag == "file":
                if len(child):
                    raise ValueError("file cannot contain XML elements")
                text = child.text or ""
                encoding = child.get("encoding", "utf-8")
                if encoding == "base64":
                    try:
                        data = base64.b64decode("".join(text.split()), validate=True)
                    except (ValueError, binascii.Error) as exc:
                        raise ValueError(f"invalid base64: {name}") from exc
                elif encoding == "utf-8":
                    data = text.encode("utf-8")
                else:
                    raise ValueError(f"unsupported encoding: {encoding}")
                value = Node(False, data)
            else:
                raise ValueError(f"unknown XML element: {child.tag}")
            node.children[name] = value
        return node

    def normalize(self, path="."):
        """Resolve relative paths, dot components and the root boundary."""
        return "/" + posixpath.normpath(
            posixpath.join(self.cwd, path)
        ).lstrip("/")

    def get(self, path="."):
        """Find a node or report a missing/non-directory component."""
        absolute = self.normalize(path)
        node = self.root
        for part in absolute.strip("/").split("/"):
            if not part:
                continue
            if not node.directory:
                raise ValueError(f"not a directory: {part}")
            if part not in node.children:
                raise ValueError(f"no such file or directory: {absolute}")
            node = node.children[part]
        return node

    @staticmethod
    def size(node):
        """Return the sum of file payload bytes below a node."""
        if not node.directory:
            return len(node.data)
        return sum(VFS.size(child) for child in node.children.values())
