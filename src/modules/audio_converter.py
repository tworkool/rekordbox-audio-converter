import re
from datetime import datetime
import subprocess
import os
from pathlib import Path
from pydub import AudioSegment
from pydub.utils import mediainfo
from modules.config import config

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
                "native_ffmpeg": config['NativeFFMPEG'],
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
            "errors": 0,
            "total": 0
        }

        for root, subdirs, files in os.walk(path):
            abs_root = Path(root)
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
                        if (self.settings['native_ffmpeg']):
                            converted_without_errors = self.convert_file_to_wav_with_ffmpeg(Path.joinpath(abs_root, file), converted_files_subdir_abs)
                        else:
                            converted_without_errors = self.convert_file_to_wav(Path.joinpath(abs_root, file), converted_files_subdir_abs)

                        if converted_without_errors:
                            summary["converted"] += 1
                        else:
                            summary["errors"] += 1
                    else:
                        self.save_print(f"\t INFO: ignoring file {file}")
                        summary["skipped"] += 1

        # out file save
        with open(f'{converted_files_dir_abs}/summary.txt', mode='w', encoding="utf-8") as f:
            f.write(
                f"---------------SUMMARY----------------\n{summary}\n DATE: {datetime.utcnow()}\n-------------SUMMARY END--------------\n\n{self.output}")
        print(f'{converted_files_dir_abs}/summary.txt')

    def is_file_type_correct(self, file) -> bool:
        file_str = str(file)
        regex = re.findall(f'.*\.({self.settings["file_filter"]})', file_str)
        return (len(regex) == 1) and ('\n' not in file_str)

    def convert_file_to_wav(self, file_path: Path, target_path):
        flac_tmp_audio_data = AudioSegment.from_file(
            file_path, file_path.suffix[1:])

        # filename manipulations
        old_file_info = mediainfo(str(file_path)).get('TAG', {})
        file_name_modifications = self.settings['file_name_modifications']

        if file_name_modifications['recreate_file_name_from_metadata']:
            try:
                new_file_name = f"{old_file_info['artist']} {file_name_modifications['title_separator']} {old_file_info['title']}"
            except KeyError:
                new_file_name = file_path.name.replace(
                    file_path.suffix, '').strip()
        else:
            new_file_name = file_path.name.replace(
                file_path.suffix, '').strip()

        # disallowed windows file character check
        for c in ['/', '\\', '?', ':', '*', '<', '>', '"', '|']:
            if c in new_file_name:
                new_file_name = new_file_name.replace(c, 'X')

        # export
        export_file_format = self.settings['export_format']
        self.save_print(f"\t\t-> {new_file_name}.{export_file_format}")

        try:
            complete_file_name = str(
                Path.joinpath(Path(target_path), f"{new_file_name}.{export_file_format}").resolve())
            flac_tmp_audio_data.export(
                complete_file_name,
                format=export_file_format,
                tags=old_file_info
            )
        except Exception:
            self.save_print(f"ERROR: Error while saving file {new_file_name}")
            return False

        if self.settings['remove_converted_files']:
            # remove original file
            file_path.unlink()

        return True

    def convert_file_to_wav_with_ffmpeg(self, file_path: Path, target_path):
        # filename manipulations
        old_file_info = mediainfo(str(file_path)).get('TAG', {})
        file_name_modifications = self.settings['file_name_modifications']

        if file_name_modifications['recreate_file_name_from_metadata']:
            try:
                new_file_name = f"{old_file_info['artist']} {file_name_modifications['title_separator']} {old_file_info['title']}"
            except KeyError:
                new_file_name = file_path.name.replace(
                    file_path.suffix, '').strip()
        else:
            new_file_name = file_path.name.replace(
                file_path.suffix, '').strip()

        # disallowed windows file character check
        for c in ['/', '\\', '?', ':', '*', '<', '>', '"', '|']:
            if c in new_file_name:
                new_file_name = new_file_name.replace(c, 'X')

        # export
        export_file_format = self.settings['export_format']
        self.save_print(f"\t\t-> {new_file_name}.{export_file_format}")

        complete_file_name = str(Path.joinpath(Path(target_path), f"{new_file_name}.{export_file_format}").resolve())
        # Use FFmpeg to convert the file, copying metadata from the input file
        # https://gist.github.com/tayvano/6e2d456a9897f55025e25035478a3a50
        # THOSE ARE THE SETTINGS PERFECT FOR REKORDBOX WAV: https://cdn.rekordbox.com/files/20210302175909/rekordbox6.4.2_introduction_de.pdf (p. 23)
        # -i file_input = input file 0
        # -map_metadata 0 = copy metadata
        # -c:a pcm_s24le = use all stream and convert to PCM 24 Bit Little Endian Codec (only one from PCM that works with WAV)
        # -ar 44100 = 44.1 Hz Frequency
        # -hide_banner -loglevel error -y = hide ffmpeg info, only output errors, overwrite all existing files without permission
        command = ['ffmpeg', '-i', file_path, '-map_metadata', '0', '-c:a', 'pcm_s24le', '-ar', '44100','-hide_banner', '-loglevel', 'error', '-y', complete_file_name]
        subprocess.call(command)

        # Check if the output file was created successfully
        if not os.path.isfile(complete_file_name):
            print("ERROR: Conversion failed")
            return False

        if self.settings['remove_converted_files']:
            # remove original file
            file_path.unlink()

        return True