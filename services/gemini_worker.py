import logging

from PySide6.QtCore import QThread, Signal
from brain.brain import Brain
from brain.errors import DeskMindError


logger = logging.getLogger(__name__)


class GeminiWorker(QThread):

    finished = Signal(str)
    error = Signal(str)

    def __init__(self, prompt, context=None):
        super().__init__()
        self.prompt = prompt
        self.context = context or {}
        self.brain = Brain()

    def run(self):
        print("Worker started")

        try:
            print("Processing request through Brain...")

            response = self.brain.process(
                self.prompt,
                self.context
            )

            print("Brain replied:", response)

            self.finished.emit(str(response))

        except DeskMindError as error:
            logger.warning("DeskMind request failed: %s", error)
            self.error.emit(error.user_message)
        except Exception:
            logger.exception("Unexpected error while processing DeskMind request")
            self.error.emit(
                "Something went wrong while processing your request. Please try again."
            )
