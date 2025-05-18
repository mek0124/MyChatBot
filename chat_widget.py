from PySide6 import QtWidgets as qtw
from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from PySide6 import Qt
from datetime import datetime

import markdown


class ChatMessageWidget(qtw.QWidget):
    def __init__(self, message: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.setup_ui()

    def setup_ui(self):
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        # Add label for sender
        sender_label = qtw.QLabel("You" if self.is_user else "Mistral AI")
        sender_label.setAlignment(Qt.AlignLeft if self.is_user else Qt.AlignRight)
        sender_label.setStyleSheet(
            "font-weight: bold; color: " + ("#2c3e50" if self.is_user else "#16a085")
        )
        layout.addWidget(sender_label)

        # Create text edit for message
        self.text_edit = qtw.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Fixed)
        self.text_edit.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {'#ecf0f1' if self.is_user else '#f8f9fa'};
                border: 1px solid {'#bdc3c7' if self.is_user else '#d1d7dc'};
                border-radius: 8px;
                padding: 8px;
            }}
            """
        )

        # Process markdown and set content
        self.set_markdown_content(self.text_edit, self.message)
        
        # Add context menu for copy/save
        if not self.is_user:
            self.text_edit.setContextMenuPolicy(Qt.CustomContextMenu)
            self.text_edit.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.text_edit)

    def set_markdown_content(self, text_edit: qtw.QTextEdit, markdown_text: str):
        # Convert markdown to HTML
        html = markdown.markdown(markdown_text)
        
        # Create a document and set HTML
        doc = qtg.QTextDocument()
        doc.setHtml(html)
        
        # Set the document to the text edit
        text_edit.setDocument(doc)

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
