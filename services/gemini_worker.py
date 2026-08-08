from PySide6.QtCore import QThread, Signal
from services.gemini_service import ask_gemini


class GeminiWorker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        print("Worker started")

        try:
            print("Calling Gemini...")
            response = ask_gemini(self.prompt)

            print("Gemini replied:", response)

            self.finished.emit(response)

        except Exception as e:
            print("Worker Error:", e)
            self.error.emit(str(e))