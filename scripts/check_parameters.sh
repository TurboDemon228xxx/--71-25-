#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
# Close each window with exit to continue.
python3 main.py --vfs examples/vfs.xml
python3 main.py --vfs examples/vfs.xml --startup examples/startup.txt
python3 main.py --vfs ignored.xml --startup ignored.txt --config examples/config.yaml
python3 main.py --config examples/missing.yaml
