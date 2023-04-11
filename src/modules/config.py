import json
import sys
from pathlib import Path

application_path: Path = (Path(sys.executable) if getattr(
    sys, 'frozen', False) else Path(__file__).parent).parent.resolve()
config_path = Path.joinpath(application_path, 'config.json')
print(f'INFO: Looking for config file in directory "{config_path}"')

config_defaults = {
    "FileFilter": "flac|m4a",
    "ExportFormat": "aiff",
    "ExportQuality":  "normal",
    "ConvertedFilesDirName":  "converted",
    "RemoveConvertedFiles": False,
    "MirrorFileStructure":  True,
    "RecreateFileNameFromMetadata": True,
    "VerboseFFMPEGOutputs": True
}


def save_config():
    with open(config_path, 'w', encoding='utf8') as f:
        json.dump(config, f)


def load_config():
    try:
        with open(config_path, 'r', encoding='utf8') as f:
            return json.load(f)
    except:
        return config_defaults


config: dict = load_config()
