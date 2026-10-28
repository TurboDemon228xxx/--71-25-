@echo off
cd /d "%~dp0.."
rem Each invocation opens a GUI; use exit to continue.
for %%S in (startup remove errors unknown arguments file_directory missing option remove_directory root current exit_arguments exit) do (
  python main.py --vfs examples/vfs.xml --startup examples/%%S.txt
)
