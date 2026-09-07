from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QMessageBox,
)

from database.connection import Database
from database.repositories import RemindersRepository
from ui.dashboard import Dashboard
from ui.ai_chat import AIChatPage
from ui.notes import NotesPage
from ui.pdf_page import PDFPage
from ui.file_serch import FileSearchPage
from ui.reminder import ReminderPage
from ui.settings import SettingsPage
from services.reminder.scheduler import ReminderScheduler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DeskMind AI")
        self.resize(1200, 700)

        # -------------------------
        # Shared application context
        # -------------------------

        self.context = {}
        self.database = Database()
        self.database.initialize()
        self.reminders = RemindersRepository(self.database)

        # -------------------------
        # Central widget
        # -------------------------

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        # -------------------------
        # Sidebar
        # -------------------------

        sidebar = QVBoxLayout()

        title = QLabel("DeskMind AI")
        title.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 15px;
        """)

        sidebar.addWidget(title)

        # -------------------------
        # Sidebar buttons
        # -------------------------

        dashboard_btn = QPushButton("🏠 Dashboard")
        chat_btn = QPushButton("🤖 AI Chat")
        notes_btn = QPushButton("📝 Notes")
        pdf_btn = QPushButton("📄 PDF Assistant")
        files_btn = QPushButton("📂 File Search")
        reminder_btn = QPushButton("⏰ Reminders")
        settings_btn = QPushButton("⚙️ Settings")

        self.sidebar_buttons = [
            dashboard_btn,
            chat_btn,
            notes_btn,
            pdf_btn,
            files_btn,
            reminder_btn,
            settings_btn,
        ]

        for btn in self.sidebar_buttons:
            btn.setMinimumHeight(45)
            btn.setCheckable(True)
            sidebar.addWidget(btn)

        sidebar.addStretch()
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(220)
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setStyleSheet("""
            #sidebar {
                background: #181828;
            }
        """)

        # -------------------------
        # Pages
        # -------------------------

        self.pages = QStackedWidget()

        self.dashboard = Dashboard()
        self.ai_chat = AIChatPage(self.context)
        self.notes = NotesPage(database=self.database, context=self.context)
        self.pdf_page = PDFPage(context=self.context)
        self.file_search_page = FileSearchPage(context=self.context)
        self.reminder_page = ReminderPage(database=self.database)
        self.settings_page = SettingsPage()

        self.reminder_scheduler = ReminderScheduler(database=self.database)
        self.reminder_scheduler.reminder_due.connect(
            self.show_reminder_notification
        )
        self.reminder_scheduler.start()

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.ai_chat)
        self.pages.addWidget(self.notes)
        self.pages.addWidget(self.pdf_page)
        self.pages.addWidget(self.file_search_page)
        self.pages.addWidget(self.reminder_page)
        self.pages.addWidget(self.settings_page)

        # -------------------------
        # Dashboard shortcut
        # -------------------------

        self.dashboard.ai_chat_requested.connect(
            lambda: self.navigate_to(self.ai_chat, chat_btn)
        )

        # -------------------------
        # Sidebar navigation
        # -------------------------

        dashboard_btn.clicked.connect(
            lambda: self.navigate_to(self.dashboard, dashboard_btn)
        )
        chat_btn.clicked.connect(
            lambda: self.navigate_to(self.ai_chat, chat_btn)
        )
        notes_btn.clicked.connect(
            lambda: self.navigate_to(self.notes, notes_btn)
        )
        pdf_btn.clicked.connect(
            lambda: self.navigate_to(self.pdf_page, pdf_btn)
        )
        files_btn.clicked.connect(
            lambda: self.navigate_to(self.file_search_page, files_btn)
        )
        reminder_btn.clicked.connect(
            lambda: self.navigate_to(self.reminder_page, reminder_btn)
        )
        settings_btn.clicked.connect(
            lambda: self.navigate_to(self.settings_page, settings_btn)
        )

        # -------------------------
        # Right side
        # -------------------------

        right_layout = QVBoxLayout()

        header = QLabel("DeskMind AI")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 15px;
            color: white;
        """)

        right_layout.addWidget(header)
        right_layout.addWidget(self.pages)

        # -------------------------
        # Main layout
        # -------------------------

        main_layout.addWidget(sidebar_widget)
        main_layout.addLayout(right_layout)

        # -------------------------
        # Global styling
        # -------------------------

        self.setStyleSheet("""
            QMainWindow {
                background: #1e1e2f;
            }

            QWidget {
                background: #1e1e2f;
                color: white;
            }

            QPushButton {
                background: #31344b;
                border: none;
                padding: 12px;
                text-align: left;
                border-radius: 8px;
                font-size: 15px;
            }

            QPushButton:hover {
                background: #4f46e5;
            }

            QPushButton:checked {
                background: #4f46e5;
                font-weight: bold;
            }
        """)

        # Start on dashboard
        self.navigate_to(self.dashboard, dashboard_btn)

    # -------------------------
    # Navigation helper
    # -------------------------

    def navigate_to(self, page, button):
        self.pages.setCurrentWidget(page)
        for btn in self.sidebar_buttons:
            btn.setChecked(False)
        button.setChecked(True)

    # -------------------------
    # Reminder notifications
    # -------------------------

    def show_reminder_notification(self, title, due_at):
        message = QMessageBox(self)

        message.setWindowTitle("⏰ Reminder")
        message.setIcon(QMessageBox.Icon.Information)

        message.setText(title)
        message.setInformativeText(f"Due: {due_at}")

        complete_button = message.addButton(
            "Complete",
            QMessageBox.ButtonRole.AcceptRole
        )

        message.addButton(
            "Dismiss",
            QMessageBox.ButtonRole.RejectRole
        )

        message.exec()

        if message.clickedButton() == complete_button:
            self.complete_reminder_from_notification(title, due_at)

    def complete_reminder_from_notification(self, title, due_at):
        reminders = self.reminders.list_active()

        for reminder in reminders:
            if (
                reminder["title"] == title
                and reminder["due_at"] == due_at
            ):
                self.reminders.complete(reminder["id"])
                break

        self.reminder_page.load_reminders()

    def closeEvent(self, event):
        self.reminder_scheduler.stop()
        event.accept()
