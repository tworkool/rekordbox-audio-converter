import re
from datetime import datetime
import subprocess
import os
from pathlib import Path, PureWindowsPath
from pydub import AudioSegment
from pydub.utils import mediainfo
from modules.config import config


class AudioConverter:
    def __init__(self) -> None:
        self.output = ""
        # outputs
        self.allowed_formats = ['aiff', 'wav']
        self.allowed_quality = ['normal', 'high', 'copy']
        try:
            self.settings = {
                "file_filter": config['FileFilter'],
                "export_format": config['ExportFormat'],
                "export_quality": config['ExportQuality'],
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
        
        self.ffmpeg_type_arguments = {
            "aiff_normal": {
                "codec": 'pcm_s16be',     # 16 Bit PCM Big Endian
                "sampling_rate": '44100', # 44.1 kHz
                "bit_rate": None,
                "custom": [],
            },
            "aiff_high": {
                "codec": 'pcm_s24be',     # 24 Bit PCM Big Endian
                "sampling_rate": '48000', # 48 kHz
                "bit_rate": None,
                "custom": [],
            },
            "aiff_copy": {
                "codec": 'copy',
                "sampling_rate": 'copy',
                "bit_rate": 'copy',
                "custom": [],
            },
            "wav_normal": {
                "codec": 'pcm_s16le',     # 16 Bit PCM Little Endian
                "sampling_rate": '44100', # 44.1 kHz
                "bit_rate": None,
                "custom": [],
            },
            "wav_high": {
                "codec": 'pcm_s24le',     # 24 Bit PCM Little Endian
                "sampling_rate": '48000', # 48 kHz
                "bit_rate": None,
                "custom": [],
            },
            "wav_copy": {
                "codec": 'copy',
                "sampling_rate": 'copy',
                "bit_rate": 'copy',
                "custom": [],
            },
        }

    # all ffmpeg arguments: https://gist.github.com/tayvano/6e2d456a9897f55025e25035478a3a50
    def generate_ffmpeg_arguments(self, in_audio: Path, out_audio: Path, in_cover: Path or None = None, quality='normal', verbose=False) -> list:
        in_format = in_audio.suffix.replace('.', '')
        out_format = out_audio.suffix.replace('.', '')
        if out_format not in self.allowed_formats:
            print(f"ERROR: format type {out_format} not allowed ({self.allowed_formats})")
        if quality not in self.allowed_quality:
            print(f"ERROR: quality {quality} not supported ({self.allowed_quality})")
        
        # global ffmpeg settings
        # -hide_banner -loglevel error -y = hide ffmpeg info, only output errors, overwrite all existing files without permission
        arg_list = ['ffmpeg', '-y']
        if verbose:
            arg_list.extend(['-hide_banner', '-loglevel', 'error'])
        # input stream 0: audio file
        arg_list.extend(['-i', f'"{in_audio}"'])

        if 'wav' != out_format and in_cover and in_cover.is_file():
            # input stream 1: image file, album cover
            arg_list.extend(['-i', f'"{in_cover}"'])
            # copy codec of stream 1: image file to output
            # arg_list.extend(['-c:1', 'copy'])
        
        # map metadata from in stream 0: in audio file to output
        arg_list.extend(['-map_metadata', '0'])

        ffmpeg_arg_preset_key = f"{out_format}_{quality}"
        ffmpeg_arg_preset = self.ffmpeg_type_arguments[ffmpeg_arg_preset_key]

        # audio codec, sampling rate and bit rate
        # as specified by rekordbox here [p. 23]: https://cdn.rekordbox.com/files/20210302175909/rekordbox6.4.2_introduction_de.pdf
        if ffmpeg_arg_preset['codec'] is not None:
            arg_list.extend(['-acodec', ffmpeg_arg_preset['codec']])
        if ffmpeg_arg_preset['sampling_rate'] is not None:
            arg_list.extend(['-ar', ffmpeg_arg_preset['sampling_rate']])
        if ffmpeg_arg_preset['bit_rate'] is not None:
            arg_list.extend(['-b:a', ffmpeg_arg_preset['bit_rate']])

        # specify ID3 v2 version, Rekordbox uses ID3 v2.4
        # write ID3 v2.4 tag (1=true)
        arg_list.extend(['-id3v2_version', '4', '-write_id3v2', '1'])
        # out file format (leads to constant bitrate)
        arg_list.extend(['-f', out_format])
        # output file
        arg_list.append(f'"{out_audio}"')

        arg_command = " ".join(arg_list)
        #return arg_list
        return arg_command

    def save_print(self, s):
        self.output += s
        self.output += "\n"
        print(s)

    def generate_file_tree(self, paths: list, mirror_file_structure=True, is_files=True):
        if len(paths) == 0:
            return
        
        if is_files:
            for _p in paths:
                root_path_parent = Path(_p).parent.resolve()
                root_target_folder_name = str(Path(_p).resolve())[len(str(root_path_parent))+1:]
                file = Path(_p).name
                self.save_print(f"\t* {file}")
                if self.is_file_type_correct(file):
                    converted_without_errors = self.convert_file_to_wav_with_ffmpeg(Path(_p), str(root_path_parent))
                else:
                    self.save_print(f"\t INFO: ignoring file {file}")
        else:
            directory = paths[0]
            root_path_parent = Path(directory).parent.resolve()
            root_target_folder_name = str(Path(directory).resolve())[len(str(root_path_parent))+1:]
            converted_files_dir_abs = f"{root_path_parent}/{root_target_folder_name}_{self.settings['converted_files_dir_name']}-{int(datetime.utcnow().timestamp())}"
            Path(converted_files_dir_abs).mkdir(parents=True, exist_ok=True)

            summary = {
                "skipped": 0,
                "converted": 0,
                "errors": 0,
                "total": 0,
            }

            for root, subdirs, files in os.walk(directory):
                abs_root = Path(root)
                relative_root = str(root).replace(str(directory), '')
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
                                converted_without_errors = self.convert_file_to_wav_with_ffmpeg(
                                    Path.joinpath(abs_root, file), converted_files_subdir_abs)
                            else:
                                converted_without_errors = self.convert_file_to_wav_with_pydub(
                                    Path.joinpath(abs_root, file), converted_files_subdir_abs)

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

    def fix_windows_file_name(self, file_name: str) -> str:
        # disallowed windows file character check
        _file_name = file_name
        for c in ['/', '\\', '?', ':', '*', '<', '>', '"', '|']:
            if c in file_name:
                _file_name = file_name.replace(c, 'X')
        return _file_name

    def improve_file_name_from_metadata(self, file_path: Path, template_format='$ARTIST - $TITLE'):
        file_info = mediainfo(str(file_path)).get('TAG', {})
        file_name = template_format

        template_key_value_list = [
            {
                'key': '$ARTIST',
                'value': 'artist',
            },
            {
                'key': '$TITLE',
                'value': 'title',
            },
        ]

        current_replace_key = ''
        try:
            for e in template_key_value_list:
                current_replace_key = e['key']
                current_replace_value = file_info[e['value']]
                if current_replace_key in file_name:
                    file_name = file_name.replace(current_replace_key, current_replace_value)
            return file_name
        except KeyError:
            print(f"ERROR: Could not improve file name from metadata due to missing tag {current_replace_key}")
            return False

    def convert_file_to_wav_with_ffmpeg(self, file_path: Path, target_path):
        # filename manipulations
        if self.settings['file_name_modifications']:
          modified_file_name = self.improve_file_name_from_metadata(file_path)
          new_file_name = modified_file_name or file_path.name.replace(file_path.suffix, '').strip()
        else:
          new_file_name = file_path.name.replace(file_path.suffix, '').strip()
        
        # fix windows file name
        new_file_name = self.fix_windows_file_name(new_file_name)

        # export
        export_file_format = self.settings['export_format']
        self.save_print(f"\t\t-> {new_file_name}.{export_file_format}")

        output_audio = Path.joinpath(Path(target_path), f"{new_file_name}.{export_file_format}").resolve()
        input_audio = Path(file_path).resolve()
        input_cover_image = Path.joinpath(Path(target_path), "cover.jpg").resolve()
        
        #command = ['ffmpeg', '-i', file_path, '-map_metadata', '0', '-c:a', 'pcm_s24le', '-ar', '44100', '-hide_banner', '-loglevel', 'error', '-y', complete_file_name]
        command = self.generate_ffmpeg_arguments(
            input_audio,
            output_audio,
            input_cover_image,
            quality='normal',
            verbose=True
        )
        subprocess.call(command, timeout=200)

        # Check if the output file was created successfully
        if not input_audio.is_file():
            print("ERROR: Conversion failed")
            return False

        if self.settings['remove_converted_files']:
            # remove original file
            file_path.unlink()

        return True
    
    def convert_file_to_wav_with_pydub(self, file_path: Path, target_path):
        flac_tmp_audio_data = AudioSegment.from_file(
            file_path, file_path.suffix[1:])

        old_file_info = mediainfo(str(file_path)).get('TAG', {})

        # filename manipulations
        if self.settings['file_name_modifications']:
          modified_file_name = self.improve_file_name_from_metadata(file_path)
          new_file_name = modified_file_name or file_path.name.replace(file_path.suffix, '').strip()
        else:
          new_file_name = file_path.name.replace(file_path.suffix, '').strip()
        
        # fix windows file name
        new_file_name = self.fix_windows_file_name(new_file_name)

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
