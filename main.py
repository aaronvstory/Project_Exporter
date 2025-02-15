import json
import os
import sys
from datetime import datetime
from fnmatch import fnmatch
from typing import Dict, List, Optional, Set

from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QFont,
    QFontDatabase,
    QIcon,
    QStandardItem,
    QStandardItemModel,
)
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTextEdit,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


class FileItem(QStandardItem):
    ICON_MAP = {
        # Programming Languages
        '.py': 'text-x-python',
        '.js': 'text-javascript',
        '.ts': 'text-typescript',
        '.html': 'text-html',
        '.css': 'text-css',
        '.java': 'text-x-java',
        '.cpp': 'text-x-c++src',
        '.h': 'text-x-c++hdr',
        '.cs': 'text-x-csharp',
        '.go': 'text-x-go',
        '.rs': 'text-x-rust',
        # Documentation
        '.txt': 'text-plain',
        '.md': 'text-markdown',
        '.pdf': 'application-pdf',
        '.doc': 'x-office-document',
        '.docx': 'x-office-document',
        # Data formats
        '.json': 'application-json',
        '.xml': 'text-xml',
        '.yaml': 'text-yaml',
        '.yml': 'text-yaml',
        '.csv': 'text-csv',
        # Images
        '.jpg': 'image-jpeg',
        '.jpeg': 'image-jpeg',
        '.png': 'image-png',
        '.gif': 'image-gif',
        '.svg': 'image-svg+xml',
        # Config files
        '.conf': 'text-x-config',
        '.ini': 'text-x-config',
        '.env': 'text-x-config',
        '.cfg': 'text-x-config',
    }

    def __init__(self, text: str, is_dir: bool = False):
        super().__init__(text)
        self.is_dir = is_dir
        self.setIcon(self.get_icon())

    def get_icon(self) -> QIcon:
        if self.is_dir:
            return QIcon.fromTheme("folder")
        ext = os.path.splitext(self.text())[1].lower()
        theme = self.ICON_MAP.get(ext, "text-x-generic")
        return QIcon.fromTheme(theme)


