from email import message
import os
from ui.chat_bubble import ChatBubble
from PySide6.QtCore import QTimer
from services.gemini_worker import GeminiWorker
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QScrollArea,
    QFrame
)


class AIChatPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Chat History
        
        # Scroll Area
        self.scroll_area = QScrollArea()
        print(self.scroll_area.verticalScrollBar())
        self.scroll_area.setWidgetResizable(True)

# Container that will hold all chat bubbles
        self.chat_container = QWidget()

# Layout inside the container
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()

        self.chat_container.setLayout(self.chat_layout)

        self.scroll_area.setWidget(self.chat_container)


        # Input Box
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText(
            "Type your message..."
        )

        # Send Button
        self.send_button = QPushButton("Send")

        bottom = QHBoxLayout()

        bottom.addWidget(self.message_input)
        bottom.addWidget(self.send_button)

        layout.addWidget(self.scroll_area)
        layout.addLayout(bottom)

        self.setLayout(layout)

        # Chat state
        self.is_thinking = False

        # Connect button AFTER creating it
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)
    def add_message(self, message, sender):

        bubble = ChatBubble(message, sender)
        
        row = QHBoxLayout()

        if sender == "user":
            row.addStretch()
            row.addWidget(bubble)

        else:
            row.addWidget(bubble)
            row.addStretch()

        self.chat_layout.insertLayout(
            self.chat_layout.count() - 1,
            row
       )

        QTimer.singleShot(50, self.scroll_to_bottom)

        return bubble
    def send_message(self):

        if self.is_thinking:
            return
        
        message = self.message_input.text().strip()

        if not message:
            return
        self.add_message(message, "user")

        self.message_input.clear()

        self.thinking_bubble = self.add_message(
            "Thinking...",
            "ai"
        )
        


        self.is_thinking = True
        self.send_button.setEnabled(False)

    # Create worker
        self.worker = GeminiWorker(message)

    # Connect signals
        self.worker.finished.connect(self.show_response)
        self.worker.error.connect(self.show_error)

    # Start background thread
        self.worker.start()
    def show_response(self, response):
        self.thinking_bubble.set_message(response)
        self.is_thinking = False
        self.send_button.setEnabled(True)
        

        
    def show_error(self, error):

        self.is_thinking = False
        self.send_button.setEnabled(True)

        self.add_message(f"❌ Error: {error}", "ai")
    def scroll_to_bottom(self):
        self.chat_container.adjustSize()

        scrollbar = self.scroll_area.verticalScrollBar()

        print("Maximum:", scrollbar.maximum())
        print("Current:", scrollbar.value())

        scrollbar.setValue(scrollbar.maximum())