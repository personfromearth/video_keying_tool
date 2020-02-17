import os
from pathlib import Path
import cv2
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class MainWindow(QMainWindow):
    def __init__(self, bgImg, videoFilePath):
        # QMainWindow.__init__(self)
        super().__init__()
        self.bgImg = bgImg
        self.videoFilePath = videoFilePath
        self.cap = cv2.VideoCapture(self.videoFilePath)
        self.FPS = self.cap.get(cv2.CAP_PROP_FPS)
        self.numFrames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        class Label(QLabel):
            def __init__(self, img):
                super(Label, self).__init__()
                self.setFrameStyle(QFrame.StyledPanel)
                self.pixmap = QtGui.QPixmap(img)

            # def paintEvent(self, event):
            #     size = self.size()
            #     painter = QtGui.QPainter(self)
            #     point = QtCore.QPoint(0, 0)
            #     scaledPix = self.pixmap.scaled(size, Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
            #     # start painting the label from left upper corner
            #     point.setX((size.width() - scaledPix.width()) / 2)
            #     point.setY((size.height() - scaledPix.height()) / 2)
            #     print(point.x(), ' ', point.y())
            #     painter.drawPixmap(point, scaledPix)

        def addSlider(label, minValue, maxValue, value):
            slider = QSlider(QtCore.Qt.Horizontal, self)
            slider.setMinimum(minValue)
            slider.setMaximum(maxValue)
            slider.setValue(value)
            slider.setSingleStep(1)
            slider.setTickInterval(1)
            slider.setTickPosition(1)
            sliderLabel = QLabel(label)
            sliderLabel.setMinimumWidth(110)
            sliderLayout = QHBoxLayout()
            sliderLayout.setContentsMargins(0, 2, 0, 2)
            sliderLayout.addWidget(sliderLabel)
            sliderLayout.addWidget(slider)
            # mainVBoxLayout.addLayout(sliderLayout)
            slidersLayout.addLayout(sliderLayout)
            slider.valueChanged.connect(self.showFrame)
            return slider

        mainWidget = QWidget()
        mainWidget.setContentsMargins(3, 0, 3, 3)
        mainWidget.setMinimumSize(1920 / 2, 1080 / 2)
        self.setCentralWidget(mainWidget)

        mainVBoxLayout = QVBoxLayout()
        mainVBoxLayout.setSpacing(1)
        mainVBoxLayout.setContentsMargins(0, 0, 0, 0)

        titleBarLayout = QHBoxLayout()
        titleBarLayout.setSpacing(0)
        titleBarLayout.setContentsMargins(0, 0, 0, 0)
        spacer = QSpacerItem(40, 40, QSizePolicy.MinimumExpanding)
        titleBarLayout.addSpacerItem(spacer)
        QSizeGrip(self)
        titleBarWidget = QWidget()
        titleBarWidget.setMaximumHeight(20)
        titleBarWidget.setContentsMargins(0, 0, 0, 0)
        mainVBoxLayout.addWidget(titleBarWidget)
        titleBarWidget.setLayout(titleBarLayout)

        bottomPanelLayout = QHBoxLayout()
        mainMenuBtnsLayout = QVBoxLayout()
        mainMenuBtnsLayout.setContentsMargins(10, 0, 10, 0)
        addToQueueBtn = QPushButton('Add to Queue')
        addToQueueBtn.setStyleSheet('background-color: #33546C')
        # submit/render btn
        self.submitButton = QPushButton('Render Matte')
        self.submitButton.clicked.connect(self.writeMask)

        mainMenuBtnsLayout.addWidget(addToQueueBtn)
        mainMenuBtnsLayout.addWidget(self.submitButton)


        slidersLayout = QVBoxLayout()
        bottomPanelLayout.addLayout(slidersLayout)
        bottomPanelLayout.addLayout(mainMenuBtnsLayout)

        mainWidget.setLayout(mainVBoxLayout)

        # self.videoFrame = QLabel()
        self.videoFrame = QLabel()



        mainVBoxLayout.addWidget(self.videoFrame)
        mainVBoxLayout.addLayout(bottomPanelLayout)

        # add sliders
        self.timelineSlider = addSlider('Timeline', 0, self.numFrames - 1, 0)
        self.hLowSlider = addSlider('Hue Low: ', 0, 255, 20)
        self.hUpperSlider = addSlider('Hue Upper: ', 0, 255, 150)
        self.sLowSlider = addSlider('Saturation Low: ', 0, 255, 0)
        self.sUpperSlider = addSlider('Saturation Upper: ', 0, 255, 255)
        self.vLowSlider = addSlider('Velocity Low: ', 0, 255, 0)
        self.vUpperSlider = addSlider('Velocity Upper: ', 0, 255, 255)

        # title bar btns
        self.windowSizeBtn = QPushButton()
        self.windowSizeBtn.setMinimumSize(12, 12)
        self.windowSizeBtn.setContentsMargins(0, 0, 0, 0)
        self.windowSizeBtn.clicked.connect(self.changeWindowSize)
        self.windowSizeBtn.setIcon(QtGui.QIcon('icons/expand.png'))
        self.windowSizeBtn.setIconSize(QtCore.QSize(15, 15))

        self.closeBtn = QPushButton()
        self.closeBtn.setContentsMargins(0, 0, 0, 0)
        self.closeBtn.clicked.connect(self.close)
        self.closeBtn.setIcon(QtGui.QIcon('icons/close.png'))
        self.closeBtn.setIconSize(QtCore.QSize(15, 15))

        self.minimizeBtn = QPushButton()
        self.minimizeBtn.setContentsMargins(0, 0, 0, 0)
        self.minimizeBtn.clicked.connect(self.showMinimized)
        self.minimizeBtn.setIcon(QtGui.QIcon('icons/minimize.png'))
        self.minimizeBtn.setIconSize(QtCore.QSize(15, 15))



        titleBarLayout.addWidget(self.minimizeBtn)
        titleBarLayout.addWidget(self.windowSizeBtn)
        titleBarLayout.addWidget(self.closeBtn)

        self.showFrame()

    def mousePressEvent(self, event):
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        x = event.globalX()
        y = event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x - x_w, y - y_w)

    def changeWindowSize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

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
                mask = ~cv2.inRange(hsv_img, (self.hLowSlider.value(), self.sLowSlider.value(), self.vLowSlider.value()),
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
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_img, (self.hLowSlider.value(), self.sLowSlider.value(), self.vLowSlider.value()),
                           (self.hUpperSlider.value(), self.sUpperSlider.value(), self.vUpperSlider.value()))
        return mask

    def showFrame(self):
        mask = self.getFrameMask()
        r, g, b = cv2.split(self.bgImg)
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
        frameSize = self.videoFrame.size()
        self.videoFrame.setPixmap(QtGui.QPixmap(image).scaled(1920, 1080,
                                                              QtCore.Qt.KeepAspectRatio))
