# Практическая работа 1 — вариант 26

Группа ИКБО-71-25. Графический эмулятор UNIX на Python 3.10+.

Подробный отчёт, команды, конфигурация, формат VFS, демонстрация и исходный код: [pract.md](pract.md).

```bash
python -m pip install -r requirements.txt
python main.py --config examples/config.yaml
python -m unittest discover -v
```

Для запуска нужен Tkinter. Windows: `run.bat`; Linux/macOS: `sh run.sh`.
