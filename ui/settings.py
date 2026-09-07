from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("⚙️ Settings")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
        """)

        layout.addWidget(title)

        placeholder = QLabel("Settings will be available here in a future update.")
        placeholder.setStyleSheet("""
            font-size: 15px;
            color: #bdbdbd;
            padding: 10px;
        """)

        layout.addWidget(placeholder)
        layout.addStretch()
