import sys
import cv2
from PyQt5.QtWidgets import QApplication
from GUI import MainWindow

bg_img = cv2.imread("bgPath")

videoFilePath = r"videoPath"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow(bg_img, videoFilePath)
    main_window.show()
    sys.exit(app.exec_())
