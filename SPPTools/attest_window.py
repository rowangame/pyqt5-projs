# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget


class QAttestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mObserver = None

    def closeEvent(self, event):
        # 如果有观察者对象,由观察者对象处理逻辑
        if self.mObserver != None:
            if self.mObserver.onWindowCloseEvent != None:
                self.mObserver.onWindowCloseEvent(event)
                return
        # 接受事件回调
        event.accept()

    def setObserverObject(self, observer):
        self.mObserver = observer


