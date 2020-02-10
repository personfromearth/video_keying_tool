import sys
import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from GUI import MainWindow

bgImg = cv2.imread(r"F:\keyer_test\bg.jpg")

videoFilePath = r"E:\short_sample.mp4"

styleSheet = """
    QSlider::handle:horizontal {
    background-color: #78EBE6;
}
QMainWindow {
    background-color: #17212B;
    color: #ffffff;
}
QPushButton {
    background-color: #17212B;
    color: #ffffff;
    border: none;
}
QLabel {
    color: #D4D4D4;
}
"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(styleSheet)

    main_window = MainWindow(bgImg, videoFilePath)
    main_window.setWindowFlags(Qt.FramelessWindowHint)
    main_window.show()
    sys.exit(app.exec_())
