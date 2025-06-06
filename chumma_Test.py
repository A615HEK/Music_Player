import requests
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PySide6.QtCore import Qt, QThread, Signal

class Worker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, url, method, data=None):
        super().__init__()
        self.url = url
        self.method = method
        self.data = data

    def run(self):
        try:
            if self.method == "GET":
                response = requests.get(self.url)
            elif self.method == "POST":
                response = requests.post(self.url, json=self.data)
            else:
                self.error.emit(f"Unsupported method: {self.method}")
                return

            response.raise_for_status() # Raise an exception for HTTP errors
            self.finished.emit(response.text)
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Request error: {e}")
        except Exception as e:
            self.error.emit(f"An unexpected error occurred: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FastAPI PyQt Communication")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        layout.addWidget(self.text_output)

        self.get_button = QPushButton("Get Data from FastAPI")
        self.get_button.clicked.connect(self.get_data)
        layout.addWidget(self.get_button)

        self.post_button = QPushButton("Post Item to FastAPI")
        self.post_button.clicked.connect(self.post_item)
        layout.addWidget(self.post_button)

    def log_message(self, message):
        self.text_output.append(message)

    def get_data(self):
        url = "http://127.0.0.1:8000/" # Example: requesting data for item ID 123
        self.log_message(f"Making GET request to: {url}")
        self.worker = Worker(url, "GET")
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def post_item(self):
        url = "http://127.0.0.1:8000/items/"
        item_data = {"name": "New Widget", "description": "A fancy new widget", "price": 25.99}
        self.log_message(f"Making POST request to: {url} with data: {item_data}")
        self.worker = Worker(url, "POST", data=item_data)
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def handle_response(self, response_text):
        self.log_message(f"{type(response_text)}")

    def handle_error(self, error_message):
        self.log_message(f"Error: {error_message}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()