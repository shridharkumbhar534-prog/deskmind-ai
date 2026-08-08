from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QPushButton
)

from PySide6.QtCore import Qt, Signal


class Dashboard(QWidget):
    ai_chat_requested = Signal()
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        # Welcome Text
        welcome = QLabel("👋 Welcome to DeskMind AI")
        welcome.setStyleSheet("""
            font-size:30px;
            font-weight:bold;
            color:white;
            padding:10px;
        """)

        main_layout.addWidget(welcome)

        subtitle = QLabel("Choose a feature to get started")
        subtitle.setStyleSheet("""
            font-size:16px;
            color:#bdbdbd;
            padding-left:10px;
        """)

        main_layout.addWidget(subtitle)

        # Cards
        grid = QGridLayout()

        cards = [
            "🤖 AI Chat",
            "📄 PDF Assistant",
            "📝 Notes",
            "📂 File Search",
            "🚀 App Launcher",
            "⏰ Reminder",
            "⚙️ Settings"
        ]

        row = 0
        col = 0

        for text in cards:

            card = QPushButton(text)
            if text == "🤖 AI Chat":
                card.clicked.connect(self.ai_chat_requested.emit)

            card.setMinimumSize(250,120)

            card.setStyleSheet("""
                QPushButton{
                    background:#31344b;
                    border:none;
                    border-radius:15px;
                    font-size:18px;
                    font-weight:bold;
                    text-align:left;
                    padding:20px;
                }

                QPushButton:hover{
                    background:#4f46e5;
                }
            """)

            grid.addWidget(card,row,col)

            col += 1

            if col == 2:
                col = 0
                row += 1

        main_layout.addSpacing(20)

        main_layout.addLayout(grid)

        main_layout.addStretch()

        self.setLayout(main_layout)