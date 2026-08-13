from brain.intent import IntentDetector
from brain.dispatcher import Dispatcher
from brain.registry import CapabilityRegistry
from capabilities.chat import ChatCapability


class Brain:

    def __init__(self):
        self.intent_detector = IntentDetector()

        self.registry = CapabilityRegistry()
        self.registry.register("chat", ChatCapability)

        self.dispatcher = Dispatcher(self.registry)

    def process(self, message: str):

        intent = self.intent_detector.detect(message)

        return self.dispatcher.dispatch(
            intent,
            message
        )