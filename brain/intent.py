import re


class IntentDetector:

    def detect(self, message: str):

        message = message.strip().lower()

        # -------------------------
        # Notes commands
        # -------------------------

        if re.match(
            r"^(create|save|add)\s+(a\s+)?note\s*:",
            message
        ):
            return "notes"

        if re.match(
            r"^(list|show)\s+notes?$",
            message
        ):
            return "notes"

        if re.match(
            r"^(read|show)\s+note\s+\d+$",
            message
        ):
            return "notes"

        if re.match(
            r"^update\s+note\s+\d+\s*:",
            message
        ):
            return "notes"

        if re.match(
            r"^delete\s+note\s+\d+$",
            message
        ):
            return "notes"

        # -------------------------
        # Other capabilities
        # -------------------------

        if re.search(r"\bopen\b", message):
            return "open_app"

        if re.search(r"\b(remind|reminder|reminders)\b", message):
            return "create_reminder"

        if re.search(r"\bpdf\b", message):
            return "pdf"

        # -------------------------
        # Default
        # -------------------------
        if re.search(r"\b(file search|search files|find files)\b", message):
            return "file_search"
        return "chat"