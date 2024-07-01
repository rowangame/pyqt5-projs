# -*- coding: utf-8 -*-
# import os
import threading
import time
import re

# from PyQt5 import QtGui
# from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QFont
from PyQt5.QtWidgets import QMessageBox, QApplication

from attest_window import QAttestWindow
from main_tools_view import Ui_main_tools_view
from attest_manager import Attest_Manager
import serial.tools.list_ports

from spp_config_data import PortConfig_Data
import serial_util as SUtil

class Main_Tools_Manager(object):
    # ui界面对象
    mView = Ui_main_tools_view()

    @classmethod
    def on_attest_slt(self):
        print("on_attest_slt")
        if not hasattr(self, 'wndAttest'):
            self.wndAttest = QAttestWindow()
            self.wndAttest.setObserverObject(Attest_Manager)
            Attest_Manager.getView().setupUi(self.wndAttest)
            Attest_Manager.getView().mMainWindow = self.wndAttest

            # palette = QPalette()
            # palette.setColor(QPalette.Background, Qt.cyan)
            # self.wndAttest.setPalette(palette)

            Attest_Manager.initEvents()

            # 禁止窗口最大化
            self.wndAttest.setFixedWidth(self.wndAttest.width())
            self.wndAttest.setFixedHeight(self.wndAttest.height())

            # 靠右边显示
            desktop = QApplication.desktop()
            tmpRect = self.wndAttest.geometry()
            tmpX = (desktop.width() - tmpRect.width()) // 2 + 150
            tmpY = (desktop.height() - tmpRect.height()) // 2
            self.wndAttest.move(int(tmpX),int(tmpY))

            # # 设置窗口图标
            # tmpDirName = os.getcwd()
            # ico_path = os.path.join(tmpDirName, 'logo.png')
            # icon = QtGui.QIcon()
            # icon.addPixmap(QtGui.QPixmap(ico_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            # self.wndAttest.setWindowIcon(icon)
        self.wndAttest.show()


    @classmethod
    def on_com_fresh(self):
        # print("on_com_fresh")
        wndMain = self.getView()
        wndMain.comNumSlt.clear()
        wndMain.comNumSlt.addItem("None")

        plist = list(serial.tools.list_ports.comports())
        if len(plist) == 0:
            self.showWarningInfo("获取串口列表为空")
            return

        for tmpP in plist:
            # print("plist=", tmpP.name)
            wndMain.comNumSlt.addItem(tmpP.name)
        # 默认不选择端口号
        wndMain.comNumSlt.setCurrentIndex(0)

    @classmethod
    def on_read_data(self, data):
        wndMain = self.getView()
        # print("on_read_data", "type(self)=",type(self), "type(data)=",type(data), "data=" + data)
        wndMain.textEdit.append(data)

    @classmethod
    def validateAtCmd(self, atCmd):
        # 正则表达式验证指令是否是十六进制字符串
        # pat = re.compile(r"^[a-fA-F0-9]+$")
        # res = pat.search(atCmd)
        # #print(res)
        # return res != None
        res2 = re.match(r"^[a-fA-F0-9]+$", atCmd)
        # print(res2)
        if res2 != None:
            # 十六进制字符串长度必须是2的倍数
            return len(atCmd) % 2 == 0
        return False

    @classmethod
    def on_at_send(self):
        print("on_at_send")
        wndMain = self.getView()
        if not PortConfig_Data.mIsOpen:
            self.showWarningInfo("请打开串口")
            return
        atCmd = wndMain.edtAtInput.text()
        if not self.validateAtCmd(atCmd):
            self.showWarningInfo("输入的指令不符合格式要求")
            return
        wndMain.textEdit.append("TX->" + atCmd)
        SUtil.sendATByHexBase(atCmd,PortConfig_Data.mSerObj)


    @classmethod
    def on_com_open(self):
        print("on_com_open")
        wndMain = self.getView()
        if not PortConfig_Data.mIsOpen:
            # 分析串口类型
            index = wndMain.comNumSlt.currentIndex()
            if index == 0:
                self.showWarningInfo("请选择串口类型!")
                return
            # 记录串口类型
            PortConfig_Data.mComNum = wndMain.comNumSlt.itemText(index)

            # 分析波特率
            index = wndMain.cmbBaudrateSlt.currentIndex()
            if index == 0:
                self.showWarningInfo("请选择波特率类型!")
                return
            PortConfig_Data.mBaudrate = int(wndMain.cmbBaudrateSlt.itemText(index))

            try:
                print("先停止读数据线程...")
                if PortConfig_Data.mReadThread != None:
                    PortConfig_Data.stopReadProcess()

                print("先关闭现有的串口对象...")
                if PortConfig_Data.mSerObj != None:
                    PortConfig_Data.mSerObj.close()
                    PortConfig_Data.mSerObj = None

                print("打开串口操作...")
                serObj = SUtil.openSerialCom(PortConfig_Data.mComNum, PortConfig_Data.mBaudrate, PortConfig_Data.mTimeOut)
                PortConfig_Data.mSerObj = serObj
                PortConfig_Data.mIsOpen = True
                wndMain.btnComOpen.setText("关闭串口")

                print("关联读取线程...")
                PortConfig_Data.mObserver = self
                PortConfig_Data.mReadThread = threading.Thread(target=PortConfig_Data().readProcess, args=('main_tools_read', self))
                PortConfig_Data.mReadThread.start()
                print("打开串口成功...")
            except Exception as e:
                PortConfig_Data.mIsOpen = False
                self.showWarningInfo("打开串口失败?" + repr(e))
        else:
            print("停止读数据线程...")
            if PortConfig_Data.mReadThread != None:
                PortConfig_Data.stopReadProcess()

            print("关闭现有的串口对象...")
            if PortConfig_Data.mSerObj != None:
                PortConfig_Data.mSerObj.close()
                PortConfig_Data.mSerObj = None
            time.sleep(1)
            PortConfig_Data.mIsOpen = False
            wndMain.btnComOpen.setText("打开串口")
            print("关闭串口成功...")

    @classmethod
    def on_clear(self):
        # print("on_clear")
        wndMain = self.getView()
        answer = QMessageBox.question(wndMain.mMainWindow, '确认', '是否清空数据?', QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            print("clear...")
            wndMain.textEdit.setText("")
        else:
            print("cancel...")

    @classmethod
    def onCmbBaudrateCurrentIndexChanged(self):
        wndMain = self.getView()
        index = wndMain.cmbBaudrateSlt.currentIndex()
        value = wndMain.cmbBaudrateSlt.itemText(index)
        # self.showInformationInfo(f"index={index} value={value}")
        print(f"index={index} value={value}")

    @classmethod
    def addCmbItems(self):
        # 波特率选项
        Baudrates = ["None",4800,9600,14400,19200,38400,56000,57600,115200,128000,230400,256000,
                     460800,500000,512000,600000,750000,921600,1152000]
        wndMain = self.getView()
        for tmpV in Baudrates:
            wndMain.cmbBaudrateSlt.addItem(f"{tmpV}")
        # 添加选项变动事件
        # wndMain.cmbBaudruteSlt.currentIndexChanged.connect(self.onCmbBaudrateCurrentIndexChanged)
        wndMain.cmbBaudrateSlt.setCurrentIndex(0)

        # 校验位选项
        Check_Bits = ["None","Odd","Even","Mark","Space"]
        for tmpV in Check_Bits:
            wndMain.cmbBitCheckSlt.addItem(tmpV)
        wndMain.cmbBitCheckSlt.setCurrentIndex(0)
        wndMain.cmbBitCheckSlt.setEnabled(True)

        # 数据位
        Data_Bits = [5,6,7,8]
        for tmpV in Data_Bits:
            wndMain.cmbDataCheckSlt.addItem(f"{tmpV}")
        wndMain.cmbDataCheckSlt.setCurrentIndex(3)
        wndMain.cmbDataCheckSlt.setEnabled(True)

        # 停止位
        Stop_Bits = [1, 1.5, 2]
        for tmpV in Stop_Bits:
            wndMain.cmbStopBitSlt.addItem(f"{tmpV}")
        wndMain.cmbStopBitSlt.setCurrentIndex(0)
        wndMain.cmbStopBitSlt.setEnabled(True)

        # 串口选项
        wndMain.comNumSlt.addItem("None")
        wndMain.comNumSlt.setCurrentIndex(0)

        # 测试数据内容
        # 设置背景颜色
        wndMain.textEdit.setStyleSheet("QTextEdit{background-color:rgba(160,160,160,255);}")
        # 设置字体
        tmpFont = QFont("Times", 12, QFont.Black)
        tmpFont.setBold(False)
        wndMain.textEdit.setFont(tmpFont)

    @classmethod
    def onWindowCloseEvent(self, event):
        try:
            print("main_tools_manager.onWindowCloseEvent...")
            # 如果是串口通信中，则需要关闭串口通信
            if PortConfig_Data.mIsOpen:
                print("onAppQuit->停止读数据线程...")
                if PortConfig_Data.mReadThread != None:
                    PortConfig_Data.stopReadProcess()

                print("onAppQuit->关闭现有的串口对象...")
                if PortConfig_Data.mSerObj != None:
                    PortConfig_Data.mSerObj.close()
                    PortConfig_Data.mSerObj = None
                time.sleep(1)
                PortConfig_Data.mIsOpen = False
                print("onAppQuit->关闭串口成功...")
        except Exception as e:
            print(repr(e))
        finally:
            event.accept()

    # 初始化按钮事件
    @classmethod
    def initEvents(self):
        # 添加选择项
        self.addCmbItems()

        # 初始化串口配置数据
        PortConfig_Data.clearData()

        # 添加按键事件
        wndMain = self.getView()
        wndMain.btnComFresh.clicked.connect(self.on_com_fresh)
        wndMain.btnComOpen.clicked.connect(self.on_com_open)
        wndMain.btnAtSend.clicked.connect(self.on_at_send)
        wndMain.btnClear.clicked.connect(self.on_clear)
        wndMain.btnAtTestSlt.clicked.connect(self.on_attest_slt)

    @classmethod
    def showWarningInfo(self, info):
        wndMain = self.mView
        wndMain.mWarning = QMessageBox(QMessageBox.Warning, '警告', info)
        wndMain.mWarning.show()

    @classmethod
    def showInformationInfo(self, info):
        wndMain = self.mView
        wndMain.mWarning = QMessageBox(QMessageBox.Information, '提示', info)
        wndMain.mWarning.show()

    @classmethod
    def getView(self):
        return Main_Tools_Manager.mView