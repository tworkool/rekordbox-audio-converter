import configparser
from pathlib import Path

config_parser = configparser.ConfigParser()
config_parser.read(f'{Path(__file__).parent.parent.resolve()}\\config.ini')

def get_config():
    try:
        return {
            "FileFilter": config_parser.get('AUDIOPARSER', 'FileFilter'),
            "ExportFormat": config_parser.get('AUDIOPARSER', 'ExportFormat'),
            "ConvertedFilesDirName": config_parser.get('AUDIOPARSER', 'ConvertedFilesDirName'),
            "RemoveConvertedFiles": config_parser.getboolean('AUDIOPARSER', 'RemoveConvertedFiles'),
            "MirrorFileStructure": config_parser.getboolean('AUDIOPARSER', 'MirrorFileStructure'),
            "TitleSeparator": config_parser.get('AUDIOPARSER/FILENAMEMODIFICATIONS', 'TitleSeparator'),
            "CustomRegexReplacement": config_parser.get('AUDIOPARSER/FILENAMEMODIFICATIONS', 'CustomRegexReplacement'),
            "RecreateFileNameFromMetadata": config_parser.getboolean('AUDIOPARSER/FILENAMEMODIFICATIONS', 'RecreateFileNameFromMetadata'),
        }
    except ValueError as e:
        print("ERROR: cannot parse config file values, the following error occured: ")
        print(e)
        return {}

config = get_config()
