# -*- coding: utf-8 -*-
# @Time    : 2023/12/15
# @Author  : admin xielunguo
# @Email   : xielunguo@cosonic.com`
# @File    : main.py
# @Software: PyCharm

import sys

from PyQt5.QtWidgets import QApplication

from main_view_manager import Main_View_Manager
from main_view_window import QMainViewWindow

if __name__ == "__main__":
    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myMainWindow = QMainViewWindow()
    myMainWindow.setObserverObject(Main_View_Manager)

    # 初始化主界面
    Main_View_Manager.getView().setupUi(myMainWindow)
    # 设置主窗口属性
    # setattr(Main_View_Manager.getView(), "mMainWindow", myMainWindow)
    Main_View_Manager.getView().mMainWindow = myMainWindow
    # 初始化事件
    Main_View_Manager.initEvents()

    # 禁止窗口最大化
    myMainWindow.setFixedWidth(myMainWindow.width())
    myMainWindow.setFixedHeight(myMainWindow.height())

    # palette = QPalette()
    # palette.setColor(QPalette.Background, Qt.cyan)
    # myMainWindow.setPalette(palette)

    # 居中显示
    desktop = QApplication.desktop()
    tmpRect = myMainWindow.geometry()
    tmpX = (desktop.width() - tmpRect.width()) // 2
    tmpY = (desktop.height() - tmpRect.height()) // 2
    myMainWindow.move(tmpX, tmpY)

    # 设置标题
    myMainWindow.setWindowTitle("Go4-自动指令工具V1.0")

    # # 设置窗口图标(此方法占内存多,但图标显示效果较好,适用于较小的图片)
    # tmpDirName = os.path.dirname(os.path.abspath(__file__))
    # print(tmpDirName)
    # ico_path = os.path.join(tmpDirName, 'logo.png')
    # icon = QtGui.QIcon()
    # icon.addPixmap(QtGui.QPixmap(ico_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    # myMainWindow.setWindowIcon(icon)

    myMainWindow.show()
    sys.exit(app.exec_())