@echo off
cd /d "%~dp0.."
rem Close each window with exit to continue.
python main.py --vfs examples/vfs.xml
python main.py --vfs examples/vfs.xml --startup examples/startup.txt
python main.py --vfs ignored.xml --startup ignored.txt --config examples/config.yaml
python main.py --config examples/missing.yaml
