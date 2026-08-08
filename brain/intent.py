class IntentDetector:

    def detect(self, message: str):

        message = message.lower()

        if "open" in message:
            return "open_app"

        if "remind" in message:
            return "create_reminder"

        if "pdf" in message:
            return "pdf"

        return "chat"