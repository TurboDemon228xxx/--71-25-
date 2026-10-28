#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
python3 main.py --vfs examples/minimal.xml
python3 main.py --vfs examples/files.xml
python3 main.py --vfs examples/vfs.xml --startup examples/startup.txt
python3 main.py --vfs examples/missing.xml
