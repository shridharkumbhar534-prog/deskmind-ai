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
        # Reminders
        # -------------------------

        if re.search(r"\b(remind|reminder|reminders)\b", message):
            return "create_reminder"

        # -------------------------
        # PDF
        # -------------------------

        if re.search(r"\bpdf\b", message):
            return "pdf"

        # -------------------------
        # File search
        # -------------------------

        if re.search(r"\b(file search|search files|find files|search for files|find file)\b", message):
            return "file_search"

        # -------------------------
        # App launcher
        # -------------------------

        if re.match(
            r"^(open|launch|start)\s+(calculator|notepad|chrome|edge|explorer|cmd|powershell|calc|terminal|command prompt|file explorer|text editor|windows calculator)\b",
            message,
        ):
            return "open_app"

        # -------------------------
        # Default
        # -------------------------

        return "chat"
