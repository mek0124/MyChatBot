from PySide6 import QtCore as qtc
from pathlib import Path
import base64
import uuid
from backend.agents.mistral_agent import MistralWorker
from backend.agents.dataset_agent import DatasetAgentWorker
from backend.models.message import Message
from backend.models.profile import Profile

class MainController(qtc.QObject):
    display_user_message = qtc.Signal(str)
    display_ai_message = qtc.Signal(str)

    show_loading = qtc.Signal()
    hide_loading = qtc.Signal()

    error_occurred = qtc.Signal(str)

    def __init__(self):
        super().__init__()
        self.conversation_id = str(uuid.uuid4())
        self.user_profile = None
        self.ai_profile = None
        self.worker_threads = []
        
        self.init_profiles()

    def init_profiles(self):
        user_worker = DatasetAgentWorker(entity_type='user')
        user_worker.profile_ready.connect(self.set_user_profile)
        user_worker.error_occurred.connect(
            lambda e: print(f"Error getting user profile: {e}"))
        user_worker.finished_signal.connect(self.cleanup_thread)
        self.worker_threads.append(user_worker)
        user_worker.start()
        
        ai_worker = DatasetAgentWorker(entity_type='ai')
        ai_worker.profile_ready.connect(self.set_ai_profile)
        ai_worker.error_occurred.connect(
            lambda e: print(f"Error getting AI profile: {e}"))
        ai_worker.finished_signal.connect(self.cleanup_thread)
        self.worker_threads.append(ai_worker)
        ai_worker.start()

    def set_user_profile(self, profile: Profile):
        self.user_profile = profile
        print(f"User profile set: {profile.id}")

    def set_ai_profile(self, profile: Profile):
        self.ai_profile = profile
        print(f"AI profile set: {profile.id}")

    def send_message(self, message_text: str):
        if not message_text or not self.user_profile:
            return
        
        self.display_user_message.emit(message_text)
            
        # Create message object
        message = Message(
            conversation_id=self.conversation_id,
            sender_id=self.user_profile.id,
            content=message_text
        )
        
        # Log the message
        self.log_message(message)
        
        self.show_loading.emit()

        # Send to Mistral
        self.send_to_mistral(message_text)

    def send_to_mistral(self, prompt: str):
        worker = MistralWorker(prompt)
        worker.response_received.connect(self.handle_response)
        worker.error_occurred.connect(self.handle_error)
        worker.finished_signal.connect(self.cleanup_thread)
        self.worker_threads.append(worker)
        worker.start()

    def handle_response(self, response: str):
        self.hide_loading.emit()

        self.display_ai_message.emit(response)

        if not self.ai_profile:
            return
            
        # Create message object for AI response
        message = Message(
            conversation_id=self.conversation_id,
            sender_id=self.ai_profile.id,
            content=response
        )
        
        # Log the message
        self.log_message(message)

    def handle_error(self, error: str):
        self.hide_loading.emit()
        self.error_occurred.emit(error)

    def log_message(self, message: Message):
        worker = DatasetAgentWorker(message=message)
        worker.logging_complete.connect(
            lambda success: print("Message logged" if success else "Failed to log message"))
        worker.error_occurred.connect(
            lambda error: print(f"Error logging message: {error}"))
        worker.finished_signal.connect(self.cleanup_thread)
        self.worker_threads.append(worker)
        worker.start()

    def attach_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                filename = Path(file_path).name
                return f"Here is the content of file '{filename}':\n\n{content}\n\nPlease analyze this file."
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def attach_image(self, image_path: str):
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            filename = Path(image_path).name
            return f"Here is an image named '{filename}' (base64 encoded):\n\n{encoded_string}\n\nPlease analyze this image."
        except Exception as e:
            return f"Error processing image: {str(e)}"

    def cleanup_thread(self):
        self.worker_threads = [t for t in self.worker_threads if t.isRunning()]