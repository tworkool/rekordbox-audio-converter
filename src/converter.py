from pydub import AudioSegment
from os import walk
from pathlib import Path
from pydub.utils import mediainfo
from time import time
import re

current_path = Path(__file__).parent.resolve()


class AudioConverter:
    def __init__(self) -> None:
        self.file_filter = '*.flac'
        self.converted_files_dir_name = 'converted'

    def generate_file_tree(self, path, mirror_file_structure = True):
        """
        index = 0
        for path in Path(path).rglob(self.file_filter):
            index += 1
            file_path = f"{path.parent.resolve()}\\"
            print(index, path.name, file_path) 
        print(f"INFO: found {index} item(s) for {self.file_filter} files")
        """

        root_path_parent = str(Path(path).parent.resolve())
        root_target_folder_name = path[len(root_path_parent)+1:]
        converted_files_dir_abs = f"{root_path_parent}/{root_target_folder_name}_{self.converted_files_dir_name}-{int(time())}"
        Path(converted_files_dir_abs).mkdir(parents=True, exist_ok=True)

        for root, subdirs, files in walk(path):
            relative_root = root.replace(path, '')
            converted_files_subdir_abs = f"{converted_files_dir_abs}/{relative_root}"
            Path(converted_files_subdir_abs).mkdir(parents=True, exist_ok=True)
            print(
                f"INFO: created: {converted_files_subdir_abs}, path includes {len(files)} target files")

            if files and len(files) > 0:
                for file in files:
                    regex = re.search(r'.*\.flac', str(file))
                    if regex is None:
                        print(f"\t INFO: ignoring file {file}")
                    else:
                        print(f"\t* {file}")
                        self.convert_file_to_wav(
                            Path(f"{root}\\{file}"), converted_files_subdir_abs)

    def convert_file_to_wav(self, file_path: Path, target_path, remove_after=False):
        flac_tmp_audio_data = AudioSegment.from_file(
            file_path, file_path.suffix[1:])
        new_file_name = file_path.name.replace(file_path.suffix, '')

        complete_file_name = f"{target_path}\\{new_file_name}.wav"
        flac_tmp_audio_data.export(
            complete_file_name,
            format="wav",
            tags=mediainfo(f"{file_path}\\{file_path.name}").get('TAG', {})
        )

        if remove_after:
            # remove original file
            file_path.unlink()


""" def main():
    print(current_path)
    index = 0
    for path in Path('D:\\Audio\\backup\\Contents').rglob('*.flac'):
        index += 1
        file_path = f"{path.parent.resolve()}\\"
        print(index, path.name)
        flac_tmp_audio_data = AudioSegment.from_file(path, path.suffix[1:])

        new_file_name = path.name.replace(path.suffix, '')
        new_file_name_list = new_file_name.split('-')
        # remove leading song number
        if (len(new_file_name_list) > 0 and new_file_name_list[0].strip().isnumeric()):
            tmp_fl_name = ""
            for i in range(1, len(new_file_name_list)):
                tmp_fl_name += new_file_name_list[i]
                tmp_fl_name += ' - '
                tmp_fl_name.strip()
            new_file_name = tmp_fl_name

        # export wav file
        flac_tmp_audio_data.export(
            f"{file_path}{new_file_name}.wav",
            format="wav",
            tags=mediainfo(f"{file_path}\\{path.name}").get('TAG', {})
        )
        # remove flac file
        path.unlink()


if __name__ == '__main__':
    main() """
