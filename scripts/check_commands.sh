#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
for script in startup remove errors unknown arguments file_directory missing option remove_directory root current exit_arguments exit; do
  python3 main.py --vfs examples/vfs.xml --startup "examples/$script.txt"
done
