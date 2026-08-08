from brain.intent import IntentDetector


class Router:

    def __init__(self):
        self.intent = IntentDetector()

    def route(self, message: str):

        intent = self.intent.detect(message)

        return f"Detected Intent: {intent}"