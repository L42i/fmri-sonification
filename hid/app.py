import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QLabel,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QSpinBox,
    QLineEdit,
    QPlainTextEdit
)
from PyQt5.QtCore import QSize
from sequencer import SequencerThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Synth Engine Client")
        self.setFixedSize(QSize(1280, 720))

        self.file_path = None
        self.worker = None
        self.is_paused = False

        # widgets
        self.upload_button = QPushButton("Upload CSV")
        self.play_pause_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")
        self.log_output = QPlainTextEdit()

        self.port_input = QSpinBox()
        self.port_input.setRange(1337, 65535)
        self.port_input.setValue(1337)
        self.port_input.setMaximumWidth(80)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("127.0.0.1")
        self.ip_input.setText("127.0.0.1")
        self.ip_input.setMaximumWidth(140)

        # log
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Waiting for data...")
        self.log_output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2e2e2e;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
            }
            """)
        

        # disable buttons until file exists
        self.play_pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        # connect buttons
        self.upload_button.clicked.connect(self.upload_file)
        self.play_pause_button.clicked.connect(self.play_pause_file)
        self.stop_button.clicked.connect(self.stop_file)
        self.port_input.valueChanged.connect(self.on_port_changed)
        self.ip_input.textChanged.connect(self.on_ip_changed)

        # basic controls layout
        basicControls = QHBoxLayout()
        basicControls.setSpacing(30)
        basicControls.addWidget(self.upload_button)
        basicControls.addWidget(self.play_pause_button)
        basicControls.addWidget(self.stop_button)

        # parameters layout
        parameters = QGridLayout()
        parameters.setSpacing(10)
        parameters.addWidget(QLabel("IP:"), 0, 0)
        parameters.addWidget(self.ip_input, 1, 0)
        parameters.addWidget(QLabel("Port:"), 0, 1)
        parameters.addWidget(self.port_input, 1, 1)

        # main layout
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(20, 20, 20, 20)
        mainLayout.setSpacing(10)
        mainLayout.addLayout(basicControls)
        mainLayout.addSpacing(20)
        mainLayout.addLayout(parameters)
        mainLayout.addWidget(self.log_output)

        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open CSV File",
            "",
            "CSV Files (*.csv)"
        )

        if file_path:
            self.file_path = file_path
            self.log_output.appendPlainText(f"Selected: {file_path}")
            self.play_pause_button.setEnabled(True)

    def play_pause_file(self):
        if not self.file_path:
            return

        # worker default stuff
        if self.worker is None or not self.worker.isRunning():
            self.worker = SequencerThread(self.file_path)
            self.worker.set_ip(self.ip_input.text().strip() or "127.0.0.1")
            self.worker.set_port(self.port_input.value())
            self.worker.status.connect(self.update_status)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()

            self.play_pause_button.setText("Pause")
            self.stop_button.setEnabled(True)
            self.is_paused = False
            return

        # if already running, toggle pause/resume
        if self.is_paused:
            self.worker.resume()
            self.play_pause_button.setText("Pause")
            self.is_paused = False
        else:
            self.worker.pause()
            self.play_pause_button.setText("Play")
            self.is_paused = True

    def stop_file(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()

        self.log_output.clear()   # reset terminal

        self.play_pause_button.setText("Play")
        self.stop_button.setEnabled(False)
        self.is_paused = False

    def update_status(self, message):
        self.log_output.appendPlainText(message)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def on_finished(self):
        self.play_pause_button.setText("Play")
        self.stop_button.setEnabled(False)
        self.is_paused = False
        if self.worker:
            self.worker = None

    def on_port_changed(self, value):
        if self.worker:
            self.worker.set_port(value)

    def on_ip_changed(self, value):
        if self.worker:
            self.worker.set_ip(value.strip() or "127.0.0.1")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
