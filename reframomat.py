from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import *
import sys
import os
import enum
import numpy as np

def interpColors(color1, color2, factor):
  c1 = np.array(color1.getHslF())
  c2 = np.array(color2.getHslF())

  result = (1-factor) * c1 + factor * c2
  return QColor.fromHslF(*tuple(result))

class AmbilightWindow(QWidget):
  def __init__(self, rect):
    QWidget.__init__(self)

    self.setGeometry(rect)
    self.setWindowTitle("Ambilight")

    self.color1 = QColor(0x000000)
    self.color2 = QColor(0x555555)

  def paintEvent(self, event):
    qp = QPainter()
    qp.begin(self)
    gradient = QLinearGradient(self.rect().topLeft(), self.rect().bottomLeft())
    gradient.setColorAt(0, self.color1)
    gradient.setColorAt(1, self.color2)
    qp.fillRect(self.rect(), gradient)
    qp.end()

  def setColors(self, color1, color2):
    self.color1 = color1
    self.color2 = color2
    self.update()


class MainWindow(QWidget):
  def __init__(self, rect, controller):
    QWidget.__init__(self)

    self.controller = controller

    self.setGeometry(rect)
    self.setWindowTitle("Reframomat")

    self.welcomeMsg = QLabel(self)
    self.welcomeMsg.setText("Willkommen beim Reframomat!\nDrücke den Buzzer, um loszulegen!")
    self.welcomeMsg.setAlignment(Qt.AlignCenter)
    self.welcomeMsg.setGeometry(self.rect())

    self.videoWidget = QVideoWidget(self)
    self.videoWidget.setGeometry(self.rect())
    self.videoWidget.hide()

  def keyPressEvent(self, event):
    if type(event) == QKeyEvent:
      if event.key() == Qt.Key_Escape:
        QApplication.quit()
      elif event.key() == Qt.Key_S:
        self.controller.skip()
      else:
        self.controller.onBuzzerPress()
      event.accept()
    else:
      event.ignore()
    

class ReframomatState(enum.Enum):
  WELCOME = 0
  PHASE_1 = 1
  PHASE_2 = 2
  PHASE_3 = 3
  END = 4

class ReframomatController:
  #                 timestamp,  top color,  bottom color
  colors_phase1 = [[0,          0x000001,   0xFDFFFF], \
                   [10,         0xFF0001,   0x01FFFF], \
                   [20,         0xFFFF01,   0x0100FF], \
                   [27,         0xFFFFFD,   0x010000]]

  def __init__(self):
    if QDesktopWidget().screenCount() > 1:
      primaryRect = QDesktopWidget().availableGeometry(0)
      secondaryRect = QDesktopWidget().availableGeometry(1)
    else:
      # "Debug mode" with only one screen.
      # Use the top half of the first screen so we can
      # look at the console output.
      primaryRect = QDesktopWidget().availableGeometry(0)
      primaryRect.setHeight(primaryRect.height()/2)
      secondaryRect = QRect(primaryRect)
      primaryRect.setWidth(primaryRect.width()/2)
      secondaryRect.setLeft(primaryRect.width())

    self.state = ReframomatState.WELCOME
  
    self.secondWin = AmbilightWindow(secondaryRect)
    self.secondWin.show()
  
    self.mainWin = MainWindow(primaryRect, self)
    self.mainWin.show()

    self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
    self.mediaPlayer.setVideoOutput(self.mainWin.videoWidget)
    self.mediaPlayer.error.connect(self.handleError)
    self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)

    self.timer = QTimer(self.mainWin)
    self.timer.timeout.connect(self.onTimer)
    self.timer.start(100)

  def onBuzzerPress(self):
    if self.state == ReframomatState.WELCOME:
      self.mainWin.videoWidget.show()
      self.startVideo("dummy1.mp4")
      self.state = ReframomatState.PHASE_1
    elif self.state == ReframomatState.PHASE_1:
      print("Buzzer in Phase 1")
    elif self.state == ReframomatState.PHASE_2:
      print("Buzzer in Phase 2")
    elif self.state == ReframomatState.PHASE_3:
      print("Buzzer in Phase 3")
    elif self.state == ReframomatState.END:
      self.mainWin.welcomeMsg.setText("Willkommen beim Reframomat!\nDrücke den Buzzer, um loszulegen!")
      self.state = ReframomatState.WELCOME

  def onTimer(self):
    if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
      if self.state == ReframomatState.PHASE_1:
        pos = self.mediaPlayer.position() / 1000
        colors1 = self.colors_phase1[0]
        colors2 = self.colors_phase1[1]
        firstidx = 0
        while colors2[0] < pos:
          firstidx += 1
          if firstidx < len(self.colors_phase1)-1:
            colors1 = self.colors_phase1[firstidx]
            colors2 = self.colors_phase1[firstidx+1]
          else:
            break

        fadeFactor = min(1, (pos - colors1[0]) / (colors2[0] - colors1[0]))
        #print("pos %f, firstidx %i, fade %f" % (pos, firstidx, fadeFactor))
        
        result1 = interpColors(QColor(colors1[1]), QColor(colors2[1]), fadeFactor)
        result2 = interpColors(QColor(colors1[2]), QColor(colors2[2]), fadeFactor)

        self.secondWin.setColors(result1, result2)
          


  def mediaStateChanged(self):
    if self.mediaPlayer.state() == QMediaPlayer.StoppedState:
      if self.state == ReframomatState.PHASE_1:
        self.startVideo("dummy2.mp4")
        self.state = ReframomatState.PHASE_2
      elif self.state == ReframomatState.PHASE_2:
        self.startVideo("dummy3.mp4")
        self.state = ReframomatState.PHASE_3
      elif self.state == ReframomatState.PHASE_3:
        self.mainWin.videoWidget.hide()
        self.mainWin.welcomeMsg.setText("Ende Gelände! Buzz me!")
        self.state = ReframomatState.END

  def skip(self):
    self.mediaPlayer.stop()

  def startVideo(self, file):
    path = os.path.abspath(file)
    url = QUrl.fromLocalFile(path)
    content = QMediaContent(url)
    self.mediaPlayer.setMedia(content)
    self.mediaPlayer.play()

  def handleError(self):
    print("Error: " + self.mediaPlayer.errorString())





if __name__ == "__main__":
  app = QApplication(sys.argv)

  main = ReframomatController()

  sys.exit(app.exec_())