class ProjectExportTool(QMainWindow):
    FONT_PATH = os.path.join(
        os.path.dirname(__file__),
        "HarmonyOS_Sans_SC_Regular.ttf"
    )

    DEFAULT_IGNORE_PATTERNS = {
        '.git',
        '.gitignore',
        '__pycache__',
        '*.pyc',
        '.DS_Store',
        'node_modules',
        '.idea',
        '.vscode',
        '*.log',
        '*.tmp',
        '*.temp',
        '*.swp',
        '~*',
        'Thumbs.db',
        'desktop.ini',
    }

    def __init__(self):
        super().__init__()
        self.current_dir: Optional[str] = None
        self.file_model = QStandardItemModel()
        self.ignore_patterns: Set[str] = self.DEFAULT_IGNORE_PATTERNS.copy()
        self.setWindowTitle("Project File Export Tool")
        self.setGeometry(100, 100, 1000, 600)
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
        font_id = QFontDatabase.addApplicationFont(self.FONT_PATH)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            font = QFont(font_family, 12)
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

        # Create checkboxes container
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_container)

        # Create structure-only checkbox
        self.structure_only_cb = QCheckBox("Export Structure Only")
        self.structure_only_cb.setToolTip(
            "Only export the directory structure, not file contents"
        )
        checkbox_layout.addWidget(self.structure_only_cb)

        # Create LLM optimization checkbox
        self.llm_optimize_cb = QCheckBox("Optimize for LLMs")
        self.llm_optimize_cb.setToolTip(
            "Enhances output for Large Language Models by:\n"
            "• Adding semantic file type detection\n"
            "• Including metadata (size, type, modification date)\n"
            "• Generating content previews\n"
            "• Adding structural markers for better parsing\n"
            "• Chunking large files for RAG systems"
        )
        checkbox_layout.addWidget(self.llm_optimize_cb)

        # Create ignore patterns checkbox
        self.ignore_defaults_cb = QCheckBox("Use Default Ignore Patterns")
        self.ignore_defaults_cb.setToolTip(
            "Ignore common files/folders like:\n"
            "• .git, __pycache__, node_modules\n"
            "• IDE folders (.vscode, .idea)\n"
            "• Temporary files (*.tmp, *.log)\n"
            "• System files (.DS_Store, Thumbs.db)"
        )
        self.ignore_defaults_cb.setChecked(True)
        self.ignore_defaults_cb.stateChanged.connect(self.toggle_ignore_patterns)
        checkbox_layout.addWidget(self.ignore_defaults_cb)

        # Custom ignore patterns input
        ignore_layout = QHBoxLayout()
        self.ignore_input = QLineEdit()
        self.ignore_input.setPlaceholderText("Add custom ignore pattern (e.g., *.txt)")
        self.ignore_add_btn = QPushButton("Add")
        self.ignore_add_btn.clicked.connect(self.add_ignore_pattern)
        ignore_layout.addWidget(self.ignore_input)
        ignore_layout.addWidget(self.ignore_add_btn)
        checkbox_layout.addLayout(ignore_layout)

        # Ignore patterns display
        self.ignore_display = QTextEdit()
        self.ignore_display.setReadOnly(True)
        self.ignore_display.setMaximumHeight(80)
        self.ignore_display.setPlaceholderText("Current ignore patterns will show here")
        self.update_ignore_display()
        checkbox_layout.addWidget(self.ignore_display)

        # Export format selection
        format_layout = QHBoxLayout()
        format_label = QLabel("Export Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Text", "Markdown", "JSON", "YAML"])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        checkbox_layout.addLayout(format_layout)

        # Export button
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_project)
        checkbox_layout.addWidget(self.export_button)

        self.layout.addWidget(checkbox_container)

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

        # Create main layout with splitter
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - File tree and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search files...")
        self.search_box.textChanged.connect(self.filter_files)
        left_layout.addWidget(self.search_box)

        # File tree
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.clicked.connect(self.on_file_clicked)
        left_layout.addWidget(self.file_tree)

        # Export controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)

        # Export format selection
        format_layout = QHBoxLayout()
        format_label = QLabel("Export Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Text", "Markdown", "JSON", "YAML"])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        controls_layout.addLayout(format_layout)

        # Structure-only checkbox
        self.structure_only_cb = QCheckBox("Export Structure Only")
        controls_layout.addWidget(self.structure_only_cb)

        # Export button
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_project)
        controls_layout.addWidget(self.export_button)

        left_layout.addWidget(controls_widget)

        # Right panel - Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        preview_label = QLabel("Preview")
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)

        right_layout.addWidget(preview_label)
        right_layout.addWidget(self.preview_text)

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        # Set initial splitter sizes
        splitter.setSizes([400, 600])

        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)

        # Enable drag and drop
        self.setAcceptDrops(True)

    def select_folder(self):
        title = "Select Project Folder"
        dir_path = QFileDialog.getExistingDirectory(self, title)
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

    def process_folder(self, dir_path: str):
        if not os.path.isdir(dir_path):
            return

        self.current_dir = dir_path
        self.populate_file_tree(dir_path)
        self.status_edit.setText(f"Loaded project: {dir_path}")

    def filter_files(self, text: str):
        if not self.current_dir:
            return

        self.file_model.clear()
        self.populate_file_tree(self.current_dir, text.lower())

    def on_file_clicked(self, index):
        item = self.file_model.itemFromIndex(index)
        if not item.is_dir:
            try:
                filepath = os.path.join(self.current_dir, item.text())
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.preview_text.setText(content)
            except Exception as e:
                self.preview_text.setText(f"Unable to read file: {str(e)}")

    def add_items_to_tree(self, items, parent, filter_text=""):
        """Helper method to add items to the tree model."""
        for name, is_dir in items:
            if not filter_text or filter_text in name.lower():
                item = FileItem(name, is_dir=is_dir)
                parent.appendRow(item)

    def toggle_ignore_patterns(self, state):
        if state == Qt.Checked:
            self.ignore_patterns = self.DEFAULT_IGNORE_PATTERNS.copy()
        else:
            self.ignore_patterns.clear()
        self.update_ignore_display()
        if self.current_dir:
            self.populate_file_tree(self.current_dir)

    def add_ignore_pattern(self):
        pattern = self.ignore_input.text().strip()
        if pattern:
            self.ignore_patterns.add(pattern)
            self.ignore_input.clear()
            self.update_ignore_display()
            if self.current_dir:
                self.populate_file_tree(self.current_dir)

    def update_ignore_display(self):
        self.ignore_display.setText("\n".join(sorted(self.ignore_patterns)))

    def should_ignore(self, path: str) -> bool:
        """Check if a path should be ignored based on patterns."""
        name = os.path.basename(path)
        return any(
            fnmatch(name, pattern) for pattern in self.ignore_patterns
        )

    def populate_file_tree(self, directory: str, filter_text: str = ""):
        """Populate the file tree with directory contents."""
        self.file_model.clear()
        root = self.file_model.invisibleRootItem()

        # Get all directories and files at the root level
        try:
            items = []
            with os.scandir(directory) as it:
                for entry in it:
                    if not self.should_ignore(entry.path):
                        items.append((entry.name, entry.is_dir()))

            # Sort directories first, then files
            dirs = [(n, d) for n, d in items if d]
            files = [(n, d) for n, d in items if not d]

            # Add to tree
            self.add_items_to_tree(sorted(dirs), root, filter_text)
            self.add_items_to_tree(sorted(files), root, filter_text)

        except OSError as e:
            print(f"Error reading directory: {e}")

    def export_project(self):
        if not self.current_dir:
            return

        export_format = self.format_combo.currentText().lower()
        extension = {"text": ".txt", "markdown": ".md", "json": ".json", "yaml": ".yaml"}.get(export_format, ".txt")

        project_name = os.path.basename(self.current_dir)
        filename = f"{project_name}_structure"
        if not self.structure_only_cb.isChecked():
            filename += "_and_content"
        filename += extension

        output_file = os.path.join(self.current_dir, filename)
        self.generate_file_structure(self.current_dir, output_file)
        self.status_edit.setText(f"Export completed: {output_file}")

    def write_file_content(self, f, filepath, is_markdown, root_dir):
        """Write the content of a single file to the output."""
        normalized_path = os.path.normpath(filepath).replace("\\", "/")
        rel_path = os.path.relpath(normalized_path, root_dir)

        if is_markdown:
            f.write(f"\n### File: `{rel_path}`\n\n```\n")
        else:
            f.write(f'\n<file path="{normalized_path}">\n')

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
                f.write(content + "\n")
        except Exception as e:
            f.write(f"Unable to read file content: {e}\n")

        if is_markdown:
            f.write("```\n")
        else:
            f.write("</file>\n")

    def write_file_content_llm(self, f, filepath: str, root_dir: str) -> Dict:
        """Write file content optimized for LLMs."""
        normalized_path = os.path.normpath(filepath).replace("\\", "/")
        rel_path = os.path.relpath(normalized_path, root_dir)

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()

                # Get file metadata
                stat = os.stat(filepath)
                ext = os.path.splitext(filepath)[1].lower()

                # Chunk content if it's large
                content_preview = content[:200]
                if len(content) > 200:
                    content_preview += "..."

                # Create semantic chunk with enhanced metadata
                chunk = {
                    "file_path": rel_path,
                    "file_type": ext[1:] if ext else "unknown",
                    "size_bytes": stat.st_size,
                    "last_modified": datetime.fromtimestamp(
                        stat.st_mtime
                    ).isoformat(),
                    "semantic_type": self._get_semantic_type(ext, content),
                    "content_preview": content_preview,
                    "content_size": len(content),
                    "content": content,
                    "metadata": {
                        "is_binary": not self._is_text_file(content),
                        "line_count": content.count('\n') + 1,
                        "extension": ext,
                    }
                }
                return chunk
        except Exception as e:
            return {
                "file_path": rel_path,
                "error": str(e),
                "content": None
            }

    def _is_text_file(self, content: str) -> bool:
        """Check if content appears to be text."""
        try:
            content.encode('utf-8')
            return True
        except UnicodeError:
            return False

    def _get_semantic_type(self, ext: str, content: str) -> str:
        """Determine semantic type of file content."""
        if ext in ['.py', '.js', '.java', '.cpp', '.cs']:
            return "source_code"
        elif ext in ['.md', '.txt', '.rst']:
            return "documentation"
        elif ext in ['.json', '.yaml', '.yml', '.xml']:
            return "data"
        elif ext in ['.jpg', '.png', '.gif', '.svg']:
            return "image"
        elif ext in ['.html', '.css']:
            return "web"
        elif ext in ['.conf', '.ini', '.env']:
            return "configuration"
        return "unknown"

    def generate_file_structure(self, root_dir: str, output_file: str):
        """Generate the file structure and content output."""
        is_markdown = output_file.endswith(".md")
        is_json = output_file.endswith(".json")
        is_yaml = output_file.endswith(".yaml")

        if is_json or is_yaml:
            self._generate_structured_output(
                root_dir,
                output_file,
                is_yaml
            )
            return

        with open(output_file, "w", encoding="utf-8") as f:
            if is_markdown:
                self.write_markdown_header(f, root_dir)

            f.write(self.get_directory_tree(root_dir, output_file))

            if is_markdown:
                f.write("```\n")

            if not self.structure_only_cb.isChecked():
                if is_markdown:
                    f.write("\n## File Contents\n\n")

                for dirpath, _, filenames in os.walk(root_dir):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        if self.should_ignore(filepath):
                            continue
                        if is_markdown:
                            chunk = self.write_file_content_llm(f, filepath, root_dir)
                            f.write(
                                f"\n### File: `{chunk['file_path']}`\n"
                                f"Type: {chunk['semantic_type']}\n\n"
                                "```\n"
                                f"{chunk['content']}\n"
                                "```\n"
                            )
                        else:
                            self.write_file_content(f, filepath, is_markdown, root_dir)

    def write_markdown_header(self, f, root_dir):
        """Write the Markdown header section."""
        f.write(f"# Project Structure: {os.path.basename(root_dir)}\n\n")
        f.write("## Directory Tree\n\n```\n")

    def get_directory_tree(self, root_dir, output_file):
        """Generate a tree view of the directory structure."""
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

    def _generate_structured_output(
        self,
        root_dir: str,
        output_file: str,
        is_yaml: bool = False
    ):
        """Generate structured output in JSON/YAML format."""
        structure = {
            "project_name": os.path.basename(root_dir),
            "export_date": datetime.now().isoformat(),
            "structure_only": self.structure_only_cb.isChecked(),
            "llm_optimized": self.llm_optimize_cb.isChecked(),
            "directory_tree": self.get_directory_tree(root_dir, output_file),
            "files": []
        }

        if not self.structure_only_cb.isChecked():
            for dirpath, _, filenames in os.walk(root_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if self.should_ignore(filepath):
                        continue
                    if filepath == output_file:
                        continue
                    if self.llm_optimize_cb.isChecked():
                        chunk = self.write_file_content_llm(
                            None, filepath, root_dir
                        )
                        structure["files"].append(chunk)
                    else:
                        try:
                            with open(filepath, "r", encoding="utf-8") as f:
                                content = f.read()
                                structure["files"].append({
                                    "file_path": os.path.relpath(
                                        filepath, root_dir
                                    ),
                                    "content": content
                                })
                        except Exception as e:
                            structure["files"].append({
                                "file_path": os.path.relpath(
                                    filepath, root_dir
                                ),
                                "error": str(e)
                            })

        with open(output_file, "w", encoding="utf-8") as f:
            if is_yaml:
                import yaml
                yaml.dump(structure, f, default_flow_style=False)
            else:
                json.dump(structure, f, indent=2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    font_id = QFontDatabase.addApplicationFont(ProjectExportTool.FONT_PATH)
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family, 12)
        app.setFont(font)
    mainWin = ProjectExportTool()
    mainWin.show()
    sys.exit(app.exec_())
