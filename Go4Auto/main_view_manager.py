# -*- coding: utf-8 -*-
# import os
import os
import pathlib
# import threading
import time

from PyQt5.QtGui import QPalette, QFont
from PyQt5.QtWidgets import QMessageBox, QApplication

import bo4_cache_data
from auto_cmd_qthread import MyProcessQThread
from excel_util import Excel_Writer
from main_view import Ui_main_view
# from auto_cmd_process import AutoCmdProcess

class Main_View_Manager(object):
    # ui界面对象
    mView = Ui_main_view()
    mLinesCnt = 0
    mStartTime = 0

    @classmethod
    def on_data_event(self, info:tuple[str, any]):
        wndMain = self.getView()
        tag = info[0]
        if tag == "at":
            data = info[1]
            infoStr = self.getInfoData(data)
            wndMain.textEdit.append(infoStr)
            self.mLinesCnt += 1
        elif tag == "change":
            data = info[1]
            sData = "请更换设备,等待时间:%d秒" % data
            sHint = self.getNoticeInfoData(sData)
            wndMain.textEdit.append(sHint)
            self.mLinesCnt += 1
        elif tag == "comInfo":
            comName = info[1]
            boOK = info[2]
            msg = info[3]
            sHint = self.getComInfoData(comName, boOK, msg)
            wndMain.textEdit.append(sHint)
            self.mLinesCnt += 1

        # 测试开始时,滑动到最低端显示
        # 注意:
        # 1.使用普通线程,下面的代码不能使滑动条没动到最底端
        # 2.修改为使用Q线程则能实现实时滑动到底端
        hVerticalBar = wndMain.textEdit.verticalScrollBar()
        if hVerticalBar:
            curValue = hVerticalBar.value()
            # minValue = hVerticalBar.minimum()
            maxValue = hVerticalBar.maximum()
            # print(f"cValue={curValue} minValue={minValue}, maxValue={maxValue}")
            if curValue < maxValue:
                hVerticalBar.setValue(maxValue)

        # 防止过多数据记录,清空并保存日志
        if self.mLinesCnt > 2000:
            self.saveToTxtFile()
            print("Two many records, clear...")
            wndMain.textEdit.setText("")
            self.mLinesCnt = 0


    @classmethod
    def on_clear(self):
        # print("on_clear")
        wndMain = self.getView()
        answer = QMessageBox.question(wndMain.mMainWindow, '确认', '是否清空数据?', QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            print("clear...")
            wndMain.textEdit.setText("")
            self.mLinesCnt = 0
        else:
            print("cancel...")

    @classmethod
    def on_start(self):
        wndMain = self.getView()
        if wndMain.btnStart.isEnabled():
            print("do start...")
            print("关联自动线程...")
            sInfo = self.getStartInfoData("自动指令程序运行中...")
            wndMain.textEdit.append(sInfo)

            # # 使用普通线程来处理
            # AutoCmdProcess.mObserver = self
            # AutoCmdProcess.mAutoThread = threading.Thread(target=AutoCmdProcess().autoCmdProcess,
            #                                               args=('main_view_manager', self))
            # AutoCmdProcess.mAutoThread.start()

            # 使用Q线程来处理
            MyProcessQThread.mObserver = self
            MyProcessQThread.mAutoThread = MyProcessQThread()
            MyProcessQThread.mAutoThread.call_fun_signal.connect(self.on_data_event)
            MyProcessQThread.mAutoThread.start()

            self.mStartTime = time.time()
        wndMain.btnStart.setEnabled(False)

    @classmethod
    def onWindowCloseEvent(self, event):
        try:
            print("main_view_manager.onWindowCloseEvent...")
            # 如果是串口通信中，则需要关闭串口通信
            if MyProcessQThread.mRunning:
                print("onAppQuit->停止当前自动任务...")
                if MyProcessQThread.mAutoThread is not None:
                    MyProcessQThread.stopAutoProcess()

                print("onAppQuit->关闭现有的串口对象...")
                if MyProcessQThread.mSerObj is not None:
                    MyProcessQThread.mSerObj.close()
                    MyProcessQThread.mSerObj = None
                    print("onAppQuit->关闭串口成功...")

                MyProcessQThread.mRunning = False

                print("save to txt file...")
                self.saveToTxtFile()
                print("save to excel file...")
                self.saveToExcelFile()
        except Exception as e:
            print(repr(e))
        finally:
            event.accept()

    # 初始化按钮事件
    @classmethod
    def initEvents(self):
        # 初始化串口配置数据
        MyProcessQThread.clearData()

        # 添加按键事件
        wndMain = self.getView()
        wndMain.btnClear.clicked.connect(self.on_clear)
        wndMain.btnStart.clicked.connect(self.on_start)

        # 隐藏状态栏
        wndMain.statusbar.setVisible(False)

        # 如下代码解决打包出现的如下问题(不可删除)
        # (pkg_resources.DistributionNotFound: The 'pyqt5_plugins' distribution was not found)
        # 设置字体
        tmpFont = QFont("Times", 12, QFont.Black)
        tmpFont.setBold(False)

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
        return Main_View_Manager.mView

    @classmethod
    def getOKStyle(self):
        sHint = "OK"
        titleFormat = '<b><font color="#00FF00" size="4">{}</font></b>'
        return titleFormat.format(sHint)

    @classmethod
    def getPassStyle(self):
        sHint = "PASS"
        titleFormat = '<b><font color="#00FF00" size="4">{}</font></b>'
        return titleFormat.format(sHint)

    @classmethod
    def getFailStyle(self):
        sHint = "FAIL"
        titleFormat = '<b><font color="#FF0000" size="4">{}</font></b>'
        return titleFormat.format(sHint)

    @classmethod
    def getInfoData(self, devData: bo4_cache_data.Device_Data):
        if devData.processOk:
            indexFormat = '<b><font color="#000000" size="4">{}</font></b>'
            indexStr = indexFormat.format(devData.index)

            macFormat = '<b><font color="#0000FF" size="4">{}</font></b>'
            macStr = macFormat.format(devData.macAddr)

            rltFormat = '<b><font color="#00FF00" size="4">{}</font></b>'
            rltStr = rltFormat.format("OK")

            return "[" + indexStr + "]" + "-> Mac:" + macStr + " 进入RF产测状态:" + rltStr
        else:
            indexFormat = '<b><font color="#000000" size="4">{}</font></b>'
            indexStr = indexFormat.format(devData.index)

            macFormat = '<b><font color="#0000FF" size="4">{}</font></b>'
            macStr = macFormat.format(devData.macAddr)

            rltFormat = '<b><font color="#FF0000" size="4">{}</font></b>'
            rltStr = rltFormat.format("FAIL")

            return "[" + indexStr + "]" + "-> Mac:" + macStr + " 进入RF产测状态:" + rltStr

    @classmethod
    def getStartInfoData(self, sInfo):
        hintFormat = '<b><font color="#00FF00" size="4">{}</font></b>'
        hintStr = hintFormat.format(sInfo)
        return hintStr

    @classmethod
    def getNoticeInfoData(self, sInfo):
        hintFormat = '<b><font color="#000000" size="4">{}</font></b>'
        hintStr = hintFormat.format(sInfo)
        return hintStr

    @classmethod
    def getComInfoData(self, comName, boOK, msg):
        if not boOK:
            hintFormat = '<b><font color="#FF0000" size="4">{}</font></b>'
            hintStr = hintFormat.format(comName)
            return hintStr + msg
        else:
            hintFormat = '<b><font color="#0000FF" size="4">{}</font></b>'
            hintStr = hintFormat.format(comName)
            return hintStr + msg

    @classmethod
    def saveToTxtFile(self):
        try:
            # 如果没有测试记录则否保存
            if len(MyProcessQThread.mLstDevData) == 0:
                return

            # 执行保存数据逻辑
            timeNow = time.time()
            tinfo = time.strftime("%Y%m%d-%H_%M_%S", time.localtime(timeNow))

            # 生成目录
            wkdir = os.getcwd()
            subdir = wkdir + '\\logs'
            dirFile = pathlib.Path(subdir)
            if not dirFile.exists():
                os.mkdir(subdir)

            # 保存指令数据到日志文件
            logFileName = subdir + "\\" + f"{tinfo}-log.txt"
            txtFile = open(logFileName, "w+", encoding="utf-8")
            atLogs = self.getView().textEdit.toPlainText()
            txtFile.write(atLogs)
            txtFile.flush()
            txtFile.close()
        except Exception as e:
            print(repr(e))

    @classmethod
    def saveToExcelFile(self):
        try:
            # 如果没有测试记录则否保存
            if len(MyProcessQThread.mLstDevData) == 0:
                return
            # 执行保存数据逻辑
            timeNow = time.time()
            tinfo = time.strftime("%Y%m%d-%H_%M_%S", time.localtime(timeNow))

            # 生成目录
            wkdir = os.getcwd()
            subdir = wkdir + '\\logs'
            dirFile = pathlib.Path(subdir)
            if not dirFile.exists():
                os.mkdir(subdir)

            # 保存指令数据到日志文件
            excelFileName = subdir + "\\" + f"{tinfo}-log.xlsx"
            dts = dict()
            dts["startTime"] = time.strftime("%Y%m%d-%H:%M:%S", time.localtime(self.mStartTime))
            dts["endTime"] = time.strftime("%Y%m%d-%H:%M:%S", time.localtime(time.time()))
            dts["duration"] = "%d(s)" % (int(time.time() - self.mStartTime))
            dts["data"] = MyProcessQThread.mLstDevData
            Excel_Writer.saveToFile(excelFileName, dts)
        except Exception as e:
            print(repr(e))