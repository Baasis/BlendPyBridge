@echo off
set STEAM_PATH="C:\Program Files (x86)\Steam\steam.exe"
set BLENDER_APPID=365670
set PYTHON_SCRIPT="D:\LIB_SVN\BRANCH_Personal_Use\DevCave\blSocketBridge\blSocketBridge.py"

%STEAM_PATH% -applaunch %BLENDER_APPID% --python %PYTHON_SCRIPT%
