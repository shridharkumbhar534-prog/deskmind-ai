"""Comprehensive tests for the IntentDetector.

Covers:
- All existing deterministic commands
- New natural-language aliases for every capability
- Ambiguous cases that must route to chat
"""

from brain.intent import IntentDetector


detector = IntentDetector()


def check(message, expected):
    result = detector.detect(message)
    assert result == expected, (
        f"Expected {expected!r} for {message!r}, got {result!r}"
    )


# ==================================================
# Existing deterministic commands
# ==================================================

def test_existing_notes_commands():
    check("create note: Hello world", "notes")
    check("save note: My note", "notes")
    check("add note: Another", "notes")
    check("create a note: With article", "notes")
    check("list notes", "notes")
    check("list note", "notes")
    check("show notes", "notes")
    check("show note", "notes")
    check("read note 1", "notes")
    check("show note 2", "notes")
    check("update note 3: Updated text", "notes")
    check("delete note 4", "notes")
    print("Existing notes commands passed.")


def test_existing_reminders():
    check("remind me: Submit assignment | 2026-08-21 18:00", "create_reminder")
    check("reminder: buy milk | 2026-09-01 09:00", "create_reminder")
    check("reminders", "create_reminder")
    check("set a reminder for tomorrow", "create_reminder")
    print("Existing reminder commands passed.")


def test_existing_pdf():
    check("summarize this pdf", "pdf")
    check("what does the pdf say", "pdf")
    check("pdf assistant", "pdf")
    print("Existing PDF commands passed.")


def test_existing_file_search():
    check("file search", "file_search")
    check("search files for test", "file_search")
    check("find files containing hello", "file_search")
    check("search for files in project", "file_search")
    check("find file named config", "file_search")
    print("Existing file search commands passed.")


def test_existing_app_launcher():
    check("open calculator", "open_app")
    check("launch notepad", "open_app")
    check("start chrome", "open_app")
    check("open edge", "open_app")
    check("launch explorer", "open_app")
    check("start cmd", "open_app")
    check("open powershell", "open_app")
    check("launch calc", "open_app")
    check("start terminal", "open_app")
    check("open command prompt", "open_app")
    check("launch file explorer", "open_app")
    check("start text editor", "open_app")
    check("open windows calculator", "open_app")
    print("Existing app launcher commands passed.")


def test_existing_chat_default():
    check("hello there", "chat")
    check("what is the weather today", "chat")
    check("tell me a joke", "chat")
    print("Existing chat default passed.")


# ==================================================
# New natural-language aliases -- Notes
# ==================================================

def test_nl_notes_create():
    check("take a note: buy groceries", "notes")
    check("jot down: meeting at 3pm", "notes")
    check("write down: call mom", "notes")
    check("take note: quick reminder", "notes")
    check("note: short form note", "notes")
    print("Natural-language notes create passed.")


def test_nl_notes_list():
    check("what are my notes", "notes")
    check("show me my notes", "notes")
    check("view my notes", "notes")
    check("display my notes", "notes")
    check("do i have any notes", "notes")
    check("any notes?", "notes")
    print("Natural-language notes list passed.")


def test_nl_notes_modify():
    check("remove note 3", "notes")
    check("edit note 2", "notes")
    check("change note 1", "notes")
    check("modify note 5", "notes")
    check("get note 7", "notes")
    check("view note 1", "notes")
    print("Natural-language notes modify passed.")


# ==================================================
# New natural-language aliases -- Reminders
# ==================================================

def test_nl_reminders():
    check("set an alarm for 7am", "create_reminder")
    check("schedule a reminder for tomorrow", "create_reminder")
    check("don't let me forget the meeting", "create_reminder")
    check("dont let me forget to call mom", "create_reminder")
    check("wake me up at 6am", "create_reminder")
    check("remind me to submit the assignment", "create_reminder")
    print("Natural-language reminders passed.")


# ==================================================
# New natural-language aliases -- PDF
# ==================================================

def test_nl_pdf():
    check("summarize the document", "pdf")
    check("summarise this document", "pdf")
    check("ask about this document", "pdf")
    check("question about the file", "pdf")
    check("query the document", "pdf")
    check("what does this pdf say", "pdf")
    check("what does the document contain", "pdf")
    print("Natural-language PDF passed.")


# ==================================================
# New natural-language aliases -- File Search
# ==================================================

def test_nl_file_search():
    check("search for hello in files", "file_search")
    check("look for config in my files", "file_search")
    check("find all files containing test", "file_search")
    check("grep for import", "file_search")
    check("search the folder for readme", "file_search")
    print("Natural-language file search passed.")


# ==================================================
# New natural-language aliases -- App Launcher
# ==================================================

def test_nl_app_launcher():
    check("can you open notepad", "open_app")
    check("please launch chrome", "open_app")
    check("could you start calculator", "open_app")
    check("fire up calculator", "open_app")
    check("bring up notepad", "open_app")
    check("run notepad", "open_app")
    check("i need the calculator", "open_app")
    check("give me notepad", "open_app")
    check("get me chrome", "open_app")
    print("Natural-language app launcher passed.")


# ==================================================
# Ambiguous cases -- must route to chat
# ==================================================

def test_ambiguous_cases():
    # "open the note" is ambiguous -- could be notes or app launcher
    check("open the note", "chat")
    # "find" alone is too vague
    check("find something", "chat")
    # "search" alone is too vague
    check("search", "chat")
    # "note" alone is too vague
    check("note", "chat")
    # "file" alone is too vague
    check("file", "chat")
    # "document" alone is too vague
    check("document", "chat")
    # "open" alone is too vague
    check("open", "chat")
    # "open spotify" -- not a supported app
    check("open spotify", "chat")
    # "open the door" -- not a supported app
    check("open the door", "chat")
    # General conversation
    check("how are you today", "chat")
    check("what can you do", "chat")
    check("help me with my homework", "chat")
    check("write me an essay about cats", "chat")
    print("Ambiguous cases passed.")


# ==================================================
# Case insensitivity
# ==================================================

def test_case_insensitivity():
    check("Create Note: Hello", "notes")
    check("LIST NOTES", "notes")
    check("Open Calculator", "open_app")
    check("REMIND ME: test | 2026-01-01 12:00", "create_reminder")
    check("Summarize This PDF", "pdf")
    check("File Search", "file_search")
    print("Case insensitivity passed.")


# ==================================================
# Whitespace handling
# ==================================================

def test_whitespace():
    check("   create note: test   ", "notes")
    check("  open  calculator  ", "open_app")
    check("   hello   ", "chat")
    print("Whitespace handling passed.")


def main():
    test_existing_notes_commands()
    test_existing_reminders()
    test_existing_pdf()
    test_existing_file_search()
    test_existing_app_launcher()
    test_existing_chat_default()
    test_nl_notes_create()
    test_nl_notes_list()
    test_nl_notes_modify()
    test_nl_reminders()
    test_nl_pdf()
    test_nl_file_search()
    test_nl_app_launcher()
    test_ambiguous_cases()
    test_case_insensitivity()
    test_whitespace()
    print("\nAll intent detector tests passed.")


if __name__ == "__main__":
    main()
