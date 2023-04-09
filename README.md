# Rekordbox Audio Converter
This is a python audio converter that uses ffmpeg to convert audio files from one format to Rekordbox audio formats (as listed here: https://cdn.rekordbox.com/files/20210302175909/rekordbox6.4.2_introduction_de.pdf [p.23]). Currently the converter is only configured to convert to:
* WAV
* AIFF

But those are the main formats I see as important anyway.
Other formats can be added in the `audio_converter.py` AudioConverter class
This is how the config looks like:
```
self.allowed_formats = ['aiff', 'wav']
self.allowed_quality = ['normal', 'high']
self.ffmpeg_type_arguments = {
    "aiff_normal": {
        "codec": 'pcm_s16be',
        "sampling_rate": '44100',
        "bit_rate": None,
        "custom": [],
    },
    "aiff_high": {
        "codec": 'pcm_s24be',
        "sampling_rate": '96000',
        "bit_rate": None,
        "custom": [],
    },
    ...
}
```

* `allowed_formats` are the out formats
* `allowed_quality` is the output quality
* `ffmpeg_type_arguments` are the ffmpeg arguments for audio codec, sampling rate, bit rate and other custom ffmpeg arguments. The key of an configuration should be: `"<OUT_FILE_TYPE>_<OUT_QUALITY>"`. So in this example the file type aiff with settings for normal and high quality is configured

## Prerequisites
The Python scripts are made to run on windows devices only, but may work on other OS too (did not test).

If you have not installed **ffmpeg** then do so, because it is required. Also don't forget to add it to your PATH environment variables.

## Setup
### First Steps
1. run `install_requirements.bat` to install required python packages
2. run `make_spec.bat` to create a spec file with pyinstaller
3. run `build.bat` to build the executable from the spec file

### Build
execute step 3 of previous chapter
