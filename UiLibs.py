'''
自定义progressBar
'''
from PySide6.QtWidgets import *
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import *
from AnimatedToggle import AnimatedToggle
import math

class CircularProgressBarOption(object):
     def __init__(self, position: QPoint = QPoint(10,10), progressbarWidth: int = 320, progressbarColor: QColor = QColor(85, 170, 255, 255), progressbarBgColor: QColor = QColor(77, 77, 127)) -> None:
          self.__position : QPoint = position
          self.__width : int = progressbarWidth
          self.__color : QColor = progressbarColor
          self.__bgColor : QColor = progressbarBgColor
          pass

     @property
     def Position(self):
          return self.__position
     @property
     def Width(self):
          return self.__width
     @property
     def Color(self):
          return self.__color
     @property
     def BackgroundColor(self):
          return self.__bgColor
 
     pass

class CircularProgressBar(object):
     def __init__(self, parent, option: CircularProgressBarOption)-> None:
          self.__opt = option

          # 进度条的基础
          circularProgressBarBase = QFrame(parent)
          circularProgressBarBase.setObjectName(u"circularProgressBarBase")
          circularProgressBarBase.setGeometry(QRect(option.Position.x(), option.Position.y(), option.Width, option.Width))
          circularProgressBarBase.setFrameShape(QFrame.NoFrame)
          circularProgressBarBase.setFrameShadow(QFrame.Raised)
          self.__base = circularProgressBarBase

          # 进度条
          circularProgress = QFrame(circularProgressBarBase)
          circularProgress.setObjectName(u"circularProgress")
          circularProgress.setGeometry(QRect(option.Position.x(), option.Position.x(), option.Width - 20, option.Width - 20))
          # QFrame 不能省略.  stop:0.99999 , 1.00 外观显示为： 没有进度
          # styleSheet = "QFrame{{border-radius: {0}px;background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:0.99999 rgba(255, 0, 127, 0), stop:1.0 {1});}}".format((option.Width - 20) / 2, option.Color.name())
          circularProgress.setStyleSheet("QFrame{{border-radius: {0}px;background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:0.99999 rgba(255, 0, 127, 0), stop:1.0 {1});}}".format((option.Width - 20) / 2, option.Color.name()))
          circularProgress.setFrameShape(QFrame.NoFrame)
          circularProgress.setFrameShadow(QFrame.Raised)
          self.__progressbar = circularProgress
          self.__progressBarStyle = "QFrame{{border-radius: {0}px;background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:stop1 rgba(255, 0, 127, 0), stop:stop2 {1});}}".format((option.Width - 20) / 2, option.Color.name())

          # 进度条背景
          circularBg = QFrame(circularProgressBarBase)
          circularBg.setObjectName(u"circularBg")
          circularBg.setGeometry(QRect(10, 10, 300, 300))
          bgColor = option.BackgroundColor
          bgColor.setAlpha(120)

          styleSheet1 = "QFrame{{border-radius: {0}px;background-color: {1};}}".format((option.Width - 20)/2, bgColor.name(QColor.NameFormat.HexArgb))
          circularBg.setStyleSheet(styleSheet1)
          circularBg.setFrameShape(QFrame.NoFrame)
          circularBg.setFrameShadow(QFrame.Raised)

          # 中心大圆
          container = QFrame(circularProgressBarBase)
          container.setObjectName(u"container")
          container.setGeometry(QRect(25, 25, 270, 270))
          container.setStyleSheet("QFrame{{border-radius: {}px;background-color: {};}}".format((option.Width - 20)/2 - 15, bgColor.name()))
          container.setFrameShape(QFrame.NoFrame)
          container.setFrameShadow(QFrame.Raised)

          # 布局
          widget = QWidget(container)
          widget.setObjectName(u"widget")
          widget.setGeometry(QRect(40, 50, 193, 191))
          gridLayout = QGridLayout(widget)
          gridLayout.setObjectName(u"gridLayout")
          gridLayout.setContentsMargins(0, 0, 0, 0)

          # 标题
          labelTitle = QLabel(widget)
          labelTitle.setObjectName(u"labelTitle")
          font = QFont()
          font.setFamily(u"宋体")
          font.setPointSize(12)
          labelTitle.setFont(font)
          labelTitle.setStyleSheet(u"background-color: none;color: #FFFFFF")
          labelTitle.setAlignment(Qt.AlignCenter)
          labelTitle.setText('')
          self.__title = labelTitle

          gridLayout.addWidget(labelTitle, 0, 0, 1, 6)

          # %
          labelPercent = QLabel(widget)
          labelPercent.setObjectName(u"labelPercent")
          # labelPercent.setStyleSheet(u"QLabel{margin-left: 40px;}")
          labelPercent.setText('<span style=\"font-size:40pt;vertical-align:sub; color: white;\">%</span>')
          gridLayout.addWidget(labelPercent, 1, 5, 1, 1)

          '''
               后创建 进度， 使得 进度控件在 % 控件上面
          '''
          # 进度
          labelPercentage = QLabel(widget)
          labelPercentage.setObjectName(u"labelPercentage")
          labelPercentage.setStyleSheet(u"background-color: none;color: #FFFFFF")
          labelPercentage.setAlignment(Qt.AlignmentFlag.AlignCenter)
          labelPercentage.setText('<span style=\"font-size:80px;color: white;\">0</span>')
          self.__percentage = labelPercentage
          gridLayout.addWidget(labelPercentage, 1, 0, 1, 6)

          # 信息
          labelLoadingInfo = QLabel(widget)
          labelLoadingInfo.setObjectName(u"labelLoadingInfo")
          labelLoadingInfo.setMinimumSize(QSize(0, 20))
          labelLoadingInfo.setMaximumSize(QSize(16777215, 20))
          font2 = QFont()
          font2.setFamily(u"Segoe UI")
          font2.setPointSize(9)
          labelLoadingInfo.setFont(font2)
          labelLoadingInfo.setStyleSheet(u"QLabel{border-radius: 10px;background-color: rgb(93, 93, 154);color: #FFFFFF;margin-left: 40px;margin-right: 40px;}")
          labelLoadingInfo.setFrameShape(QFrame.NoFrame)
          labelLoadingInfo.setAlignment(Qt.AlignCenter)
          labelLoadingInfo.setText("......")
          self.__loading = labelLoadingInfo

          gridLayout.addWidget(labelLoadingInfo, 2, 0, 1, 6)

          labelCredits = QLabel(widget)
          labelCredits.setObjectName(u"labelCredits")
          labelCredits.setFont(font2)
          labelCredits.setStyleSheet(u"background-color: none; color: rgb(93, 93, 154);")
          labelCredits.setAlignment(Qt.AlignCenter)
          labelCredits.setText("Ai2Soft.sto")

          gridLayout.addWidget(labelCredits, 3, 0, 1, 6)

          circularBg.raise_()
          circularProgress.raise_()
          container.raise_()
     pass

     def __setProgressbarValue(self, value = 0):
          stop1 = 0.99999
          stop2 = 1.0

          if value > 0:
               progress = (100 - value) / 100.0
               stop1 = progress - 0.001
               stop2 = progress

          if value == 100:
            stop1 = 1.000
            stop2 = 1.000

          styleSheet = self.__progressBarStyle.replace('stop1', str(stop1)).replace('stop2', str(stop2))
          self.__progressbar.setStyleSheet(styleSheet)

     pass

     def MoveTo(self, x :int, y : int):
          self.__base.setGeometry(QRect(x, y, self.__opt.Width, self.__opt.Width))
    
     def setTitle(self, title):
          return self.__title.setText(title)

     def Loading(self, text):
          self.__loading.setText(text)

     def Update(self, percent):
          # 文本显示百分比
          self.__percentage.setText('<span style=\"font-size:80px;color: white;\">{}</span>'.format(math.ceil(percent)))
          # 进度条
          self.__setProgressbarValue(percent)

     pass

