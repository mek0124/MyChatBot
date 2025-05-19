import os
from PySide6 import QtCore as qtc
from mistralai import Mistral

class MistralWorker(qtc.QThread):
    response_received = qtc.Signal(str)
    error_occurred = qtc.Signal(str)
    finished_signal = qtc.Signal()

    def __init__(self, prompt: str, parent=None):
        super().__init__(parent)
        self.prompt = prompt

    def run(self):
        try:
            api_key = os.environ.get("MISTRAL_API_KEY")
            
            if not api_key:
                self.error_occurred.emit("Error: MISTRAL_API_KEY not found in environment variables.")
                return

            model = "mistral-large-latest"
            client = Mistral(api_key=api_key)

            messages = [{"role": "user", "content": self.prompt}]

            chat_response = client.chat.complete(
                model=model,
                messages=messages,
            )
            self.response_received.emit(chat_response.choices[0].message.content)
        except Exception as e:
            self.error_occurred.emit(f"An error occurred: {e}")
        finally:
            self.finished_signal.emit()