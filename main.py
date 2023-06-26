# coding: utf-8

from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from UiLibs import *
import os
import time
from WndDragging import WndDragMove
from bilibiliMerge import *
from LogLevel import LogLevel
from LogType import LogType
from FfmpegState import FfmpegState

class Main(QWidget):
    def __init__(self, width, height):
        super().__init__(None)
        merge = BilibiliMerge()
        merge.onSuccessGetFiles.connect(self.__onSuccessGetFiles)
        merge.onFailedGetFiles.connect(lambda err: self.__writeLog(err, LogType.Error))
        merge.onMergeCompleted.connect(lambda msg: self.__writeLog(msg, LogType.Info))
        merge.onBeginGroup.connect(lambda group: self.__writeLog('准备处理列表：\n{}'.format(group), LogType.Info))
        merge.onBeginMergeFile.connect(self.__onBeginMergeFile)
        merge.onMergedFile.connect(self.__onMergedFile)
        merge.onMergeFileFailed.connect(lambda file:self.__writeLog('文件合并失败：\n{}'.format(file), LogType.Warning, LogLevel.Sub))
        merge.onRewriteFileError.connect(lambda file:self.__writeLog('重写文件失败：\n{}'.format(file), LogType.Warning, LogLevel.Sub))
        self.__merge = merge

        self.setWindowTitle('bilibili离线缓存合并程序')
        # 拖动可以分离出去 WndDragging
        self.__wndDragMove = WndDragMove(self)
        self.__ffmpegState = FfmpegState.NotFound
        self.setFixedSize(QSize(width, height))
        self.__addControls()
        self.__initCornerWnd()
        pass

    def __onBeginMergeFile(self, file):
        self.__writeLog('准备合并文件：{}'.format(file), LogType.Warning, LogLevel.Sub)
        self.__progressBar.Loading(file)
        pass

    def __onMergedFile(self, file,percenage):
        self.__writeLog('文件合并完成：{}'.format(file), LogType.Success, LogLevel.Sub)
        self.__progressBar.Update( percenage)
        pass
    
    def __onSuccessGetFiles(self, filesCount):
        if filesCount > 0:
            self.__writeLog('查询到文件: {} 组'.format(filesCount), LogType.Success)
        else:
            self.__writeLog('没有找到待合并的文件:', LogType.Error)
        pass

    def __onBtnStartClieck(self):
        match self.__ffmpegState:
            case FfmpegState.NotFound:
                msg = QMessageBox()
                msg.setMinimumWidth(700)
                msg.setText('未指定 fmpeg 可执行文件路径')
                msg.setWindowTitle("警告")
                msg.setWindowIcon(QIcon("./qssStyles/images/1.png"))

                icon = QPixmap('./qssStyles/images/error.png')
                icon = icon.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio)

                msg.setIconPixmap(icon)

                okBtn = QPushButton(msg)
                okBtn.setText("确定")
                okBtn.setFixedWidth(200)
                msg.addButton(okBtn, QMessageBox.YesRole)

                msg.exec_()
            case FfmpegState.Found:
                self.__writeLog('准备工作已完成。开始进行合并.', LogType.Warning)
                opt = MergeOption(self.__ffmpegFile, self.__cacheDir, self.__cbDeleteFilesWhenFinished.IsChecked)
                self.__merge.Execute(opt)
        pass
            
    # def paintEvent(self, event: QPaintEvent) -> None:
    #     '''
    #     重载​​paintEvent​​​. 此处当自定窗口样式时， 是必须的
    #     '''
    #     opt = QStyleOption()
    #     opt.initFrom(self)
    #     p = QPainter(self)
    #     self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
    #     super().paintEvent(event)

    def __initCornerWnd(self):
        '''
            WA_TranslucentBackground 与 add_shadow 冲突，
            会报错 UpdateLayeredWindowIndirect failed for ptDst=(780, 395), size=(1000x750), dirty=(1026x776 -13, -13) (参数错误。)
            解决方法： 创建一个 wndUiBaseLayer = QFrame(self)
            将 add_shadow 应用到 Frame 上即可
            ------------------------修改--------------------------
            pySide6基于层的概念
            那么
                1。去掉 paintEvent 的重载
                2。去掉 Main 对应的样式. 使用 setAttribute 去掉背景色
                3。增加一个层，用于显示阴影效果。 这个层要手动调整位置及大小
                4。增加一个控件层
        '''
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) #透明背景 
        self.setWindowFlag(Qt.WindowType.Window |Qt.WindowType.FramelessWindowHint) #无边框
        self.__addWndShadow() # 注意，这里使用的是 self。 不然，其它控件会继承阴影效果
        pass

    def __addWndShadow(self):
        # 添加阴影
        shadow = QtWidgets.QGraphicsDropShadowEffect(self.__shadowLayer)
        shadow.setOffset(0,0) # 偏移
        shadow.setBlurRadius(10) # 阴影半径 这里与 Main 样式中的 margin: 10px; 关联
        # shadow.setColor(Qt.gray) # 阴影颜色
        self.__shadowLayer.setGraphicsEffect(shadow) # 将设置套用到widget窗口中        
        pass   

    def __restoreDefaultCacheDir(self):
        self.__cacheDir = os.path.expanduser('~') + r'\Videos\bilibili'
        self.__cacheDirLable.setText('({})'.format(self.__cacheDir))
        pass    

    def __onStateChanged(self, isChecked):
        # todo 以下代码可以简化
        if isChecked:
            self.__restoreDefaultCacheDir()
            self.__writeLog("设置离线缓存目录为：", LogType.Success)
            self.__writeLog(self.__cacheDir, LogType.Warning, LogLevel.Sub)
        else:
            tmp = self.__cacheDir
            self.__cacheDir = ''
            self.__cacheDirLable.setText('')
            destDir = QFileDialog.getExistingDirectory(None, '选择离线缓存目录', tmp, QFileDialog.ShowDirsOnly)
            if destDir and os.path.exists(destDir):
                self.__cacheDir = destDir
                self.__cacheDirLable.setText('({})'.format(self.__cacheDir))
                self.__writeLog("设置离线缓存目录为：", LogType.Success)
                self.__writeLog(self.__cacheDir, LogType.Warning, LogLevel.Sub)
            else:
                # self.__writeLog('未设置离线缓存目录',LogType.Warning, LogLevel.Sub)
                self.__useDefaultCachePath.Reset()


    def __addControls(self):
        # 创建一个UI的基层
        shadowLayer = QWidget(self)
        shadowLayer.setStyleSheet("QWidget{ background-color: white; border-radius: 15px;}")
        shadowLayer.setGeometry(10,10,self.width()-18,self.height()-18)
        self.__shadowLayer = shadowLayer

        owner = QFrame(self)
        # owner.hide()
        # 窗口的边框宽度
        wndBorderWidth = 5 * 2 * 2

        # 关闭按钮
        wndClostBtn = QPushButton(owner)
        wndClostBtn.setObjectName("wndClostBtn") # 与样式 QPushButton#wndClostBtn 对应
        wndClostBtn.clicked.connect(lambda: self.close()) # 关闭
        wndClostBtn.setCursor(QCursor(Qt.PointingHandCursor)) # 手形鼠标
        wndClostBtn.setGeometry(self.width() - 25 - wndBorderWidth, 20, 18, 18)

        # 圆形进度条
        opt = CircularProgressBarOption()
        progressBar : CircularProgressBar = CircularProgressBar(owner, opt)
        progressBar.setTitle("bilibili离线缓存合并")
        progressBar.MoveTo(50, (self.height() - opt.Width) / 3)
        self.__progressBar = progressBar

        # 选项
        self.__cbDeleteFilesWhenFinished = CheckBox(owner, QPoint(20, self.height() - 140), "处理完成后删除离线缓存文件")
        cbUseDefaultCachePath = CheckBox(owner, QPoint(20, self.height() - 105), "使用默认 bilibili 离线缓存路径")
        cbUseDefaultCachePath.onCheckStateChanged.connect(self.__onStateChanged)
        self.__useDefaultCachePath = cbUseDefaultCachePath

        # 显示默认路径
        self.__cacheDir = os.path.expanduser('~') + r'\Videos\bilibili'
        lblCachePath = QLabel(owner)
        font = QFont()
        font.setFamily(u"宋体")
        font.setPointSize(12)
        lblCachePath.setFont(font)
        lblCachePath.setText('({})'.format(self.__cacheDir))
        lblCachePath.setStyleSheet("QLabel{ color:gray; }")
        cbRect = cbUseDefaultCachePath.Rect
        txtRect = lblCachePath.fontMetrics().boundingRect(lblCachePath.text())
        lblCachePath.setGeometry(cbRect.width() + cbRect.left() - 20, cbRect.y() + 11, txtRect.width(), txtRect.height())
        self.__cacheDirLable = lblCachePath

        # 日志
        logs = QPlainTextEdit(owner)
        logs.setReadOnly(True)
        logs.setGeometry(self.width()/2, 50, self.width()/ 2 - 30, self.height() - 150)
        # 垂直滚动条
        self.__vScroll = QScrollBar()
        logs.setVerticalScrollBar(self.__vScroll)
        
        self.__logs = logs

        # 底部button
        btnOK = QtWidgets.QPushButton('开始',owner)
        btnOK.setDefault(True)
        btnOK.setGeometry(int((self.width() - 220)/2) - wndBorderWidth, self.height() - 50, 220, 35)
        btnOK.clicked.connect(self.__onBtnStartClieck)

        pass

    def __writeLog(self, msg, logType : LogType = LogType.Info, logLevel : LogLevel = LogLevel.Main):
        prefix = ''
        if logLevel == LogLevel.Sub:
            prefix = r'&nbsp;&nbsp;&nbsp;&nbsp;'

        '''
            用于向控件首先插入数据
            # set the cursor position to 0
            cursor = QTextCursor(self.__logs.document())
            # set the cursor position (defaults to 0 so this is redundant)
            cursor.setPosition(0)
            self.__logs.setTextCursor(cursor)            
        '''        
        match logType:
            case LogType.Info:
                self.__logs.appendHtml('{} {}\n'.format(time.strftime('%H:%M:%S', time.localtime()), msg))
            case LogType.Warning:
                self.__logs.appendHtml('<span style="background-color:yellow; font-weigth:bold;">{2}{0} {1}</span>\n'.format(time.strftime('%H:%M:%S', time.localtime()), msg, prefix))
            case LogType.Error:
                self.__logs.appendHtml('<span style="background-color:red; font-weigth:bold;">{2}{0} {1}</span>\n'.format(time.strftime('%H:%M:%S', time.localtime()), msg ,prefix))
            case LogType.Success:
                self.__logs.appendHtml('<span style="color:green; font-weigth:bold;">{2}{0} {1}</span>\n'.format(time.strftime('%H:%M:%S', time.localtime()), msg, prefix))
        # 滚动到底部
        vScrollbar = self.__logs.verticalScrollBar()
        if vScrollbar:
            self.__vScroll.setValue(self.__vScroll.maximum())

        pass

    def CheckExistOfFFmpeg(self) -> None:
        root = os.path.abspath('.')
        ffmpegPath = os.path.join(root, "bin")

        found = True
        if not os.path.exists(ffmpegPath):
            found = False

        if found:
            self.__ffmpegFile = os.path.join(ffmpegPath, "ffmpeg.exe")
            found = os.path.exists(self.__ffmpegFile)
            if not found:
                self.__writeLog("在根目录下没有发现 ffmpeg.exe", LogType.Warning)

        else:
            self.__writeLog("在根目录下没有发现 bin 目录", LogType.Warning)

        if found:
            self.__writeLog("ffmpeg 准备就绪", LogType.Success)
            self.__ffmpegState = FfmpegState.Found
        pass

    pass

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    dialog = Main(800, 600)

    path = "{}/qssStyles/default.qss".format(os.path.dirname(os.path.abspath(__file__)))
    with open(path, "r", encoding='UTF-8') as f:
        _style = f.read()
        app.setStyleSheet(_style)
        f.close()
    dialog.__writeLog('程序启动', LogType.Success)
    dialog.CheckExistOfFFmpeg()
    dialog.show()

    app.exec()