from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
)
from PySide6.QtWidgets import QMessageBox

from database.connection import Database
from database.repositories import RemindersRepository
from ui.dashboard import Dashboard
from ui.ai_chat import AIChatPage
from ui.notes import NotesPage
from ui.pdf_page import PDFPage
from ui.file_serch import FileSearchPage
from ui.reminder import ReminderPage
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
        # Reminder database access
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

        buttons = [
            dashboard_btn,
            chat_btn,
            notes_btn,
            pdf_btn,
            files_btn,
            reminder_btn,
            settings_btn,
        ]

        for btn in buttons:
            btn.setMinimumHeight(45)
            sidebar.addWidget(btn)

        sidebar.addStretch()
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(220)
        # -------------------------
        # Pages
        # -------------------------
        self.pages = QStackedWidget()

        self.dashboard = Dashboard()
        self.ai_chat = AIChatPage(self.context)
        self.notes = NotesPage(context=self.context)
        self.pdf_page = PDFPage()
        self.file_search_page = FileSearchPage()
        self.reminder_page = ReminderPage()
        self.reminder_scheduler = ReminderScheduler()
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

        # -------------------------
        # Dashboard shortcut
        # -------------------------

        self.dashboard.ai_chat_requested.connect(
            lambda: self.pages.setCurrentWidget(self.ai_chat)
        )

        # -------------------------
        # Sidebar navigation
        # -------------------------

        dashboard_btn.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.dashboard)
        )

        chat_btn.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.ai_chat)
        )

        notes_btn.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.notes)
        )

        pdf_btn.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.pdf_page)
        )

        files_btn.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.file_search_page)
        )

        reminder_btn.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.reminder_page)
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
        """)
        
        
    def show_reminder_notification(self, title, due_at):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "⏰ Reminder",
            f"{title}\n\nDue: {due_at}",
        )
        
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