import re
from time import time
from datetime import datetime
from os import walk
from pathlib import Path
from pydub import AudioSegment
from pydub.utils import mediainfo
from modules.config import config
from mutagen import wave, aiff, File as mutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError, TextFrame
""" import mutagen.id3 """


class AudioConverter:
    def __init__(self) -> None:
        self.output = ""
        try:
            self.settings = {
                "file_filter": config['FileFilter'],
                "export_format": config['ExportFormat'],
                "converted_files_dir_name": config['ConvertedFilesDirName'],
                "remove_converted_files": config['RemoveConvertedFiles'],
                "mirror_file_structure": config['MirrorFileStructure'],
                "file_name_modifications": {
                    "title_separator": config['TitleSeparator'],
                    "custom_regex_replacement": config['CustomRegexReplacement'],
                    "recreate_file_name_from_metadata": config['RecreateFileNameFromMetadata']
                }
            }
        except Exception:
            print("ERROR: could not read AudioConverter settings from config")

    def save_print(self, s):
        self.output += s
        self.output += "\n"
        print(s)

    def generate_file_tree(self, path, mirror_file_structure=True):
        root_path_parent = str(Path(path).parent.resolve())
        root_target_folder_name = path[len(root_path_parent)+1:]
        converted_files_dir_abs = f"{root_path_parent}/{root_target_folder_name}_{self.settings['converted_files_dir_name']}-{int(datetime.utcnow().timestamp())}"
        Path(converted_files_dir_abs).mkdir(parents=True, exist_ok=True)

        summary = {
            "skipped": 0,
            "converted": 0,
            "total": 0
        }

        for root, subdirs, files in walk(path):
            relative_root = root.replace(path, '')
            converted_files_subdir_abs = f"{converted_files_dir_abs}/{relative_root}"
            Path(converted_files_subdir_abs).mkdir(parents=True, exist_ok=True)
            self.save_print(
                f"INFO: created: {converted_files_subdir_abs}, path includes {len(files)} target files")

            if files and len(files) > 0:
                for file in files:
                    summary["total"] += 1
                    if self.is_file_type_correct(file):
                        self.save_print(f"\t* {file}")
                        self.convert_file_to_wav(
                            Path(f"{root}\\{file}"), converted_files_subdir_abs)
                        summary["converted"] += 1
                    else:
                        self.save_print(f"\t INFO: ignoring file {file}")
                        summary["skipped"] += 1
        
        with open(f'{converted_files_dir_abs}/summary.txt', 'w') as f:
            f.write(f"---------------SUMMARY----------------\n{summary}\n DATE: {datetime.utcnow()}\n-------------SUMMARY END--------------\n\n{self.output}")
        print(f'{converted_files_dir_abs}/summary.txt')

    def is_file_type_correct(self, file) -> bool:
        file_str = str(file)
        regex = re.findall(f'.*\.({self.settings["file_filter"]})', file_str)
        return (len(regex) == 1) and ('\n' not in file_str)

    def convert_file_to_wav(self, file_path: Path, target_path):
        flac_tmp_audio_data = AudioSegment.from_file(
            file_path, file_path.suffix[1:])

        new_file_name = ""
        old_file_info = mediainfo(str(file_path)).get('TAG', {})
        file_name_modifications = self.settings['file_name_modifications']

        if file_name_modifications['recreate_file_name_from_metadata'] and (old_file_info['artist'] and old_file_info['title']):
            new_file_name = f"{old_file_info['artist']} {file_name_modifications['title_separator']} {old_file_info['title']}"
        else:
            new_file_name = file_path.name.replace(
                file_path.suffix, '').strip()

        export_file_format = self.settings['export_format']
        self.save_print(f"\t\t-> {new_file_name}.{export_file_format}")

        complete_file_name = str(Path(f"{target_path}\\{new_file_name}.{export_file_format}").resolve())
        flac_tmp_audio_data.export(
            complete_file_name,
            format=export_file_format,
            tags=old_file_info
        )
        
        """ if (export_file_format == 'wav'):
            try:
                tags = EasyID3(complete_file_name)
            except ID3NoHeaderError:
                tags = mutagenFile(complete_file_name, easy=True)
                tags.add_tags()

            #for key in EasyID3.valid_keys.keys():
            #    print(key)

            tag_changes = False
            if old_file_info['title']:
                tags['title'] = TextFrame(encoding=3, text=[old_file_info['title']])
                tag_changes = True
            
            if old_file_info['artist']:
                tags['artist'] = TextFrame(encoding=3, text=[old_file_info['artist']])
                tag_changes = True

            if (tag_changes):
                tags.save(complete_file_name, v1=2)
                print(tags) """


        if self.settings['remove_converted_files']:
            # remove original file
            file_path.unlink()
