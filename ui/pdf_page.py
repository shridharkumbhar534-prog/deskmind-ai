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


class PDFWorker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, request, pdf_path):
        super().__init__()
        self.request = request
        self.pdf_path = pdf_path
        self.brain = Brain()

    def run(self):
        try:
            response = self.brain.dispatcher.dispatch(
                "pdf",
                self.request,
                {
                    "pdf_path": self.pdf_path
                }
            )

            self.finished.emit(str(response))

        except DeskMindError as error:
            self.error.emit(error.user_message)

        except Exception as error:
            print("PDF Worker Error:", error)
            self.error.emit(
                "Something went wrong while processing the PDF."
            )


class PDFPage(QWidget):

    def __init__(self):
        super().__init__()

        self.worker = None
        self.pdf_path = None
        self.is_processing = False

        layout = QVBoxLayout(self)

        title = QLabel("📄 PDF Assistant")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
        """)

        layout.addWidget(title)

        self.select_button = QPushButton("Select PDF")
        self.select_button.clicked.connect(
            self.select_pdf
        )

        layout.addWidget(self.select_button)

        self.file_label = QLabel(
            "No PDF selected."
        )

        layout.addWidget(self.file_label)

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText(
            "Ask something about the PDF..."
        )

        self.question_input.returnPressed.connect(
            self.ask_question
        )

        layout.addWidget(self.question_input)

        self.ask_button = QPushButton("Ask")
        self.ask_button.clicked.connect(
            self.ask_question
        )

        layout.addWidget(self.ask_button)

        self.answer_box = QTextEdit()
        self.answer_box.setReadOnly(True)
        self.answer_box.setPlaceholderText(
            "PDF answers will appear here..."
        )

        layout.addWidget(self.answer_box)

    def select_pdf(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        self.pdf_path = file_path

        self.file_label.setText(
            f"Selected: {file_path}"
        )

        self.answer_box.clear()

    def ask_question(self):

        if self.is_processing:
            return

        if not self.pdf_path:
            self.answer_box.setPlainText(
                "Please select a PDF first."
            )
            return

        question = (
            self.question_input.text().strip()
        )

        if not question:
            self.answer_box.setPlainText(
                "Please enter a question."
            )
            return

        self.is_processing = True

        self.select_button.setEnabled(False)
        self.ask_button.setEnabled(False)
        self.question_input.setEnabled(False)

        self.answer_box.setPlainText(
            "Reading PDF and generating answer..."
        )

        self.worker = PDFWorker(
            question,
            self.pdf_path
        )

        self.worker.finished.connect(
            self.show_answer
        )

        self.worker.error.connect(
            self.show_error
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.worker.error.connect(
            self.worker.deleteLater
        )

        self.worker.start()

    def show_answer(self, answer):

        self.answer_box.setPlainText(answer)

        self.finish_processing()

    def show_error(self, error):

        self.answer_box.setPlainText(
            f"Error: {error}"
        )

        self.finish_processing()

    def finish_processing(self):

        self.is_processing = False

        self.select_button.setEnabled(True)
        self.ask_button.setEnabled(True)
        self.question_input.setEnabled(True)