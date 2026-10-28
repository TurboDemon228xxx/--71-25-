## Практика 1

# Эмулятор UNIX-оболочки — вариант 26

**Группа:** ИКБО-71-25. **Язык:** Python 3.10+. **Интерфейс:** Tkinter GUI.

### 1. Постановка задачи

Разработать графический эмулятор оболочки UNIX-подобной ОС. Для варианта 26 реализованы пять этапов: REPL, конфигурация YAML, виртуальная файловая система XML, команды `ls`, `cd`, `du`, `tree` и удаление `rm` в памяти.

### 2. Реализованные этапы

| Этап | Реализация |
| --- | --- |
| 1. REPL | Окно с именем VFS, история ввода и вывода, ввод по Enter, разбор строки по пробельным символам, ошибки неизвестных команд и аргументов, `exit`. Первоначальные заглушки `ls` и `cd` заменены рабочими командами на этапе 4. |
| 2. Конфигурация | `--vfs`, `--startup`, `--config`; безопасное чтение YAML; значения YAML перекрывают CLI; отладочный вывод настроек. Стартовый скрипт показывает ввод и вывод, останавливается при первой ошибке либо `exit`. |
| 3. VFS | XML считывается в дерево объектов в памяти; файлы UTF-8 и base64; абсолютные и относительные пути, `.` и `..`; примеры пустой VFS, нескольких файлов и трёх уровней вложенности. |
| 4. Основные команды | Просмотр файлов и каталогов, смена каталога, подсчёт размеров и вывод дерева. |
| 5. Дополнительные команды | Удаление файлов и рекурсивное удаление каталогов. XML на диске остаётся неизменным. |

### 3. Установка и запуск

Скачать репозиторий и открыть терминал в его корневой папке. Необходим Python 3.10 или новее с Tkinter (в стандартном установщике Python для Windows он включён; в Linux может потребоваться пакет `python3-tk`).

```bash
python -m pip install -r requirements.txt
python main.py
```

Windows: `run.bat`. Linux/macOS: `sh run.sh`.

Запуск с параметрами:

```bash
python main.py --vfs examples/vfs.xml --startup examples/startup.txt
python main.py --config examples/config.yaml
python main.py --vfs ignored.xml --startup ignored.txt --config examples/config.yaml
```

В последнем примере оба пути берутся из YAML. CLI-пути отсчитываются от текущей папки терминала; пути в YAML — от папки конфигурационного файла. Если ключ отсутствует в YAML, используется CLI-значение. Без параметров загружается `examples/vfs.xml`.

Пример `examples/config.yaml`:

```yaml
vfs: vfs.xml
startup: startup.txt
```

Неверный YAML, неизвестные ключи, неверные типы и недоступный файл конфигурации дают диагностическое сообщение и код завершения 2. Ошибка загрузки VFS показывается в диалоге GUI и завершает программу с кодом 1. Ошибка стартового скрипта выводится в окне; после остановки скрипта можно продолжать интерактивную работу.

### 4. Команды и режимы

| Команда | Назначение и примеры |
| --- | --- |
| `ls [путь]` | Содержимое каталога в алфавитном порядке; для файла — его имя. Без пути — текущий каталог. `ls`, `ls /home`, `ls /readme.txt`. |
| `cd [путь]` | Переход в каталог. Без аргументов — `/`. `cd /home/student`, `cd docs`, `cd ..`, `cd /`. |
| `du [-s] [путь]` | Размер содержимого файлов в байтах. Без `-s` показывает также вложенные файлы и каталоги, с `-s` — только общий размер. `du`, `du -s /home`, `du /binary.bin`. |
| `tree [путь]` | Дерево с ASCII-ветвями; без пути — текущий каталог. `tree`, `tree /home/student`. |
| `rm путь [путь ...]` | Удаление одного или нескольких файлов. `rm /binary.bin`, `rm a.txt b.txt`. |
| `rm -r путь [путь ...]` | Рекурсивное удаление каталогов; `-R` — синоним. `rm -r /home/student/docs`. |
| `exit` | Закрытие окна эмулятора. Аргументы запрещены. |

Пустой ввод игнорируется. Разбор намеренно простой: разделение по пробелам, как в условии; кавычки, имена с пробелами, конвейеры и перенаправления не поддерживаются. Неописанные опции вызывают ошибку. Корень, текущий каталог и его предки защищены от удаления. При `rm` с несколькими путями обработка идёт последовательно до первой ошибки, уже выполненные удаления сохраняются в памяти.

`du` считает длину двоичного содержимого, а не занимаемые блоки физического диска. Каталоги не добавляют собственный размер. Команды не запускают системную оболочку и не обращаются к файлам реальной ОС.

### 5. Формат виртуальной файловой системы

```xml
<vfs name="practice26">
  <file name="readme.txt">Hello, VFS!</file>
  <file name="binary.bin" encoding="base64">AAEC/w==</file>
  <directory name="home">
    <directory name="student">
      <directory name="docs">
        <file name="notes.txt">Variant 26</file>
      </directory>
      <file name="hello.txt">Hello</file>
    </directory>
  </directory>
  <directory name="empty"/>
</vfs>
```

