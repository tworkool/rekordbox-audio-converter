import re
from time import time
from os import walk
from pathlib import Path
from pydub import AudioSegment
from pydub.utils import mediainfo


class AudioConverter:
    def __init__(self) -> None:
        self.settings = {
            "file_filter": 'flac|m4a',
            "export_format": 'wav',
            "converted_files_dir_name": 'converted',
            "remove_converted_files": False,
            "mirror_file_structure": True,
            "file_name_modifications": {
                "title_separator": '-',
                "custom_regex_replacement": None,
                "recreate_file_name_from_metadata": True
            }
        }

    def generate_file_tree(self, path, mirror_file_structure=True):
        root_path_parent = str(Path(path).parent.resolve())
        root_target_folder_name = path[len(root_path_parent)+1:]
        converted_files_dir_abs = f"{root_path_parent}/{root_target_folder_name}_{self.settings['converted_files_dir_name']}-{int(time())}"
        Path(converted_files_dir_abs).mkdir(parents=True, exist_ok=True)

        for root, subdirs, files in walk(path):
            relative_root = root.replace(path, '')
            converted_files_subdir_abs = f"{converted_files_dir_abs}/{relative_root}"
            Path(converted_files_subdir_abs).mkdir(parents=True, exist_ok=True)
            print(
                f"INFO: created: {converted_files_subdir_abs}, path includes {len(files)} target files")

            if files and len(files) > 0:
                for file in files:
                    if self.is_file_type_correct(file):
                        print(f"\t* {file}")
                        self.convert_file_to_wav(
                            Path(f"{root}\\{file}"), converted_files_subdir_abs)
                    else:
                        print(f"\t INFO: ignoring file {file}")

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
            new_file_name = file_path.name.replace(file_path.suffix, '').strip()

        print(f"\t\t-> {new_file_name}")

        complete_file_name = f"{target_path}\\{new_file_name}.{self.settings['export_format']}"
        flac_tmp_audio_data.export(
            complete_file_name,
            format=self.settings['export_format'],
            tags=old_file_info
        )

        if self.settings['remove_converted_files']:
            # remove original file
            file_path.unlink()
