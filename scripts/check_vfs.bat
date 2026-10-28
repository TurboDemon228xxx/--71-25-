@echo off
cd /d "%~dp0.."
rem Close each window with exit to continue.
python main.py --vfs examples/minimal.xml
python main.py --vfs examples/files.xml
python main.py --vfs examples/vfs.xml --startup examples/startup.txt
python main.py --vfs examples/missing.xml
