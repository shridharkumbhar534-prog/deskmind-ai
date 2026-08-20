from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from brain.brain import Brain
from brain.errors import DeskMindError


class FileSearchWorker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, query, directory):
        super().__init__()
        self.query = query
        self.directory = directory
        self.brain = Brain()

    def run(self):
        try:
            response = self.brain.process(
                self.query,
                {
                "search_directory": self.directory
                }
            )

            self.finished.emit(str(response))

        except DeskMindError as error:
            self.error.emit(error.user_message)

        except Exception as error:
            print("File Search Worker Error:", error)
            self.error.emit(
                "Something went wrong while searching the files."
            )


class FileSearchPage(QWidget):

    def __init__(self):
        super().__init__()

        self.worker = None
        self.directory = None
        self.is_searching = False

        layout = QVBoxLayout(self)

        title = QLabel("📂 File Search")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
        """)

        layout.addWidget(title)

        self.select_button = QPushButton("Select Folder")
        self.select_button.clicked.connect(self.select_folder)

        layout.addWidget(self.select_button)

        self.folder_label = QLabel(
            "No folder selected."
        )

        layout.addWidget(self.folder_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search for text inside files..."
        )

        self.search_input.returnPressed.connect(
            self.search_files
        )

        layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.select_button.setStyleSheet("""
            QPushButton {
                background: #31344b;
                border: none;
                padding: 12px;
                text-align: left;
                border-radius: 8px;
                font-size: 15px;
            }

            QPushButton:hover {
                background: #4f46e5;
            }
        """)

        self.search_button.setStyleSheet("""
            QPushButton {
                background: #31344b;
                border: none;
                padding: 12px;
                text-align: left;
                border-radius: 8px;
                font-size: 15px;
            }
    
            QPushButton:hover {
                background: #4f46e5;
            }
        """)    
        
        
        
        
        
        
        
        
        
        self.search_button.clicked.connect(
            self.search_files
        )

        layout.addWidget(self.search_button)

        self.results_box = QTextEdit()
        self.results_box.setReadOnly(True)
        self.results_box.setPlaceholderText(
            "Search results will appear here..."
        )

        layout.addWidget(self.results_box)

    def select_folder(self):

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Folder"
        )

        if not directory:
            return

        self.directory = directory

        self.folder_label.setText(
            f"Selected: {directory}"
        )

        self.results_box.clear()

    def search_files(self):

        if self.is_searching:
            return

        if not self.directory:
            self.results_box.setPlainText(
                "Please select a folder first."
            )
            return

        query = self.search_input.text().strip()

        if not query:
            self.results_box.setPlainText(
                "Please enter something to search for."
            )
            return

        self.is_searching = True

        self.select_button.setEnabled(False)
        self.search_button.setEnabled(False)
        self.search_input.setEnabled(False)

        self.results_box.setPlainText(
            "Searching files..."
        )

        self.worker = FileSearchWorker(
            query,
            self.directory
        )

        self.worker.finished.connect(
            self.show_results
        )

        self.worker.error.connect(
            self.show_error
        )

        self.worker.start()

    def show_results(self, results):

        self.results_box.setPlainText(results)

        self.finish_search()

    def show_error(self, error):

        self.results_box.setPlainText(
            f"Error: {error}"
        )

        self.finish_search()

    def finish_search(self):

        self.is_searching = False

        self.select_button.setEnabled(True)
        self.search_button.setEnabled(True)
        self.search_input.setEnabled(True)