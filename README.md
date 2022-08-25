# python-flac-to-wav-audioconverter

## Prerequisites
The Python scripts are made to run on windows devices only!

If you have not installed **ffmpeg** then do so, because it is required. Also don't forget to add it to you PATH environment variables.

## Setup
1. run `install_requirements.bat` to install required python packages
2. run `make_spec.bat` to create a spec file with pyinstaller (if you want the config file to be copied automatically, please read the instructions in the make_spec batch script!, otherwise you can copy the `config.ini` file manually into the folder where the executable will be build)
3. run `build.bat` to build the executable from the spec file