class CheckBox(QObject):
     # 若要使用 Signal ，必须继承自 QObject. 同时要使用 super().__init__() ,且 <变量> 不声明而是直接赋值
     onCheckStateChanged = Signal(bool)

     def __init__(self, parent, position : QPoint, text) -> None:
          self.__position = position
          self.__text = text
          self.__layer = parent

          self.__bound = QRect()
          self.__bound.setTopLeft(position)
          self.__createCheckBox()
          self.__createLable()

          super().__init__()
          pass

     def __createCheckBox(self):
          size = AnimatedToggle.sizeHint()
          chBox = AnimatedToggle(self.__layer)
          chBox.setFixedSize(size)
          chBox.setGeometry(self.__position.x(), self.__position.y(), size.width(), size.height())
          chBox.setChecked(True)
          
          self.__checkBox = chBox
          chBox.stateChanged.connect(lambda state, checkbox=self: self.__update(state, checkbox))
          self.__bound.setHeight(size.height())
          pass

     def __update(self, state, checkbox):
          self.onCheckStateChanged.emit(state ==  2)

     def __createLable(self):
          lbl = QLabel(self.__layer)
          font = QFont()
          font.setFamily(u"宋体")
          font.setPointSize(14)
          lbl.setFont(font)
          lbl.setText(self.__text)
          rect = lbl.fontMetrics().boundingRect(lbl.text())
          lbl.setGeometry(self.__position.x() + 60, self.__position.y() + 11, rect.width(), rect.height())

          maxHeight = rect.height() if rect.height() > self.__bound.height() else self.__bound.height()
          self.__bound.setHeight(maxHeight)
          self.__bound.setWidth(self.__position.x() + 60 + rect.width() + 5)
          pass

     @property
     def Rect(self) -> QRect:
          return self.__bound
     

     @property
     def IsChecked(self) -> bool:
          return self.__checkBox.checkState() == Qt.CheckState.Checked

     def Reset(self):
          self.__checkBox.setCheckState(Qt.CheckState.Checked)
     pass