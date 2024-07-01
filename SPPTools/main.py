# -*- coding: utf-8 -*-
# @Time    : 2023/06/19
# @Author  : admin xielunguo
# @Email   : xielunguo@cosonic.com`
# @File    : main.py
# @Software: PyCharm
import os
import sys

# from PyQt5 import QtGui
# from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication

from main_tools_manager import Main_Tools_Manager
from main_tools_window import QMaintoolsWindow

if __name__ == '__main__':
    # absName = os.path.abspath(os.path.dirname(__file__))
    # print(absName)
    #
    # tmpDirName = os.getcwd()
    # print(tmpDirName)

    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myMainWindow = QMaintoolsWindow()
    myMainWindow.setObserverObject(Main_Tools_Manager)

    # 初始化主界面
    Main_Tools_Manager.getView().setupUi(myMainWindow)
    # 设置主窗口属性
    # setattr(Main_Tools_Manager.getView(), "mMainWindow", myMainWindow)
    Main_Tools_Manager.getView().mMainWindow = myMainWindow
    # 初始化事件
    Main_Tools_Manager.initEvents()

    # 禁止窗口最大化
    myMainWindow.setFixedWidth(myMainWindow.width())
    myMainWindow.setFixedHeight(myMainWindow.height())

    # palette = QPalette()
    # palette.setColor(QPalette.Background, Qt.cyan)
    # myMainWindow.setPalette(palette)

    # 居中显示
    desktop = QApplication.desktop()
    tmpRect = myMainWindow.geometry()
    tmpX = (desktop.width() - tmpRect.width()) // 2 - 200
    tmpY = (desktop.height() - tmpRect.height()) // 2
    myMainWindow.move(int(tmpX), int(tmpY))

    # 设置标题
    myMainWindow.setWindowTitle("串口工具-指令测试V1.3")

    # # 设置窗口图标(此方法占内存多,但图标显示效果较好,适用于较小的图片)
    # tmpDirName = os.getcwd()
    # ico_path = os.path.join(tmpDirName, 'logo.png')
    # icon = QtGui.QIcon()
    # icon.addPixmap(QtGui.QPixmap(ico_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    # myMainWindow.setWindowIcon(icon)

    myMainWindow.show()
    sys.exit(app.exec_())