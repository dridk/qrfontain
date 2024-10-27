import io
import numpy as np
import struct
import sys
import time
import lt
import hashlib
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PIL import Image

import qrfontain

MARGIN = 20


class CaptureWidget(QWidget):
    """
    Transparent widget used to capture QR Code
    """

    capture_changed = Signal(QPixmap)

    def __init__(self, frame_per_second: int = 60, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Capture window")
        self.frame_per_second = frame_per_second
        self.interval_ms = 1 / frame_per_second

        # Timer creation
        self.timer = QTimer()
        self.timer.setInterval(self.interval_ms)
        self.timer.timeout.connect(self.capture)

        # Make widget transparent
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(800, 800)

    def set_capture(self, activate: bool):
        if activate:
            self.timer.start()
        else:
            self.timer.stop()

    def capture(self):
        """
        Capture QR code and decode it using fontain decoder
        """
        area = self.geometry().adjusted(MARGIN, MARGIN, -MARGIN, -MARGIN)

        screens = QApplication.screens()
        screen = screens[1]
        x = area.x()
        y = area.y()
        pix = screen.grabWindow(0, x, y, area.width(), area.height())
        self.capture_changed.emit(pix)

        # self.payload = self.decode_qr_code(pix)

        # self.qr_code_detected = True if self.payload else False
        # self.captured.emit()

        # if self.transmission:
        #     self.decode_fontain()

    # def decode_qr_code(self, pix: QPixmap) -> bytes:
    #     """
    #     Decode QR code from pixmap and return bytes or None
    #     """

    #     img = self.to_pillow(pix)
    #     data = zbarlight.scan_codes(["qrcode"], img)
    #     if data:
    #         data = data[0].decode()
    #         return base64.b64decode(data)
    #     return None

    # def total_size(self):
    #     if self.decoder is None:
    #         return -1

    #     else:
    #         return self.decoder.filesize

    # def decode_fontain(self) -> bytes:

    #     stream = io.BytesIO(self.payload)

    #     header = lt.decode._read_header(stream)
    #     block = lt.decode._read_block(header[1], stream)

    #     self.decoder.consume_block((header, block))

    #     if self.decoder.is_done():
    #         self.transmission = False

    #         delay = time.time() - self.start
    #         self.start = None

    #         print(delay)

    #         self.completed.emit()
    #         with open(self.filename, "wb") as file:
    #             self.decoder.stream_dump(file)

    def paintEvent(self, event: QPaintEvent):
        """
        Draw capture area
        """
        painter = QPainter(self)


class MainWindow(QWidget):

    finished = Signal()
    progressed = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Transfer Window")

        self.is_transmission = False
        self.is_qrcode = False
        self.decoder = None

        # Preview
        self.preview_widget = QLabel()
        self.preview_widget.setAlignment(Qt.AlignCenter)

        # capture widget
        self.capture_widget = CaptureWidget()
        self.capture_widget.move(250, 200)

        self.progress_bar = QProgressBar()

        # Add status
        self.status = QStatusBar()
        self.info_label = QLabel()
        self.status.addPermanentWidget(self.info_label)

        # setup toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.decode_action = self.toolbar.addAction(
            QIcon.fromTheme(QIcon.ThemeIcon.MediaRecord), "Start transmission"
        )

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.preview_widget)
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.status)
        self.setLayout(self.main_layout)
        # connect
        self.decode_action.triggered.connect(self.start_transmission)
        self.capture_widget.capture_changed.connect(self.on_capture_changed)
        self.finished.connect(self.on_finished)

        self.capture_widget.set_capture(True)
        self.capture_widget.show()

    def closeEvent(self, event):
        self.capture_widget.close()
        event.accept()

    def start_transmission(self):

        self.decoder = lt.decode.LtDecoder()
        self.is_transmission = True

    def show_message(self):

        if self.is_transmission:
            message = "Download file in progress ... "
        else:
            message = ""

        self.info_label.setText(f"{self.is_qrcode=}    {self.is_transmission=}")
        self.status.showMessage(message)

    def show_success(self):
        print("success")
        QMessageBox.information(self, "success", "Your file has been downloaded")

    def on_capture_changed(self, pixmap: QPixmap):

        self.preview_widget.setPixmap(pixmap)

        img = self.to_pillow(pixmap)

        data = qrfontain.decode_qrcode(img)
        # If data is None, no qr code available
        self.is_qrcode = data is not None

        if self.is_qrcode and self.is_transmission:
            # Start transmission
            stream = io.BytesIO(data)
            header = lt.decode._read_header(stream)
            block = lt.decode._read_block(header[1], stream)
            self.decoder.consume_block((header, block))

            self.progress_bar.setRange(0, self.decoder.block_graph.num_blocks)
            self.progress_bar.setValue(len(self.decoder.block_graph.checks))

            if self.decoder.is_done():
                print("Done")
                self.is_transmission = False
                self.finished.emit()

        self.show_message()

    def to_pillow(self, img: QPixmap) -> Image:
        """
        Convert QPixmap to PIL Image
        """
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        return Image.open(io.BytesIO(buffer.data()))

    def on_finished(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save file ", QDir.homePath())

        if not file:
            return

        with open(file, "wb") as file:
            file.write(self.decoder.bytes_dump())


if __name__ == "__main__":

    app = QApplication(sys.argv)

    win = MainWindow()

    win.show()

    # capture_widget = CaptureWidget()
    # log_widget = QPlainTextEdit()
    # preview_widget = QLabel()

    # capture_widget.show()
    # log_widget.show()
    # preview_widget.show()

    # preview_widget.resize(700, 700)

    # # capture_widget.capture_changed.connect(preview_widget.set_capture)
    # capture_widget.log_changed.connect(log_widget.setPlainText)
    # capture_widget.pix_changed.connect(preview_widget.setPixmap)

    # capture_widget.show()

    app.exec()
