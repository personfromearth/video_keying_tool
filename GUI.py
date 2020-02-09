import os
from pathlib import Path
import cv2
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *


class MainWindow(QMainWindow):
    def __init__(self, bg_img, videoFilePath):
        QMainWindow.__init__(self)
        self.bg_img = bg_img
        self.videoFilePath = videoFilePath
        self.setWindowTitle('Keying Tool')
        self.cap = cv2.VideoCapture(self.videoFilePath)
        self.FPS = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.numFrames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # timeline slider
        def createSlider(minValue, maxValue, value, singleStep, tickInterval, tickPosition):
            slider = QSlider(QtCore.Qt.Horizontal, self)
            slider.setMinimum(minValue)
            slider.setMaximum(maxValue)
            slider.setValue(value)
            slider.setSingleStep(singleStep)
            slider.setTickInterval(tickInterval)
            slider.setTickPosition(tickPosition)
            return slider

        self.timelineSlider = createSlider(0, self.numFrames - 1, 0, 1, 1, 1)
        self.timelineSlider.setWindowTitle('Timeline')

        # create hsv sliders
        self.hLowSlider = createSlider(0, 255, 100, 1, 1, 1)
        self.hUpperSlider = createSlider(0, 255, 150, 1, 1, 1)
        self.sLowSlider = createSlider(0, 255, 0, 1, 1, 1)
        self.sUpperSlider = createSlider(0, 255, 255, 1, 1, 1)
        self.vLowSlider = createSlider(0, 255, 0, 1, 1, 1)
        self.vUpperSlider = createSlider(0, 255, 255, 1, 1, 1)

        self.hLowSlider.valueChanged.connect(self.showFrame)
        self.hUpperSlider.valueChanged.connect(self.showFrame)
        self.sLowSlider.valueChanged.connect(self.showFrame)
        self.sUpperSlider.valueChanged.connect(self.showFrame)
        self.vLowSlider.valueChanged.connect(self.showFrame)
        self.vUpperSlider.valueChanged.connect(self.showFrame)
        self.timelineSlider.valueChanged.connect(self.showFrame)

        self.submitButton = QPushButton('Render Matte')
        self.submitButton.clicked.connect(self.writeMask)

        self.videoFrame = QLabel()

        mainWidget = QWidget()
        mainWidget.setMinimumSize(1920 / 2, 1080 / 2)

        self.setCentralWidget(mainWidget)

        vBoxLayout = QVBoxLayout()
        mainWidget.setLayout(vBoxLayout)

        vBoxLayout.addWidget(self.videoFrame)
        vBoxLayout.addWidget(self.timelineSlider)
        vBoxLayout.addWidget(self.hLowSlider)
        vBoxLayout.addWidget(self.hUpperSlider)
        vBoxLayout.addWidget(self.sLowSlider)
        vBoxLayout.addWidget(self.sUpperSlider)
        vBoxLayout.addWidget(self.vLowSlider)
        vBoxLayout.addWidget(self.vUpperSlider)
        vBoxLayout.addWidget(self.submitButton)

        self.showFrame()

    def writeMask(self):
        cap = self.cap
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        outputName = os.path.join(os.path.dirname(self.videoFilePath),
                                  Path(self.videoFilePath).stem + '_matte' + '.mp4')
        out = cv2.VideoWriter(outputName, fourcc, self.FPS, (int(cap.get(3)), int((cap.get(4)))))
        while cap:
            ret, frame = cap.read()
            if ret:
                hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv_img, (self.hLowSlider.value(), self.sLowSlider.value(), self.vLowSlider.value()),
                                   (self.hUpperSlider.value(), self.sUpperSlider.value(), self.vUpperSlider.value()))
                out.write(cv2.merge((mask, mask, mask)))
            else:
                break
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print('done!')

    def getFrameMask(self):
        videoFilePath = self.videoFilePath
        cap = cv2.VideoCapture(videoFilePath)
        cap.set(1, self.timelineSlider.value())
        ret, frame = cap.read()
        self.image = frame
        hsv_img = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_img, (self.hLowSlider.value(), self.sLowSlider.value(), self.vLowSlider.value()),
                           (self.hUpperSlider.value(), self.sUpperSlider.value(), self.vUpperSlider.value()))
        return mask

    def showFrame(self):
        mask = self.getFrameMask()
        r, g, b = cv2.split(self.bg_img)
        b &= mask
        g &= mask
        r &= mask

        r1, g1, b1 = cv2.split(self.image)
        b1 &= ~mask
        g1 &= ~mask
        r1 &= ~mask

        bg_masked = cv2.merge((r, g, b))
        img_masked = cv2.merge((r1, g1, b1))

        result = bg_masked + img_masked

        image = QtGui.QImage(result.data, result.shape[1], result.shape[0],
                             QtGui.QImage.Format_RGB888).rgbSwapped()
        self.videoFrame.setPixmap(QtGui.QPixmap.fromImage(image))
