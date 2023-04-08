from PySide6 import QtCore, QtWidgets
from modules.audio_converter import AudioConverter
from modules.config import config


class ConverterPromptWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.audio_converter = AudioConverter()
        self.selected_items = []

        self.files_list = QtWidgets.QLabel("No File(s) or Directory Selected")
        self.convert_button = QtWidgets.QPushButton("Convert File(s)")
        self.file_button = QtWidgets.QPushButton("Select File(s)")
        self.dir_button = QtWidgets.QPushButton("Select Directory")
        self.mirror_checkbox = QtWidgets.QCheckBox("Mirror Folder Structure")
        self.dironly_checkbox = QtWidgets.QCheckBox("Only allow directory selection")
        # self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignCenter)
        self.metadata_naming_checkbox = QtWidgets.QCheckBox("Improve filename with metada info, if possible")
        self.allowed_formats_dropdown = QtWidgets.QComboBox()
        self.allowed_quality_dropdown = QtWidgets.QComboBox()

        self.mirror_checkbox.setChecked(True)
        self.dironly_checkbox.setChecked(True)
        self.metadata_naming_checkbox.setChecked(config['RecreateFileNameFromMetadata'])

        for i in self.audio_converter.allowed_formats:
            self.allowed_formats_dropdown.addItem(i)
        self.allowed_formats_dropdown.setCurrentText(config['ExportFormat'])

        for i in self.audio_converter.allowed_quality:
            self.allowed_quality_dropdown.addItem(i)
        self.allowed_quality_dropdown.setCurrentText(config['ExportQuality'])

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.files_list)
        self.layout.addWidget(self.metadata_naming_checkbox)
        self.layout.addWidget(self.dironly_checkbox)
        self.layout.addWidget(self.mirror_checkbox)
        self.layout.addWidget(self.allowed_formats_dropdown)
        self.layout.addWidget(self.allowed_quality_dropdown)
        self.layout.addWidget(self.file_button)
        self.layout.addWidget(self.dir_button)
        self.layout.addWidget(self.convert_button)

        self.convert_button.clicked.connect(self.convert_files)
        self.file_button.clicked.connect(self.get_files)
        self.dir_button.clicked.connect(self.get_dirs)
        self.dironly_checkbox.toggled.connect(self.dir_only_checkbox_changed)
        self.metadata_naming_checkbox.toggled.connect(self.metadata_naming_checkbox_changed)

        self.dir_only_checkbox_changed()
        self.set_selected_items()

    def convert_files(self):
        selected_item = self.selected_items[0]
        self.audio_converter.settings['export_format'] = self.allowed_formats_dropdown.currentText()
        self.audio_converter.settings['export_quality'] = self.allowed_quality_dropdown.currentText()
        is_mirroring_enabled = self.mirror_checkbox.checkState() == QtCore.Qt.CheckState.Checked
        self.audio_converter.generate_file_tree(selected_item, mirror_file_structure=is_mirroring_enabled)

    def metadata_naming_checkbox_changed(self):
        is_checked = self.metadata_naming_checkbox.checkState() == QtCore.Qt.CheckState.Checked
        p_val = self.audio_converter.settings['file_name_modifications']['recreate_file_name_from_metadata']
        self.audio_converter.settings['file_name_modifications']['recreate_file_name_from_metadata'] = not p_val

    def dir_only_checkbox_changed(self):
        is_checked = self.dironly_checkbox.checkState() == QtCore.Qt.CheckState.Checked
        self.mirror_checkbox.setDisabled(not is_checked)
        self.file_button.setVisible(not is_checked)
        self.dir_button.setVisible(is_checked)

    def set_selected_items(self, items: list = []):
        self.selected_items = items
        no_items_selected = len(items) == 0
        self.files_list.setText(
            "No File(s) or Directory Selected" if no_items_selected else str(items))
        self.convert_button.setDisabled(no_items_selected)

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
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        # dlg.setFilter(tr("Flac files (*.flac)"))
        filenames = []

        if dlg.exec():
            filenames = dlg.selectedFiles()
            self.set_selected_items(filenames)
            return filenames
