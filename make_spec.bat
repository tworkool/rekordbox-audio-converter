@echo off
echo generating executable file...

pyi-makespec --onefile --windowed --name AudioToWavConverter src/main.py

rem Remove '--windowed' if you would like to see console outputs

rem IMPORTANT: Add this to end of generated spec file to copy the config file automatically
rem import shutil
rem shutil.copyfile('src/config.ini', '{0}/config-sample.ini'.format(DISTPATH))