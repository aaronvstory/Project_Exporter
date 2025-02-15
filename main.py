import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ProjectExportTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project File Export Tool")
        self.setGeometry(100, 100, 500, 400)  # Adjust window size
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Load icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon-3sizes.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print("Icon file not found")

        # Load and set font
        font_path = os.path.join(os.path.dirname(__file__), "HarmonyOS_Sans_SC_Regular.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            font = QFont(font_family, 12)  # Increase base font size
            self.setFont(font)
        else:
            print("Font loading failed, using system default")

        # Create title
        title_label = QLabel("Project File Export Tool", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 15px 0;")
        self.layout.addWidget(title_label)

        # Create drag area
        self.drag_label = QLabel("Drag Project Folder Here", self)
        self.drag_label.setAlignment(Qt.AlignCenter)
        self.drag_label.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 30px;
                background-color: #f8f8f8;
                color: #555;
                font-size: 16px;
            }
        """
        )
        self.drag_label.setMinimumHeight(120)
        self.layout.addWidget(self.drag_label)

        # Create select folder button
        self.select_button = QPushButton("Select Folder", self)
        self.select_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )
        self.select_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_button)

        # Create checkbox
        self.export_tree_only_checkbox = QCheckBox("Export File Structure Only", self)
        self.export_tree_only_checkbox.setStyleSheet("font-size: 14px; margin-top: 10px;")
        self.layout.addWidget(self.export_tree_only_checkbox)

        # Create status edit
        self.status_edit = QLineEdit(self)
        self.status_edit.setReadOnly(True)
        self.status_edit.setPlaceholderText("Output status will be shown here")
        self.status_edit.setStyleSheet(
            """
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f9f9f9;
                font-size: 14px;
            }
        """
        )
        self.layout.addWidget(self.status_edit)

        self.central_widget.setLayout(self.layout)
        self.setAcceptDrops(True)

    def select_folder(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if dir_path:
            self.process_folder(dir_path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            dir_path = urls[0].toLocalFile()
            self.process_folder(dir_path)

    def process_folder(self, dir_path):
        if os.path.isdir(dir_path):
            self.status_edit.clear()
            project_name = os.path.basename(dir_path)
            if self.export_tree_only_checkbox.isChecked():
                output_file = os.path.join(dir_path, f"{project_name}_structure.txt")
            else:
                output_file = os.path.join(dir_path, f"{project_name}_structure_and_content.txt")
            self.generate_file_structure(dir_path, output_file)
            self.status_edit.setText(f"Export completed: {output_file}")

    def generate_file_structure(self, root_dir, output_file):
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(self.get_directory_tree(root_dir, output_file))
            if not self.export_tree_only_checkbox.isChecked():
                for dirpath, _, filenames in os.walk(root_dir):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        if filepath == output_file:
                            continue
                        normalized_path = os.path.normpath(filepath).replace("\\", "/")
                        f.write(f'\n<file path="{normalized_path}">\n')
                        try:
                            with open(filepath, "r", encoding="utf-8") as file:
                                content = file.read()
                                f.write(content + "\n")
                        except Exception as e:
                            f.write(f"Unable to read file content: {e}\n")
                        f.write("</file>\n")

    def get_directory_tree(self, root_dir, output_file):
        tree = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            level = dirpath.replace(root_dir, "").count(os.sep)
            indent = "│   " * (level)
            tree.append(f"{indent}├── {os.path.basename(dirpath)}/")
            subindent = "│   " * (level + 1)
            for f in filenames:
                if os.path.join(dirpath, f) == output_file:
                    continue
                tree.append(f"{subindent}├── {f}")
        return "\n".join(tree) + "\n"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set global font
    font_path = os.path.join(os.path.dirname(__file__), "HarmonyOS_Sans_SC_Regular.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family, 12)  # Increase base font size
        app.setFont(font)

    mainWin = ProjectExportTool()
    mainWin.show()
    sys.exit(app.exec_())
