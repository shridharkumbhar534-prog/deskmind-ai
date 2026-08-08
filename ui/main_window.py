from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget
)

from ui.dashboard import Dashboard
from ui.ai_chat import AIChatPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DeskMind AI")
        self.resize(1200, 700)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        # Sidebar
        sidebar = QVBoxLayout()

        title = QLabel("DeskMind AI")
        title.setStyleSheet("""
            color:white;
            font-size:20px;
            font-weight:bold;
            padding:15px;
        """)

        sidebar.addWidget(title)

        dashboard_btn = QPushButton("🏠 Dashboard")
        chat_btn = QPushButton("🤖 AI Chat")
        pdf_btn = QPushButton("📄 PDF Assistant")
        notes_btn = QPushButton("📝 Notes")
        files_btn = QPushButton("📂 File Search")
        apps_btn = QPushButton("🚀 App Launcher")
        reminder_btn = QPushButton("⏰ Reminder")
        settings_btn = QPushButton("⚙️ Settings")

        for btn in [dashboard_btn, chat_btn, pdf_btn, notes_btn, files_btn, apps_btn, reminder_btn, settings_btn]:
            btn.setMinimumHeight(45)
            sidebar.addWidget(btn)

        sidebar.addStretch()

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(220)

        # Pages
        # Pages
        self.pages = QStackedWidget()

        self.dashboard = Dashboard()
        
        self.dashboard.ai_chat_requested.connect(
            lambda: self.pages.setCurrentWidget(self.ai_chat)
)
        self.ai_chat = AIChatPage()

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.ai_chat)

        # Right Side
        right_layout = QVBoxLayout()

        header = QLabel("DeskMind AI")
        header.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
            padding:15px;
            color:white;
        """)

        right_layout.addWidget(header)
        right_layout.addWidget(self.pages)

        main_layout.addWidget(sidebar_widget)
        main_layout.addLayout(right_layout)
        dashboard_btn.clicked.connect(
        lambda: self.pages.setCurrentWidget(self.dashboard)
        )

        chat_btn.clicked.connect(
        lambda: self.pages.setCurrentWidget(self.ai_chat)
        )
        self.setStyleSheet("""
            QMainWindow{
                background:#1e1e2f;
            }

            QWidget{
                background:#1e1e2f;
                color:white;
            }

            QPushButton{
                background:#31344b;
                border:none;
                padding:12px;
                text-align:left;
                border-radius:8px;
                font-size:15px;
            }

            QPushButton:hover{
                background:#4f46e5;
            }
        """)