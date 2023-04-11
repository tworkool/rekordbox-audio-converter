from PySide6 import QtCore, QtWidgets, QtGui
from modules.audio_converter import AudioConverter
from modules.config import config, application_path, save_config
from pathlib import Path
import subprocess


class ConverterPromptWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        build_assets_path = Path.joinpath(
            application_path.parent, 'build_assets')
        logo_path = Path.joinpath(build_assets_path, 'favicon.ico')
        self.setWindowIcon(QtGui.QIcon(str(logo_path)))
        self.setWindowTitle("Tworkool's Rekordbox Audio Converter")

        self.audio_converter = AudioConverter()

        self.out_settings_groupbox = QtWidgets.QGroupBox("Output Settings")
        self.in_files_groupbox = QtWidgets.QGroupBox(
            "Input Files/Folders (double click to open)")

        self.__file_list = QtWidgets.QListWidget()
        self.convert_button = QtWidgets.QPushButton("Convert File(s)")
        self.file_button = QtWidgets.QPushButton("Select File(s)")
        self.dir_button = QtWidgets.QPushButton("Select Directory")
        self.save_config_button = QtWidgets.QPushButton("Save Config")
        self.remove_converted_files_checkbox = QtWidgets.QCheckBox(
            "Remove Original Files After Conversion")
        self.mirror_checkbox = QtWidgets.QCheckBox("Mirror Folder Structure")
        self.dironly_checkbox = QtWidgets.QCheckBox(
            "Only allow directory selection")
        self.metadata_naming_checkbox = QtWidgets.QCheckBox(
            "Improve filename with metada info, if possible")
        self.allowed_formats_dropdown = QtWidgets.QComboBox()
        self.allowed_quality_dropdown = QtWidgets.QComboBox()

        self.mirror_checkbox.setChecked(True)
        self.dironly_checkbox.setChecked(True)
        self.metadata_naming_checkbox.setChecked(
            config['RecreateFileNameFromMetadata'])
        self.remove_converted_files_checkbox.setChecked(
            config['RemoveConvertedFiles'])

        for i in self.audio_converter.allowed_formats:
            self.allowed_formats_dropdown.addItem(i)
        self.allowed_formats_dropdown.setCurrentText(config['ExportFormat'])

        for i in self.audio_converter.allowed_quality:
            self.allowed_quality_dropdown.addItem(i)
        self.allowed_quality_dropdown.setCurrentText(config['ExportQuality'])

        self.layout = QtWidgets.QVBoxLayout(self)
        self.in_files_groupbox_layout = QtWidgets.QVBoxLayout()
        # self.in_files_groupbox_layout.addStretch(1)
        self.in_files_groupbox_layout.addWidget(self.__file_list)
        self.in_files_groupbox.setLayout(self.in_files_groupbox_layout)
        self.layout.addWidget(self.in_files_groupbox)
        out_settings_groupbox_layout = QtWidgets.QVBoxLayout()
        out_settings_groupbox_layout.addWidget(self.metadata_naming_checkbox)
        out_settings_groupbox_layout.addWidget(
            self.remove_converted_files_checkbox)
        out_settings_groupbox_layout.addWidget(self.dironly_checkbox)
        out_settings_groupbox_layout.addWidget(self.mirror_checkbox)
        out_settings_groupbox_layout.addWidget(QtWidgets.QLabel(
            "Output Audio File Format", alignment=QtCore.Qt.AlignLeft))
        out_settings_groupbox_layout.addWidget(self.allowed_formats_dropdown)
        out_settings_groupbox_layout.addWidget(QtWidgets.QLabel(
            "Output Audio File Quality (normal=best compatibility)", alignment=QtCore.Qt.AlignLeft))
        out_settings_groupbox_layout.addWidget(self.allowed_quality_dropdown)
        out_settings_groupbox_layout.addWidget(self.save_config_button, alignment=QtCore.Qt.AlignRight)
        self.out_settings_groupbox.setLayout(out_settings_groupbox_layout)
        self.layout.addWidget(self.out_settings_groupbox)
        self.layout.addWidget(self.file_button)
        self.layout.addWidget(self.dir_button)
        self.layout.addWidget(self.convert_button)

        # data connections
        self.convert_button.clicked.connect(self.convert_files)
        self.file_button.clicked.connect(self.get_files)
        self.dir_button.clicked.connect(self.get_dirs)
        self.dironly_checkbox.toggled.connect(self.dir_only_checkbox_changed)
        self.__file_list.itemDoubleClicked.connect(self.directory_path_clicked)
        self.save_config_button.clicked.connect(self.save_settings)

        # settings connections
        self.metadata_naming_checkbox.toggled.connect(
            self.edit_settings_checkboxes)
        self.mirror_checkbox.toggled.connect(self.edit_settings_checkboxes)
        self.remove_converted_files_checkbox.toggled.connect(
            self.edit_settings_checkboxes)
        self.allowed_quality_dropdown.currentIndexChanged.connect(
            self.edit_settings_listwidgets)
        self.allowed_formats_dropdown.currentIndexChanged.connect(
            self.edit_settings_listwidgets)

        self.dir_only_checkbox_changed()
        self.set_selected_items()

    def edit_settings_checkboxes(self):
        config['RecreateFileNameFromMetadata'] = self.metadata_naming_checkbox.checkState(
        ) == QtCore.Qt.CheckState.Checked
        config['MirrorFileStructure'] = self.mirror_checkbox.checkState(
        ) == QtCore.Qt.CheckState.Checked
        config['RemoveConvertedFiles'] = self.remove_converted_files_checkbox.checkState(
        ) == QtCore.Qt.CheckState.Checked

    def edit_settings_listwidgets(self):
        config['ExportFormat'] = self.allowed_formats_dropdown.currentText()
        config['ExportQuality'] = self.allowed_quality_dropdown.currentText()

    def save_settings(self):
        save_config()

    def convert_files(self):
        selected_items = []
        for x in range(self.__file_list.count()):
            selected_items.append(Path(self.__file_list.item(x).text()))

        is_mirroring_enabled = self.mirror_checkbox.checkState() == QtCore.Qt.CheckState.Checked
        is_files = self.dironly_checkbox.checkState() != QtCore.Qt.CheckState.Checked
        self.audio_converter.generate_file_tree(
            selected_items, mirror_file_structure=is_mirroring_enabled, is_files=is_files)

    def directory_path_clicked(self, item: QtWidgets.QListWidgetItem):
        path = Path(item.text())
        if Path.is_dir(path):
            path = str(path.resolve())
        else:
            path = str(path.parent.resolve())
        subprocess.Popen(f'explorer "{path}"')

    def remove_converted_files_checkbox_changed(self):
        pass

    def dir_only_checkbox_changed(self):
        is_checked = self.dironly_checkbox.checkState() == QtCore.Qt.CheckState.Checked
        self.mirror_checkbox.setDisabled(not is_checked)
        self.file_button.setVisible(not is_checked)
        self.dir_button.setVisible(is_checked)

    def set_selected_items(self, items: list = []):
        no_items_selected = len(items) == 0
        self.convert_button.setDisabled(no_items_selected)

        self.__file_list.clear()
        if not no_items_selected:
            for i in items:
                self.__file_list.addItem(i)

    def get_dirs(self):
        dlg = QtWidgets.QFileDialog(self, 'Select Directory')
        dlg.setFileMode(QtWidgets.QFileDialog.Directory)
        filenames = []

        if dlg.exec():
            filenames = dlg.selectedFiles()
            self.set_selected_items(filenames)
            return filenames

    def get_files(self):
        dlg = QtWidgets.QFileDialog(self, 'Select File(s)')
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFiles)

        filter_raw = ""
        for fex in config['FileFilter'].split('|'):
            filter_raw += f"*.{fex} "
        filter_raw = filter_raw[:-1]

        file_filter = f"Audio Files ({filter_raw})"
        dlg.setNameFilters([file_filter, "Any (*)"])
        dlg.selectNameFilter(file_filter)

        filenames = []
        if dlg.exec():
            filenames = dlg.selectedFiles()
            self.set_selected_items(filenames)
            return filenames
