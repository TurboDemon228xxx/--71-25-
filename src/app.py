"""Tkinter graphical terminal."""
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from src.shell import Shell
from src.config import load_config
from src.startup import run_script
from src.vfs import VFS
from tkinter import messagebox
import xml.etree.ElementTree as ET


class Terminal:
    """Graphical terminal with scrollable output and command input."""

    def __init__(self, root: tk.Tk, name: str = "VFS") -> None:
        self.root = root
        self.shell = Shell()
        root.title(f"UNIX emulator - {name}")
        root.geometry("850x540")
        self.output = ScrolledText(
            root, bg="#151820", fg="#e4e8ef", font=("Consolas", 11),
            state="disabled", wrap="word",
        )
        self.output.pack(fill="both", expand=True)
        self.entry = tk.Entry(root, font=("Consolas", 12))
        self.entry.pack(fill="x", padx=6, pady=6)
        self.entry.bind("<Return>", self.submit)
        self.entry.focus_set()
        self.write("UNIX emulator, variant 26. Type exit to close.")

    def write(self, text: str) -> None:
        """Append output to the read-only terminal history."""
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def run_line(self, line: str):
        """Echo and execute input, including startup script commands."""
        self.write(f"$ {line}")
        result = self.shell.execute(line)
        if result.text:
            self.write(("Error: " if result.error else "") + result.text)
        if result.exit:
            self.root.destroy()
        return result

    def submit(self, event=None) -> None:
        """Handle the Return key."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.run_line(line)


def main() -> None:
    """Start the graphical REPL."""
    config = load_config()
    root = tk.Tk()
    root.withdraw()
    try:
        vfs = VFS.load(config.vfs)
    except (OSError, UnicodeError, ValueError, ET.ParseError) as exc:
        messagebox.showerror("VFS error", str(exc), parent=root)
        root.destroy()
        raise SystemExit(1) from exc
    root.deiconify()
    terminal = Terminal(root, vfs.name)
    terminal.shell = Shell(vfs)
    terminal.write(f"Configuration: vfs={config.vfs}, startup={config.startup}")
    if config.startup:
        root.after(100, lambda: run_script(
            config.startup, terminal.run_line, terminal.write,
        ))
    root.mainloop()
