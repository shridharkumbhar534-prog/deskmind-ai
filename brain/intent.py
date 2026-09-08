import re


class IntentDetector:
    """Detect user intent from a natural-language message.

    Layer 1 -- deterministic commands (exact patterns).
    Layer 2 -- natural-language aliases (reliable keyword/phrase matches).
    Ambiguous messages fall through to ``"chat"``.
    """

    # App names the launcher knows about (kept in sync with AppLauncher).
    _APP_NAMES = (
        "calculator", "notepad", "chrome", "edge", "explorer",
        "cmd", "powershell", "calc", "terminal", "command prompt",
        "file explorer", "text editor", "windows calculator",
    )

    def detect(self, message: str):
        message = message.strip().lower()

        # ==================================================
        # Layer 1 -- deterministic commands
        # ==================================================

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
        # App launcher (deterministic)
        # -------------------------

        if re.match(
            r"^(open|launch|start)\s+(" + "|".join(self._APP_NAMES) + r")\b",
            message,
        ):
            return "open_app"

        # ==================================================
        # Layer 2 -- natural-language aliases
        # ==================================================

        # -------------------------
        # Notes (natural language)
        # -------------------------

        # "take a note: ...", "jot down a note: ...", "write down note: ..."
        if re.match(
            r"^(take|jot|write)\s+"
            r"(?:a\s+|down\s+)*"
            r"note\s*:",
            message
        ):
            return "notes"

        # "jot down: ...", "write down: ..." (without the word "note")
        if re.match(
            r"^(jot|write)\s+down\s*:",
            message
        ):
            return "notes"

        # "note: ..." (short form of create)
        if re.match(r"^note\s*:", message):
            return "notes"

        # "what are my notes", "show me my notes", "view my notes"
        if re.search(
            r"\b(what\s+are|show\s+me|view|display)\b.*\bnotes?\b",
            message
        ):
            return "notes"

        # "do i have any notes"
        if re.search(r"\b(do\s+i\s+have|any)\b.*\bnotes?\b", message):
            return "notes"

        # "remove note 3", "edit note 2"
        if re.match(
            r"^(remove|edit|change|modify)\s+note\s+\d+",
            message
        ):
            return "notes"

        # "get note 5", "view note 1"
        if re.match(
            r"^(get|view)\s+note\s+\d+$",
            message
        ):
            return "notes"

        # -------------------------
        # Reminders (natural language)
        # -------------------------

        # Deterministic keyword (already worked, kept here for ordering)
        if re.search(r"\b(remind|reminder|reminders)\b", message):
            return "create_reminder"

        # "set an alarm for ...", "schedule a reminder"
        if re.search(r"\b(set|schedule)\b.*\b(alarm|reminder)\b", message):
            return "create_reminder"

        # "don't let me forget ..."
        if re.match(r"^don'?t\s+let\s+me\s+forget\b", message):
            return "create_reminder"

        # "wake me up at ..."
        if re.match(r"^wake\s+me\s+up\b", message):
            return "create_reminder"

        # -------------------------
        # PDF (natural language)
        # -------------------------

        # Deterministic keyword
        if re.search(r"\bpdf\b", message):
            return "pdf"

        # "summarize the document", "ask about this document"
        if re.search(
            r"\b(summarize|summarise|ask\s+about|question\s+about|query)\b.*\b(document|file)\b",
            message
        ):
            return "pdf"

        # "what does this pdf say"
        if re.search(r"\bwhat\b.*\b(pdf|document)\b.*\b(say|contain)\b", message):
            return "pdf"

        # -------------------------
        # File search (natural language)
        # -------------------------

        # Deterministic phrases (already worked)
        if re.search(
            r"\b(file search|search files|find files|search for files|find file)\b",
            message
        ):
            return "file_search"

        # "search for ... in files", "look for ... in files"
        if re.search(
            r"\b(search|look\s+for|find)\b.*\bin\s+(my\s+)?files?\b",
            message
        ):
            return "file_search"

        # "find all files containing ..."
        if re.match(
            r"^find\s+all\s+files?\b",
            message
        ):
            return "file_search"

        # "grep for ...", "search the folder for ..."
        if re.match(
            r"^(grep|search\s+the\s+folder\s+for)\b",
            message
        ):
            return "file_search"

        # -------------------------
        # App launcher (natural language)
        # -------------------------

        # "can you open notepad", "please launch chrome"
        if re.search(
            r"\b(open|launch|start)\b.*\b(" + "|".join(self._APP_NAMES) + r")\b",
            message
        ):
            return "open_app"

        # "fire up calculator", "bring up notepad"
        if re.search(
            r"\b(fire\s+up|bring\s+up|run)\b.*\b(" + "|".join(self._APP_NAMES) + r")\b",
            message
        ):
            return "open_app"

        # "i need the calculator", "give me notepad"
        if re.search(
            r"\b(i\s+need|give\s+me|get\s+me)\b.*\b(" + "|".join(self._APP_NAMES) + r")\b",
            message
        ):
            return "open_app"

        # ==================================================
        # Default -- ambiguous, route to chat
        # ==================================================

        return "chat"
