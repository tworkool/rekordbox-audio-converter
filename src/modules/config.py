import configparser
import sys
from pathlib import Path

config_parser = configparser.ConfigParser()

if getattr(sys, 'frozen', False):
    application_path = Path(sys.executable).parent.resolve()
elif __file__:
    application_path = Path(__file__).parent.parent.resolve()

config_path = Path.joinpath(application_path, 'config.ini')
print(f'INFO: Looking for config file in directory "{config_path}"')
config_parser.read(config_path)


def try_config_get(section, key, fallback):
    fallback_type = type(fallback)
    try:
        if fallback_type is int:
            return config_parser.getint(section, key)
        elif fallback_type is bool:
            return config_parser.getboolean(section, key)
        elif fallback_type is float:
            return config_parser.getfloat(section, key)
        else:
            return config_parser.get(section, key)
    except Exception:
        print(
            f"ERROR: could not parse value of {section}/{key}, returning fallback value")
        return fallback


def get_config():
    return {
        "FileFilter": try_config_get('AUDIOPARSER', 'FileFilter', fallback='flac|m4a'),
        "ExportFormat": try_config_get('AUDIOPARSER', 'ExportFormat', fallback='wav'),
        "ConvertedFilesDirName": try_config_get('AUDIOPARSER', 'ConvertedFilesDirName', fallback='converted'),
        "RemoveConvertedFiles": try_config_get('AUDIOPARSER', 'RemoveConvertedFiles', fallback=False),
        "MirrorFileStructure": try_config_get('AUDIOPARSER', 'MirrorFileStructure', fallback=True),
        "TitleSeparator": try_config_get('AUDIOPARSER/FILENAMEMODIFICATIONS', 'TitleSeparator', fallback='-'),
        "CustomRegexReplacement": try_config_get('AUDIOPARSER/FILENAMEMODIFICATIONS', 'CustomRegexReplacement', fallback=''),
        "RecreateFileNameFromMetadata": try_config_get('AUDIOPARSER/FILENAMEMODIFICATIONS', 'RecreateFileNameFromMetadata', fallback=True),
    }


config = get_config()
