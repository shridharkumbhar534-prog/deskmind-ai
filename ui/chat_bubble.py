from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
)




class ChatBubble(QFrame):
    def __init__(self, message, sender):

        
        super().__init__()

        self.sender = sender

        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(14, 10, 14, 10)

        # Header (future avatar/name)
        if sender == "user":
            self.header = QLabel("You")
            self.header.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            
        else:
            self.header = QLabel("DeskMind AI")
            self.header.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout.addWidget(self.header)

        self.label = QLabel(message)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Footer (future time/buttons)
        self.footer = QLabel("")
        self.footer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout.addWidget(self.footer)

        self.setLayout(layout)

        self.setMaximumWidth(700)

        if self.sender == "user":

            self.setStyleSheet("""
                QFrame{
                    background-color:#4F46E5;
                    border-radius:16px;
                    padding:12px;
                }

                QLabel{
                color:white;
                font-size:14px;
                }
            """)

        else:

            self.setStyleSheet("""
                QFrame{
                    background-color:#353555;
                    border-radius:16px;
                    padding:12px;
                }

                QLabel{
                    color:white;
                    font-size:14px;
                }
            """)
    def set_message(self, message):
        self.label.setText(message)