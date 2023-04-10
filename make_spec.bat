@echo off
echo generating executable spec file...

rem Name of to be generated spec file
set SPEC_FILE_NAME=RekordboxAudioConverter

rem Add '--windowed' if you would not like to see console outputs
pyi-makespec --onefile --icon=build_assets/favicon.ico --name %SPEC_FILE_NAME% src/main.py

rem Add Python statement to copy config.ini to build folder
ECHO.>>"%SPEC_FILE_NAME%.spec"
ECHO import shutil>>"%SPEC_FILE_NAME%.spec"
ECHO shutil.copyfile('src/config.ini', '{0}/config.ini'.format(DISTPATH))>>"%SPEC_FILE_NAME%.spec"