Элементы `directory` содержат файлы и каталоги. Имена уникальны в пределах одного каталога; `/`, пустые имена, `.` и `..` в качестве имён запрещены. По умолчанию содержимое `file` кодируется UTF-8; для бинарных данных используется `encoding="base64"`. Неверный base64 и неизвестные элементы вызывают ошибку. Имя из `vfs/@name` отображается в заголовке окна; если атрибут отсутствует, используется имя XML-файла.

После загрузки XML работа выполняется только с объектами в памяти. При повторном запуске данные восстанавливаются из исходного файла.

### 6. Демонстрация

Ввести в нижней строке окна, нажимая Enter после каждой команды:

```text
$ ls
binary.bin  empty  home  readme.txt
$ cd /home/student
$ tree
/home/student
|-- docs
|   `-- notes.txt
`-- hello.txt
$ du -s /
30      /
$ rm /binary.bin
$ du -s /
26      /
$ cd /missing
Error: cd: no such file or directory: /missing
$ unknown-command
Error: unknown-command: unknown command
$ cd a b
Error: cd: too many arguments
$ exit
```

В `du` размер и путь разделены табуляцией. Повторный запуск возвращает размер `/` к 30 байтам.

Скрипты автоматизированной демонстрации:

```bash
python main.py --config examples/config.yaml
python main.py --vfs examples/vfs.xml --startup examples/remove.txt
python main.py --vfs examples/vfs.xml --startup examples/errors.txt
```

`startup.txt` показывает все успешные основные команды и их режимы. `remove.txt` показывает удаление и завершается намеренной ошибкой `rm` без аргумента. `errors.txt` останавливается на отсутствующем каталоге; следующая команда `ls` не выполняется. Остальные ошибочные сценарии вынесены в отдельные файлы, поскольку один скрипт обязан завершаться при первой ошибке.

В папке `scripts` находятся пары `.bat`/`.sh`: `check_parameters` проверяет параметры, YAML-приоритет и ошибки конфигурации; `check_vfs` — три варианта VFS и отсутствующий XML; `check_commands` — успешные команды, удаление, ошибки и выход. Каждый вызов открывает окно GUI; закрыть его командой `exit`, чтобы перейти к следующему сценарию.

### 7. Проверка

```bash
python -m unittest discover -v
```

Результат локальной проверки: **26 тестов, OK**. Проверены пути и граница корня, бинарные данные, загрузка разных VFS, неверные XML и YAML, приоритет конфигурации, команды и ошибки, остановка скрипта, защита от удаления корня и рабочего каталога. Тест удаления сравнивает байты XML до и после команд и проверяет восстановление VFS повторной загрузкой.

Дополнительно выполнена проверка реального Tkinter-окна: ввод через обработчик Enter, история команд и ответов, имя VFS в заголовке, обработка ошибки и закрытие через `exit`.

### 8. Структура и исходный код

- `main.py` — точка входа.
- `src/app.py` — графическое окно и запуск приложения.
- `src/config.py` — CLI и YAML.
- `src/vfs.py` — дерево XML-VFS и работа с путями.
- `src/shell.py` — парсер и команды.
- `src/startup.py` — стартовые скрипты.
- `examples/` — конфигурация, XML и сценарии.
- `scripts/` — демонстрационные сценарии ОС.
- `tests/` — автоматические тесты.

Ниже приведён полный код основных модулей; отдельные файлы в репозитории предназначены для запуска.

<details>
<summary>main.py</summary>

```python
"""Entry point for practice 1, variant 26."""
from src.app import main

if __name__ == "__main__":
    main()
```

</details>

<details>
<summary>src/app.py</summary>

```python
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
```

</details>

<details>
<summary>src/config.py</summary>

```python
"""CLI and YAML configuration; file values override CLI values."""
import argparse
from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class Config:
    """Resolved application parameters."""
    vfs: Path
    startup: Path | None = None


def load_config(argv=None) -> Config:
    """Read arguments and safely parse a YAML mapping."""
    parser = argparse.ArgumentParser(description="GUI UNIX emulator, variant 26")
    parser.add_argument("--vfs", default="examples/vfs.xml")
    parser.add_argument("--startup")
    parser.add_argument("--config")
    args = parser.parse_args(argv)
    values = {"vfs": args.vfs, "startup": args.startup}
    if args.config:
        path = Path(args.config).resolve()
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("expected a YAML mapping")
            if set(data) - {"vfs", "startup"}:
                raise ValueError("allowed keys: vfs, startup")
            for key, value in data.items():
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"{key}: expected a nonempty path string")
                values[key] = str(path.parent / value)
        except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
            parser.error(f"cannot read configuration: {exc}")
    return Config(
        Path(values["vfs"]).resolve(),
        Path(values["startup"]).resolve() if values["startup"] else None,
    )
```

</details>

<details>
<summary>src/vfs.py</summary>

```python
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
```

</details>

<details>
<summary>src/shell.py</summary>

```python
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
```

</details>

<details>
<summary>src/startup.py</summary>

```python
"""Sequential startup script runner."""
from pathlib import Path
from src.shell import Result


def run_script(path: Path, execute, write) -> None:
    """Echo through execute; stop at the first failure or exit."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        write(f"Error: cannot read startup script: {exc}")
        return
    for number, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        result: Result = execute(line)
        if result.error:
            write(f"Startup script stopped at line {number}: {path}")
            return
        if result.exit:
            return
```

</details>

