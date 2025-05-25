from PySide6 import QtWidgets as qtw
from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from datetime import datetime
import markdown
import os

class ChatMessageWidget(qtw.QWidget):
    def __init__(self, message: str, is_user: bool, attachments=None, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.attachments = attachments or []
        self.setup_ui()

    def setup_ui(self):
        layout = qtw.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        self.setLayout(layout)

        # Add attachments row if there are any
        if self.attachments:
            attachments_layout = qtw.QHBoxLayout()
            attachments_layout.setContentsMargins(0, 0, 0, 5)
            attachments_layout.setSpacing(5)
            
            for attachment in self.attachments:
                icon = self.create_attachment_icon(attachment)
                attachments_layout.addWidget(icon)
            
            # Add stretch to push icons to the left for user messages
            if self.is_user:
                attachments_layout.addStretch()
            
            layout.addLayout(attachments_layout)

        sender_label = qtw.QLabel("You" if self.is_user else "Mistral AI")
        sender_label.setAlignment(qtc.Qt.AlignLeft if self.is_user else qtc.Qt.AlignRight)
        sender_label.setStyleSheet(
            """
            font-weight: bold;
            font-size: 12px;
            color: %s;
            margin-bottom: 2px;
            """ % ("rgb(177,203,231)" if self.is_user else "rgb(94,147,207)")
        )
        layout.addWidget(sender_label)

        self.text_edit = qtw.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Preferred)
        self.text_edit.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.text_edit.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.text_edit.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {'rgb(0,38,80)' if self.is_user else 'rgb(0,22,45)'};
                border: 1px solid {'rgb(33,84,141)' if self.is_user else 'rgb(33,84,141)'};
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
                margin-bottom: 8px;
                color: rgb(177,203,231);
            }}
            """
        )

        if self.message:
            self.set_markdown_content(self.text_edit, self.message)
        layout.addWidget(self.text_edit)

        if self.message:
            self.adjust_height()

        if not self.is_user and self.message:
            button_layout = qtw.QHBoxLayout()
            button_layout.setAlignment(qtc.Qt.AlignRight)
            button_layout.setSpacing(5)
            
            self.copy_button = qtw.QPushButton("Copy")
            self.copy_button.setStyleSheet("""
                QPushButton {
                    padding: 4px 8px;
                    border: 1px solid rgb(33,84,141);
                    border-radius: 4px;
                    background-color: rgb(0,38,80);
                    font-size: 12px;
                    color: rgb(177,203,231);
                }
                QPushButton:hover {
                    background-color: rgb(94,147,207);
                }
            """)
            self.copy_button.clicked.connect(self.copy_markdown)
            button_layout.addWidget(self.copy_button)
            
            self.save_md_button = qtw.QPushButton("Save MD")
            self.save_md_button.setStyleSheet("""
                QPushButton {
                    padding: 4px 8px;
                    border: 1px solid rgb(33,84,141);
                    border-radius: 4px;
                    background-color: rgb(0,38,80);
                    font-size: 12px;
                    color: rgb(177,203,231);
                }
                QPushButton:hover {
                    background-color: rgb(94,147,207);
                }
            """)
            self.save_md_button.clicked.connect(lambda: self.save_markdown('md'))
            button_layout.addWidget(self.save_md_button)
            
            self.save_txt_button = qtw.QPushButton("Save TXT")
            self.save_txt_button.setStyleSheet("""
                QPushButton {
                    padding: 4px 8px;
                    border: 1px solid rgb(33,84,141);
                    border-radius: 4px;
                    background-color: rgb(0,38,80);
                    font-size: 12px;
                    color: rgb(177,203,231);
                }
                QPushButton:hover {
                    background-color: rgb(94,147,207);
                }
            """)
            self.save_txt_button.clicked.connect(lambda: self.save_markdown('txt'))
            button_layout.addWidget(self.save_txt_button)
            
            layout.addLayout(button_layout)

        if not self.is_user and self.message:
            self.text_edit.setContextMenuPolicy(qtc.Qt.CustomContextMenu)
            self.text_edit.customContextMenuRequested.connect(self.show_context_menu)

    def create_attachment_icon(self, file_path):
        icon = qtw.QPushButton()
        icon.setFlat(True)
        icon.setFixedSize(32, 32)
        icon.setProperty("class", "attachment-icon")
        
        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_name)[1].lower()
        
        # Set icon based on file type
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            pixmap = qtg.QPixmap(file_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(28, 28, qtc.Qt.KeepAspectRatio, qtc.Qt.SmoothTransformation)
                icon.setIcon(qtg.QIcon(pixmap))
            else:
                icon.setIcon(self.style().standardIcon(qtw.QStyle.SP_FileIcon))
            icon.setToolTip(f"Image: {file_name}")
        else:
            icon.setIcon(self.style().standardIcon(qtw.QStyle.SP_FileIcon))
            icon.setToolTip(f"File: {file_name}")
        
        icon.clicked.connect(lambda: self.open_attachment(file_path))
        return icon

    def open_attachment(self, file_path):
        if os.path.exists(file_path):
            qtg.QDesktopServices.openUrl(qtc.QUrl.fromLocalFile(file_path))

    def adjust_height(self):
        doc = self.text_edit.document()
        doc.setTextWidth(self.text_edit.viewport().width())
        height = int(doc.size().height()) + 30
        self.text_edit.setMinimumHeight(min(height, 500))
        self.text_edit.setMaximumHeight(min(height, 500))

    def set_markdown_content(self, text_edit: qtw.QTextEdit, markdown_text: str):
        html = markdown.markdown(markdown_text)
        doc = qtg.QTextDocument()
        doc.setHtml(html)
        text_edit.setDocument(doc)
        qtc.QTimer.singleShot(100, self.adjust_height)

    def show_context_menu(self, position):
        menu = qtw.QMenu(self)
        
        copy_action = qtg.QAction("Copy Markdown", self)
        copy_action.triggered.connect(self.copy_markdown)
        menu.addAction(copy_action)
        
        save_md_action = qtg.QAction("Save as Markdown (.md)", self)
        save_md_action.triggered.connect(lambda: self.save_markdown('md'))
        menu.addAction(save_md_action)
        
        save_txt_action = qtg.QAction("Save as Text (.txt)", self)
        save_txt_action.triggered.connect(lambda: self.save_markdown('txt'))
        menu.addAction(save_txt_action)
        
        menu.exec_(self.text_edit.mapToGlobal(position))

    def copy_markdown(self):
        clipboard = qtw.QApplication.clipboard()
        mime_data = qtc.QMimeData()
        mime_data.setText(self.message)
        clipboard.setMimeData(mime_data)
        qtw.QMessageBox.information(self, "Copied", "Markdown content copied to clipboard!")

    def save_markdown(self, extension: str):
        default_name = f"mistral_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
        file_path, _ = qtw.QFileDialog.getSaveFileName(
            self, 
            "Save Markdown Content", 
            default_name, 
            f"Markdown Files (*.{extension});;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.message)
                qtw.QMessageBox.information(self, "Saved", f"Content saved successfully to {file_path}")
            except Exception as e:
                qtw.QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def resizeEvent(self, event):
        if self.message:
            self.adjust_height()
        super().resizeEvent(event)