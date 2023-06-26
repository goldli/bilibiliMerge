from PySide6.QtGui import *
from PySide6 import QtWidgets

class WndDragMove(object):
    def __init__(self, target : QtWidgets.QWidget) -> None:
        self.__isDragging = None
        self.__draggingStartWndPosition = None
        self.__draggingStartMousePosition = None

        target.mousePressEvent = self.__onMousePressEvent
        target.mouseMoveEvent = self.__onMouseMoveEvent
        target.mouseReleaseEvent = self.__onMouseReleaseEvent

        self.__target = target
        pass
    pass


    def __onMousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.__draggingStartMousePosition = event.globalPosition().toPoint()
            self.__draggingStartWndPosition = self.__target.frameGeometry().topLeft()
            self.__isDragging = True
    def __onMouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.__isDragging:
            distance = event.globalPosition().toPoint() - self.__draggingStartMousePosition
            self.__target.move(self.__draggingStartWndPosition + distance)
    def __onMouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.__isDragging = False