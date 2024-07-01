# -*- coding: utf-8 -*-
import os
import pathlib
import threading
import time
from io import BytesIO

from qrcode.image.pure import PyPNGImage

import qrcode
import serial
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor, QFont, QPixmap, QImage, QTextCharFormat
from PyQt5.QtWidgets import QMessageBox, QPushButton
from attest_view import Ui_wnd_attest
from attest_config_data import Attest_Config_Data
from attest_case_data import Attest_Case_Data, Keypress_Test_Data
import serial_util as SUtil
from at_process_thread import MyProcessThread
from excel_util import Excel_Writer
from spp_config_data import PortConfig_Data


class Attest_Manager(object):
    # ui界面对象
    mView = Ui_wnd_attest()
    # 加载标记
    mLoaded = False
    # 原始配置数据
    mOriAtLst = []
    # 真实指令配置数据
    mAtLst = []

    @classmethod
    def on_btn_load(self):
        print("on_btn_load")
        if self.mLoaded:
            self.showWarningInfo("指令已加载")
            return

        if not self.mLoaded:
            # 加载指令集
            try:
                # cwd = os.getcwd()
                # 返回当前文件所在文件夹的绝对路径
                absPath = os.path.dirname(os.path.abspath(__file__))
                filePath = absPath + "/A3040.txt"
                print("filePath=",filePath)
                tmpFile = open(filePath, "r", encoding='UTF-8')
                for tmpLine in tmpFile:
                    tmpInfo = tmpLine.strip()
                    if len(tmpInfo) > 0:
                        # print(tmpInfo)
                        tmpLst = tmpInfo.split("#")
                        # if len(tmpLst) > 0:
                        #     print(tmpLst[0], tmpLst[1], tmpLst[2])
                        self.mOriAtLst.append(tmpLst)
                self.mLoaded = True
            except Exception as e:
                self.showWarningInfo("加载指令集失败!?" + repr(e))

        print(f"加载指令集完成,记录数={len(self.mOriAtLst)}")

        # 初始化测试用例数据
        Attest_Case_Data.clearData()
        Attest_Case_Data.setAllCases(self.mOriAtLst)
        # 初始化按键测试
        Keypress_Test_Data.initKeypressTestData()
        Keypress_Test_Data.resetData()

        # 初始化真实指令配置数据
        # 初始化标题
        self.mAtLst.append(["结果状态值", "指令集", "指令功能定义", "人工操作等待时间(秒)", "是否需要人工确认结果[是:1 否:0]"])
        for tmpCaseData in Attest_Case_Data.mAllCases:
            self.mAtLst.append([tmpCaseData.atRefResult,
                                tmpCaseData.atCmd,
                                tmpCaseData.atDesc,
                                f"{tmpCaseData.opWaitTime}",
                                f"{tmpCaseData.needConfirm}"])

        # 显示数据
        self.initDataView()

    @classmethod
    def table_view_clicked(self, index):
        # print("table_view_clicked")
        # 参考文档
        # https://blog.csdn.net/qq_37609345/article/details/121233808

        # tmpRow = index.row()
        # tmpCol = index.column()
        # item = self.model.item(tmpRow, tmpCol)
        # value = item.text()
        # self.showInformationInfo(f"row={tmpRow},col={tmpCol},value={value}")
        pass

    @classmethod
    def onTableBtnClicked(self):
        print("onTableBtnClicked...")
        # try:
        #     tmpTableView = self.getView().tableView
        #     tmpBtn = tmpTableView.sender()
        #     tmpRow = tmpBtn.property("row_index")
        #     # self.showInformationInfo(f"row={tmpRow} txt={tmpBtn.text()}")
        #
        #     # 设置单元格内容
        #     tmpIndex = tmpTableView.model().index(tmpRow, 3)
        #     tmpTableView.model().setData(tmpIndex, "testing...")
        #     # 获得单元格内容
        #     celCtx = tmpTableView.model().index(tmpRow, 0).data()
        #     print("celCtx=", celCtx)
        # except Exception as e:
        #     print(repr(e))

    @classmethod
    def on_stop_test(self):
        # print("on_stop_test...")
        if not Attest_Config_Data.mIsTesting:
            self.showInformationInfo("当前不在测试状态中!")
            return

        if Attest_Config_Data.mStopSignal:
            print("停止测试处理中...")
            return

        wndMain = self.getView()
        sHint = "是否停止测试?"
        answer = QMessageBox.question(wndMain.mMainWindow, '人工确认', sHint, QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.No:
            return

        # 设置停止信号状态
        Attest_Config_Data.mStopSignal = True
        # 停止测试逻辑
        self.endTestProcess("except")

    @classmethod
    def initDataView(self):
        max_row = len(self.mAtLst)
        max_col = 5
        self.model = QStandardItemModel(max_row, max_col)
        for row in range(0, max_row):
            tmpLst = self.mAtLst[row]
            self.model.setItem(row, 0, QStandardItem(tmpLst[0]))
            self.model.setItem(row, 1, QStandardItem(tmpLst[1]))
            self.model.setItem(row, 2, QStandardItem(tmpLst[2]))
            if row == 0:
                self.model.setItem(row, 3, QStandardItem("指令结果"))
                self.model.setItem(row, 4, QStandardItem("验证状态"))
            else:
                self.model.setItem(row, 3, QStandardItem("None"))
                self.model.setItem(row, 4, QStandardItem("待验证"))

        wndMain = self.getView()
        wndMain.tableView.setModel(self.model)
        # wndMain.tableView.clicked.connect(self.table_view_clicked)

        # 设置行宽和高
        # REF_WIDTH = 240
        REF_WIDTHS = [240, 240, 240, 140, 140]
        for i in range(max_col):
            wndMain.tableView.setColumnWidth(i, REF_WIDTHS[i])

        for i in range(max_col):
            # 设置标题加粗显示
            tmpItem = self.model.item(0, i)
            # 设置字体颜色
            tmpItem.setForeground(QBrush(QColor(0, 0, 0)))
            # 设置字体加粗
            tmpItem.setFont(QFont("Times", 12, QFont.Black))
            # 设置背景颜色
            tmpItem.setBackground(QBrush(QColor(0, 255, 0)))

        # # 添加按钮
        # OP_INDEX = 4
        # for tmpRow in range(1, max_row):
        #     tmpBtn = QPushButton(f"测试-{tmpRow}", wndMain.tableView)
        #     tmpBtn.setDown(False)
        #     tmpBtn.setStyleSheet("QPushButton{margin:3px};")
        #     tmpBtn.setProperty("row_index",tmpRow)
        #     # 注意,这里不能用lamda表达式,来传替按钮对象,来区分是哪个按钮的事件
        #     # 可以用父控件发送对象来区分
        #     tmpBtn.clicked.connect(self.onTableBtnClicked)
        #     wndMain.tableView.setIndexWidget(self.model.index(tmpRow, OP_INDEX), tmpBtn)

    @classmethod
    def on_btn_comfresh(self):
        print("on_btn_comfresh")
        wndMain = self.getView()
        wndMain.cmbNumSlt.clear()
        wndMain.cmbNumSlt.addItem("None")

        plist = list(serial.tools.list_ports.comports())
        if len(plist) == 0:
            self.showWarningInfo("获取串口列表为空")
            return

        for tmpP in plist:
            # print("plist=", tmpP.name)
            wndMain.cmbNumSlt.addItem(tmpP.name)
        # 默认不选择端口号
        wndMain.cmbNumSlt.setCurrentIndex(0)

    @classmethod
    def updateTestState(self, caseIndex, state):
        try:
            tmpTableView = self.getView().tableView
            tmpIndex = tmpTableView.model().index(caseIndex, 3)
            if state == 0:
                tmpTableView.model().setData(tmpIndex, "Testing...")
            elif state == 1:
                tmpTableView.model().setData(tmpIndex, "Fail")
            elif state == 2:
                tmpTableView.model().setData(tmpIndex, "Pass")
        except Exception as e:
            print(repr(e))

    @classmethod
    def showTestStartInfo(self, testData):
        try:
            wndMain = self.getView()
            tmpTableView = wndMain.tableView

            caseIndex = testData.caseIndex
            tmpIndex = tmpTableView.model().index(caseIndex, 3)
            tmpTableView.model().setData(tmpIndex, "测试中...")
            if caseIndex > 1:
                self.addTextHint("\n\n")
                sHint = f"id=[{caseIndex}],{testData.atDesc},命令开始..."
                # 提示测试开始
                self.addTextHint(self.getTitleStyle(sHint))
            else:
                sHint = f"id=[{caseIndex}],{testData.atDesc},命令开始..."
                # 提示测试开始
                self.addTextHint(self.getTitleStyle(sHint))
        except Exception as e:
            print(repr(e))

    @classmethod
    def keyPressTestStart(self, testAtData):
        wndMain = self.getView()
        try:
            testAtData.startTest()

            tmpTableView = wndMain.tableView
            caseIndex = testAtData.caseIndex
            tmpIndex = tmpTableView.model().index(caseIndex, 3)
            tmpTableView.model().setData(tmpIndex, "测试中...")
        except Exception as e:
            print(repr(e))

    @classmethod
    def keyPressTestEnd(self, testAtData, testKeyData):
        wndMain = self.getView()
        try:
            # 按键出错
            if testKeyData.errorStatus:
                # 记录结果数据
                testAtData.errorStatus = True
                testAtData.rltStatus = False
                testAtData.testData = ""

                # 指令状态设置
                tmpTableView = wndMain.tableView
                caseIndex = testAtData.caseIndex
                # 状态设置
                tmpIndex = tmpTableView.model().index(caseIndex, 3)
                tmpTableView.model().setData(tmpIndex, "FAIL")
                # 颜色设置
                tmpItem = tmpTableView.model().item(caseIndex, 3)
                tmpItem.setForeground(QBrush(QColor(255, 0, 0)))
                tmpItem.setBackground(QBrush(QColor(255, 255, 255)))

                # 结果状态设置[功能异常]
                tmpTableView = wndMain.tableView
                caseIndex = testAtData.caseIndex
                tmpIndex = tmpTableView.model().index(caseIndex, 4)
                tmpTableView.model().setData(tmpIndex, "FAIL")
                # 颜色设置
                tmpItem = tmpTableView.model().item(caseIndex, 4)
                tmpItem.setForeground(QBrush(QColor(255, 0, 0)))
                tmpItem.setBackground(QBrush(QColor(255, 255, 255)))
            else:
                testAtData.errorStatus = False
                testAtData.rltStatus = True
                testAtData.testData = testKeyData.testData

                # 指令状态设置
                tmpTableView = wndMain.tableView
                caseIndex = testAtData.caseIndex

                tmpIndex = tmpTableView.model().index(caseIndex, 3)
                tmpTableView.model().setData(tmpIndex, "OK")

                tmpItem = tmpTableView.model().item(caseIndex, 3)
                tmpItem.setForeground(QBrush(QColor(0, 255, 0)))
                tmpItem.setBackground(QBrush(QColor(255, 255, 255)))

                # 结果状态设置[功能正常]
                tmpTableView = wndMain.tableView
                caseIndex = testAtData.caseIndex
                tmpIndex = tmpTableView.model().index(caseIndex, 4)
                tmpTableView.model().setData(tmpIndex, "PASS")
                # 颜色设置
                tmpItem = tmpTableView.model().item(caseIndex, 4)
                tmpItem.setForeground(QBrush(QColor(0, 255, 0)))
                tmpItem.setBackground(QBrush(QColor(255, 255, 255)))
        except Exception as e:
            print(repr(e))
        finally:
            testAtData.endTest()

    @classmethod
    def showTestAtCmdInfo(self, testData, retryTimes):
        # 提示测试开始
        self.addTextHint(f"TX->{testData.atCmd} 命令次数=[{retryTimes}]")

    @classmethod
    def showOperateTime(self, testData, waittime):
        self.addTextHint(f"id=[{testData.caseIndex}],人工执行相关操作等待中:({waittime}s)")

    @classmethod
    def showRltConfirmWaitTime(self, testData, waittime):
        self.addTextHint(f"id=[{testData.caseIndex}],人工确认结果等待中:({waittime}s)")

    @classmethod
    def getAtInfoResultValue(self, testData, state, rlts):
        # 得到AT指令显示的结果：
        # 1.成功: OK
        # 2.失败: FAIL
        # 3.指定标识: 需要计算指定的值

        # 获得版信息标记
        Value_Version_Ref = "CMD_PT_GET_SW_INFO"
        # 获得Mac地址标记
        Value_MacAddr_Ref = "CMD_PT_GET_BT_ADDR"
        Pass_Value = "OK"
        Fail_Value = "FAIL"
        if state == True:
            if testData.atRefResult == Value_Version_Ref:
                try:
                    Version_Tag = "Fw_Version:"
                    MacAddr_Tag = "BT Addr:\n"
                    NewLineTag = "\n\n"

                    atRlts = rlts[0]
                    atLen = len(atRlts)
                    print("size=", len(rlts), "atRlts=", atRlts)

                    # 解析版本号的值
                    sVerIdx = atRlts.find(Version_Tag)
                    eVerIdx = atRlts.find(NewLineTag, sVerIdx + len(Version_Tag), atLen)
                    tmpVersion = atRlts[sVerIdx + len(Version_Tag) : eVerIdx]
                    version = tmpVersion.strip()
                    Attest_Config_Data.mFwVersion = version
                    print(f"tmpVersion={tmpVersion} version={version}")

                    # 解析MAC地址值
                    sMacIdx = atRlts.find(MacAddr_Tag)
                    eMacIdx = atRlts.find(NewLineTag, sMacIdx + len(MacAddr_Tag), atLen)
                    tmpMacAddr = atRlts[sMacIdx + len(MacAddr_Tag) : eMacIdx]
                    # 去掉中间的空字符
                    macAddr = tmpMacAddr.replace(" ","")
                    print(f"tmpMacAddr={tmpMacAddr} macAddr={macAddr}")
                    Attest_Config_Data.mMacAddr = macAddr

                    # 显示mac数据
                    self.getView().edtMacAddr.setText(macAddr)

                    # 获得版本信息成功
                    Attest_Config_Data.mGetInfoSuccess = True

                    return Attest_Config_Data.mFwVersion
                except Exception as e:
                    Attest_Config_Data.mGetInfoSuccess = False
                    print("解析版本信息出错:", repr(e))
                return Pass_Value
            elif testData.atRefResult == Value_MacAddr_Ref:
                if Attest_Config_Data.mGetInfoSuccess:
                    return Attest_Config_Data.mMacAddr
                else:
                    return Pass_Value
            else:
                return Pass_Value
        else:
            return Fail_Value

    @classmethod
    def showTestAtCmdResultInfo(self, testData, state, rlts):
        try:
            wndMain = self.getView()
            atValue = self.getAtInfoResultValue(testData, state, rlts)
            # 记录指令结果值[excel文件生成赋值需要]
            testData.atValue = atValue

            if state == True:
                # 指令结果数据
                tmpStr = ""
                for tmpLine in rlts:
                    tmpStr += tmpLine
                testData.testData = tmpStr
                # 指令结果显示
                for tmpRlt in rlts:
                    self.addTextHint(f"RX->{tmpRlt}")

                tmpTableView = wndMain.tableView
                caseIndex = testData.caseIndex
                # 状态设置
                tmpIndex = tmpTableView.model().index(caseIndex, 3)
                tmpTableView.model().setData(tmpIndex, atValue)
                # 颜色设置
                tmpItem = tmpTableView.model().item(caseIndex, 3)
                tmpItem.setForeground(QBrush(QColor(0, 255, 0)))
                tmpItem.setBackground(QBrush(QColor(255, 255, 255)))

                # self.addTextHint(f"{testData.atCmd},发送指令:OK")
                tmpSHint = f"{testData.atCmd},发送指令:" + self.getOKStyle()
                self.addTextHint(tmpSHint)
            else:
                tmpTableView = wndMain.tableView
                caseIndex = testData.caseIndex
                # 状态设置
                tmpIndex = tmpTableView.model().index(caseIndex, 3)
                tmpTableView.model().setData(tmpIndex, atValue)
                # 颜色设置
                tmpItem = tmpTableView.model().item(caseIndex, 3)
                tmpItem.setForeground(QBrush(QColor(255, 0, 0)))
                tmpItem.setBackground(QBrush(QColor(255, 255, 255)))

                #self.addTextHint(f"{testData.atCmd},发送指令:FAIL")
                tmpSHint = f"{testData.atCmd},发送指令:" + self.getFailStyle()
                self.addTextHint(tmpSHint)

                if len(rlts) > 0:
                    if rlts[0] == "#error":
                        # 读取指令结果数据出错
                        info = "读取指令结果出错:\n"
                        info += "请确认:\n"
                        info += "1:串口设备是否正常\n"
                        info += "2:异常原因导致耳机关机\n"
                        info += "3:串口是否被占用了\n"
                        info += "4:其它原因\n"
                        self.addTextHint(info)
                    else:
                        # 能读取到指令的结果数据,但是指令不符合结果标记
                        # 指令结果数据
                        tmpStr = ""
                        for tmpLine in rlts:
                            tmpStr += tmpLine
                        testData.testData = tmpStr
                        # 指令结果显示
                        for tmpRlt in rlts:
                            self.addTextHint(f"RX->{tmpRlt}")
            # 如果按键测试指令发送失败,则所有子项都设置为失败
            if (not state) and Keypress_Test_Data.isKeypressTest(testData.atRefResult):
                tmpTableView = wndMain.tableView
                caseIndex = testData.caseIndex
                for i in range(1, 6):
                    # 指令结果状态
                    tmpIndex = tmpTableView.model().index(caseIndex + i, 3)
                    tmpTableView.model().setData(tmpIndex, "FAIL")
                    tmpItem = tmpTableView.model().item(caseIndex + i, 3)
                    tmpItem.setForeground(QBrush(QColor(255, 0, 0)))
                    tmpItem.setBackground(QBrush(QColor(255, 255, 255)))
                    # 验证结果状态
                    tmpIndex = tmpTableView.model().index(caseIndex + i, 4)
                    tmpTableView.model().setData(tmpIndex, "FAIL")
                    tmpItem = tmpTableView.model().item(caseIndex + i, 4)
                    tmpItem.setForeground(QBrush(QColor(255, 0, 0)))
                    tmpItem.setBackground(QBrush(QColor(255, 255, 255)))
        except Exception as e:
            print(repr(e))

    @classmethod
    def showKeypressOperate(self, testAtData, testKeyData, opType):
        try:
            if opType == "operate":
                # 操作提示
                if testKeyData.caseIndex == 0:
                    self.addTextHint("\n\n")
                    sHint = "按键测试->前置条件:" + "请拔掉串口设备的一根数据线,用于验证按键测试"
                    self.addTextHint(self.getKeyPressTitleStyle(sHint))
                elif (testKeyData.caseIndex >= 1) and (testKeyData.caseIndex <= 5):
                    # 按键测试开始逻辑
                    tmpCaseData = Attest_Case_Data.findCaseData(testAtData.caseIndex + testKeyData.caseIndex)
                    self.keyPressTestStart(tmpCaseData)
                    # 显示状态
                    self.addTextHint("\n\n")
                    sHint = "按键测试->按键操作:" + "请按(%s)1~3次" % Keypress_Test_Data.Key_Values[testKeyData.caseIndex]
                    self.addTextHint(self.getKeyPressTitleStyle(sHint))
                else:
                    self.addTextHint("\n\n")
                    sHint = "按键测试->复位操作:" + "请连接串口设备的一根数据线,才能继续下步测试"
                    self.addTextHint(self.getKeyPressTitleStyle(sHint))
            else:
                # 操作等待时间提示
                if testKeyData.caseIndex == 0:
                    sHint = "前置条件->等待时间:(%d)秒" % testKeyData.opCurWaitTime
                    self.addTextHint(sHint)
                elif (testKeyData.caseIndex >= 1) and (testKeyData.caseIndex <= 5):
                    sHint = "按键操作->等待时间:(%d)秒" % testKeyData.opCurWaitTime
                    self.addTextHint(sHint)
                else:
                    sHint = "复位操作->等待时间:(%d)秒" % testKeyData.opCurWaitTime
                    self.addTextHint(sHint)
        except Exception as e:
            print(repr(e))

    @classmethod
    def showKeypressConfirm(self, testAtData, testKeyData, opType):
        wndMain = self.getView()
        try:
            if opType == "operate":
                if testKeyData.caseIndex == 0:
                    # 操作动作确认
                    sHint = "请确认是否拔掉了串口设备的一根数据线!"
                    answer = QMessageBox.question(wndMain.mMainWindow, '前置条件->操作确认', sHint, QMessageBox.Yes)
                    if answer == QMessageBox.Yes:
                        print("answer->yes0")
                    # 设置确认状态
                    testKeyData.opConfirmed = True
                elif (testKeyData.caseIndex >= 1) and (testKeyData.caseIndex <= 5):
                    sHint = "请确认是否执行了:(按下%s)按键操作!" % Keypress_Test_Data.Key_Values[testKeyData.caseIndex]
                    answer = QMessageBox.question(wndMain.mMainWindow, '按键操作->操作确认', sHint, QMessageBox.Yes)
                    if answer == QMessageBox.Yes:
                        print("answer->yes1")
                    # 执行了按键操作后,需要读取串口数据,用于验证当前按键是否正常
                    print("SUtil.readKeypressResult start")
                    tmpState, tmpRltData = SUtil.readKeypressResult(Attest_Config_Data.mSerObj)
                    print("SUtil.readKeypressResult result:", tmpState, tmpRltData)
                    # 显示读取到的内容
                    if len(tmpRltData) > 0:
                        self.addTextHint("RX->" + tmpRltData)
                    else:
                        self.addTextHint("RX->None!")
                    if tmpState:
                        sRltHint = "按键操作->读取按键结果数据:"
                        self.addTextHint(sRltHint + self.getOKStyle())
                        testKeyData.testData = tmpRltData
                        if testKeyData.rltRefValue in tmpRltData:
                            testKeyData.errorStatus = False
                            sRltHint = "按键操作->验证(%s)按键操作:" % Keypress_Test_Data.Key_Values[testKeyData.caseIndex]
                            self.addTextHint(sRltHint + self.getOKStyle())
                        else:
                            sRltHint = "按键操作->验证(%s)按键操作:" % Keypress_Test_Data.Key_Values[testKeyData.caseIndex]
                            self.addTextHint(sRltHint + self.getFailStyle())
                    else:
                        testKeyData.errorStatus = True
                        sRltHint = "按键操作->读取按键结果数据:"
                        self.addTextHint(sRltHint + self.getFailStyle())
                    testKeyData.opConfirmed = True
                    # 按键结束逻辑
                    tmpCaseData = Attest_Case_Data.findCaseData(testAtData.caseIndex + testKeyData.caseIndex)
                    self.keyPressTestEnd(tmpCaseData, testKeyData)
                else:
                    # 复位动作确认
                    sHint = "请确认是否将串口设备的一根数据线重新连接好!"
                    answer = QMessageBox.question(wndMain.mMainWindow, '复位操作->操作确认', sHint, QMessageBox.Yes)
                    if answer == QMessageBox.Yes:
                        print("answer->yes2")
                    testKeyData.opConfirmed = True
            else:
                # 操作结果确认等待时间提示
                if testKeyData.caseIndex == 0:
                    sHint = "前置条件->操作确认等待:(%d)秒" % testKeyData.opConfirmedCurWaitTime
                    self.addTextHint(sHint)
                elif (testKeyData.caseIndex >= 1) and (testKeyData.caseIndex <= 5):
                    sHint = "按键操作->操作确认等待:(%d)秒" % testKeyData.opConfirmedCurWaitTime
                    self.addTextHint(sHint)
                else:
                    sHint = "复位操作->操作确认等待:(%d)秒" % testKeyData.opConfirmedCurWaitTime
                    self.addTextHint(sHint)
        except Exception as e:
            print(repr(e))

    @classmethod
    def showTestResultConfirm(self, testData):
        wndMain = self.getView()
        # 需要不人工确认结果的用例,由指令结果判断 或者 指令结果失败就不提示人工确认
        if (testData.needConfirm == 0) or testData.errorStatus:
            # 记录按键出错显示状态[用测试状态显示和文件记录保存]
            boIsKeyTestError = False
            # 如果是按键测试,只有所有的按键功能才算通过
            if (not testData.errorStatus) and (Keypress_Test_Data.isKeypressTest(testData.atRefResult)):
                Keypress_Test_Data.mErrorStatus = False
                for tmpIndex in range(1, 6):
                    tmpKeyData = Keypress_Test_Data.mAllCases[tmpIndex]
                    if tmpKeyData.errorStatus:
                        Keypress_Test_Data.mErrorStatus = True
                        break
                # 如果有一项出错,将按键测试结果赋值为False
                if Keypress_Test_Data.mErrorStatus:
                    boIsKeyTestError = True
            # 显示结果状态
            if testData.errorStatus or boIsKeyTestError:
                # 记录结果状态
                testData.rltStatus = False
                # 显示功能异常
                tmpTableView = wndMain.tableView
                caseIndex = testData.caseIndex
                tmpIndex = tmpTableView.model().index(caseIndex, 4)
                tmpTableView.model().setData(tmpIndex, "FAIL")
                # 颜色设置
                tmpItem = tmpTableView.model().item(caseIndex, 4)
                tmpItem.setForeground(QBrush(QColor(255, 0, 0)))
                tmpItem.setBackground(QBrush(QColor(255, 255, 255)))
                # 恢复结果确认状态
                Attest_Config_Data.mRltConfirming = False
            else:
                # 记录结果状态
                testData.rltStatus = True
                # 显示功能异常
                tmpTableView = wndMain.tableView
                caseIndex = testData.caseIndex
                tmpIndex = tmpTableView.model().index(caseIndex, 4)
                tmpTableView.model().setData(tmpIndex, "PASS")
                # 颜色设置
                tmpItem = tmpTableView.model().item(caseIndex, 4)
                tmpItem.setForeground(QBrush(QColor(0, 255, 0)))
                tmpItem.setBackground(QBrush(QColor(255, 255, 255)))
                # 恢复结果确认状态
                Attest_Config_Data.mRltConfirming = False
            return

        try:
            # 提示人工确认
            sHint = f"执行:\n[{testData.atDesc}]\n命令时,功能是否正常?"
            answer = QMessageBox.question(wndMain.mMainWindow, '人工确认', sHint, QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:
                # 记录结果状态
                testData.rltStatus = True
                # 人工确认正常
                tmpTableView = wndMain.tableView
                caseIndex = testData.caseIndex
                tmpIndex = tmpTableView.model().index(caseIndex, 4)
                tmpTableView.model().setData(tmpIndex, "PASS")
                # 颜色设置
                tmpItem = tmpTableView.model().item(caseIndex, 4)
                tmpItem.setForeground(QBrush(QColor(0, 255, 0)))
                tmpItem.setBackground(QBrush(QColor(255, 255, 255)))
            else:
                # 记录结果状态
                testData.rltStatus = False
                # 人工确认异常
                tmpTableView = wndMain.tableView
                caseIndex = testData.caseIndex
                tmpIndex = tmpTableView.model().index(caseIndex, 4)
                tmpTableView.model().setData(tmpIndex, "FAIL")
                # 颜色设置
                tmpItem = tmpTableView.model().item(caseIndex, 4)
                tmpItem.setForeground(QBrush(QColor(255, 0, 0)))
                tmpItem.setBackground(QBrush(QColor(255, 255, 255)))
        except Exception as e:
            print(repr(e))
        finally:
            Attest_Config_Data.mRltConfirming = False

    @classmethod
    def showQrCodeForMacAddr(self):
        try:
            wndMain = self.getView()
            if Attest_Config_Data.mGetInfoSuccess == 1:
                # 设置居中显示
                # wndMain.lblQrcode.setAlignment(PyQt5.Qt.AlignCenter)

                macAddr = Attest_Config_Data.mMacAddr
                # 生成二维码对象
                qrMake = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=4, border=2)
                # 编码
                qrMake.add_data(macAddr)
                qrMake.make(fit=True)
                # 生成图片
                imgQrcode = qrMake.make_image(image_factory=PyPNGImage)

                # 显示二维码[从内存中加载]
                # tmpImage = QImage("./qrcode/test.png")
                tmpStream = BytesIO()
                imgQrcode.save(tmpStream, "PNG")
                tmpStream.seek(0)
                tmpBts = tmpStream.read()
                # 从字节数组创造图片对象
                tmpImage = QImage.fromData(tmpBts)
                wndMain.lblQrcode.setPixmap(QPixmap.fromImage(tmpImage))
                wndMain.lblQrcode.resize(tmpImage.width(), tmpImage.height())
                wndMain.lblQrcode.setVisible(True)
            else:
                wndMain.lblQrcode.setVisible(False)
        except Exception as e:
            print(repr(e))

    @classmethod
    def endTestProcess(self, state):
        try:
            wndMain = self.getView()

            # 显示测试时间
            timeNow = time.time()
            tinfo = time.strftime("%Y%m%d-%H:%M:%S", time.localtime(timeNow))
            Attest_Config_Data.mEndTime = timeNow
            wndMain.edtEndTime.setText(tinfo)
            # 显示持续时间
            dtime = Attest_Config_Data.mEndTime - Attest_Config_Data.mStarTime
            wndMain.edtDurTime.setText("%.2f(s)" % dtime)

            # 正常的结束测试逻辑
            if state == "success":
                # 显示当前全测试结果状态
                isError = False
                for tmpData in Attest_Case_Data.mAllCases:
                    if not tmpData.rltStatus:
                        isError = True
                        break
                if isError:
                    wndMain.lblTestRlt.setStyleSheet("color:red")
                    wndMain.lblTestRlt.setText("FAIL")
                    wndMain.lblTestRlt.setVisible(True)
                else:
                    wndMain.lblTestRlt.setStyleSheet("color:blue")
                    wndMain.lblTestRlt.setText("PASS")
                    wndMain.lblTestRlt.setVisible(True)

                # 修改按钮状态
                wndMain.btnEndTest.setEnabled(False)
                wndMain.btnTestAll.setEnabled(True)

                # 记录全测试一轮状态
                Attest_Config_Data.mSuccessState = 1
                # 生成二维码显示
                self.showQrCodeForMacAddr()

                # 等待线程停止
                if Attest_Config_Data.mTestThread != None:
                    Attest_Config_Data.mTestThread.wait()
                    Attest_Config_Data.mTestThread = None

                # 停止串口对象
                if Attest_Config_Data.mSerObj != None:
                    Attest_Config_Data.mSerObj.close()
                    Attest_Config_Data.mSerObj = None
            # 测试手动停止
            else:
                wndMain.lblTestRlt.setStyleSheet("color:red")
                wndMain.lblTestRlt.setText("FAIL")

                # 修改按钮状态
                wndMain.btnEndTest.setEnabled(False)
                wndMain.btnTestAll.setEnabled(True)

                # 等待线程停止
                if Attest_Config_Data.mTestThread != None:
                    Attest_Config_Data.mTestThread.wait()
                    Attest_Config_Data.mTestThread = None

                # 停止串口对象
                if Attest_Config_Data.mSerObj != None:
                    Attest_Config_Data.mSerObj.close()
                    Attest_Config_Data.mSerObj = None

                # 设置信息信号状态为False
                Attest_Config_Data.mStopSignal = False
        except Exception as e:
            print("endTestProcess.error?", repr(e))
        finally:
            # 清除数据状态
            Attest_Config_Data.mObserver = None
            Attest_Config_Data.mRltConfirming = False
            Attest_Config_Data.mIsTesting = False

        # 正常的结束测试逻辑,自动数据到文件
        if state == "success":
            self.on_btn_savedata()

    @classmethod
    def on_btn_testall(self):
        # print("on_btn_testall")
        if PortConfig_Data.mIsOpen:
            self.showWarningInfo("请关闭主界面的串口,防止串口被占用的冲突!")
            return

        isOk = self.validateComData()
        if not isOk:
            print("条件不足,无法执行测试用例!")
            return
        if Attest_Config_Data.mIsTesting:
            self.showWarningInfo("正在测试中...")
            return

        try:
            wndMain = self.getView()

            # 水平滑动条最右显示
            # 此方法在点击事件内起作用,但在initDataView方法内不起作用(???)
            hbar = wndMain.tableView.horizontalScrollBar()
            if hbar.value() < 2:
                hbar.setValue(2)

            # 设置测试状态
            Attest_Config_Data.mIsTesting = True
            Attest_Config_Data.mStopSignal = False
            Attest_Config_Data.mSuccessState = 0

            # 设置按钮状态
            wndMain.btnTestAll.setEnabled(False)
            wndMain.btnEndTest.setEnabled(True)
            # 隐藏测试结果状态
            wndMain.lblTestRlt.setVisible(False)
            # 隐藏二维码图片
            wndMain.lblQrcode.setVisible(False)

            # 清空指令结果信息
            wndMain.edtHint.clear()
            # 复位测试数据[所有测试用例]
            for tmpData in Attest_Case_Data.mAllCases:
                tmpData.resetData()
            # 复位测试数据[按键测试用例]
            Keypress_Test_Data.resetData()

            # 恢复显示状态
            wndMain.lblTestRlt.setStyleSheet("color:gray")
            wndMain.lblTestRlt.setText("none")
            # 表格UI复位
            max_row = len(self.mAtLst)
            tmpTableView = wndMain.tableView
            for rowIndex in range(1, max_row):
                # 指令结果
                tmpIndex1 = tmpTableView.model().index(rowIndex, 3)
                tmpTableView.model().setData(tmpIndex1, "None")
                tmpItem1 = tmpTableView.model().item(rowIndex, 3)
                tmpItem1.setForeground(QBrush(QColor(0, 0, 0)))
                tmpItem1.setBackground(QBrush(QColor(255, 255, 255)))
                # 验证结果
                tmpIndex2 = tmpTableView.model().index(rowIndex, 4)
                tmpTableView.model().setData(tmpIndex2, "待验证")
                tmpItem2 = tmpTableView.model().item(rowIndex, 4)
                tmpItem2.setForeground(QBrush(QColor(0, 0, 0)))
                tmpItem2.setBackground(QBrush(QColor(255, 255, 255)))

            # 显示开始测试时间
            timeNow = time.time()
            tinfo = time.strftime("%Y%m%d-%H:%M:%S", time.localtime(timeNow))
            wndMain.edtStrtTime.setText(tinfo)
            Attest_Config_Data.mStarTime = timeNow

            print("先打开串口操作...")
            if Attest_Config_Data.mSerObj != None:
                Attest_Config_Data.mSerObj.close()
                Attest_Config_Data.mSerObj = None
            serObj = SUtil.openSerialCom(Attest_Config_Data.mComNum, Attest_Config_Data.mBaudrate, Attest_Config_Data.mTimeOut)
            Attest_Config_Data.mSerObj = serObj

            print("开启测试线程...")
            Attest_Config_Data.mObserver = self
            Attest_Config_Data.mTestThread = MyProcessThread()
            Attest_Config_Data.mTestThread.call_fun_signal.connect(self.solveUiProcess)
            Attest_Config_Data.mTestThread.start()
        except Exception as e:
            print(repr(e))
            Attest_Config_Data.mIsTesting = False

    @classmethod
    def validateComData(self):
        wndMain = self.getView()
        # 分析串口类型
        index = wndMain.cmbNumSlt.currentIndex()
        if index == 0:
            self.showWarningInfo("请选择串口类型!")
            return False
        # 记录串口类型
        Attest_Config_Data.mComNum = wndMain.cmbNumSlt.itemText(index)

        # 分析波特率
        index = wndMain.cmbBaudrateSlt.currentIndex()
        if index == 0:
            self.showWarningInfo("请选择波特率类型!")
            return False
        Attest_Config_Data.mBaudrate = int(wndMain.cmbBaudrateSlt.itemText(index))

        # 分析测试用例是否有数据
        if not Attest_Case_Data.validateCaseData():
            self.showWarningInfo("测试指令数据为空,请加载测试数据!")
            return False

        return True

    @classmethod
    def on_btn_savedata(self):
        # print("on_btn_savedata...")
        if Attest_Config_Data.mIsTesting:
            self.showInformationInfo("当前正在测试中,不能保存数据!")
            return

        if Attest_Config_Data.mSuccessState != 1:
            self.showInformationInfo("当前没有成功执行完所有测试,不能保存数据!")
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

        wndMain = self.getView()

        # 文件名格式：产品类型_Mac地址_时间
        macAddr = "none"
        modelType = wndMain.edtModelType.text()
        fname_tag = f"%s-%s-%s" % (modelType, macAddr, tinfo)
        if Attest_Config_Data.mGetInfoSuccess:
            fname_tag = f"%s-%s-%s" % (modelType, Attest_Config_Data.mMacAddr, tinfo)

        # 保存指令数据到日志文件
        logFileName = subdir + "\\" + f"{fname_tag}.txt"
        txtFile = open(logFileName, "w+")
        atLogs = self.getView().edtHint.toPlainText()
        txtFile.write(atLogs)
        txtFile.flush()
        txtFile.close()

        # 保存测试数据到excel文件
        exeFileName = subdir + "\\" + f"{fname_tag}.xlsx"
        dts = dict()
        dts["startTime"] = wndMain.edtStrtTime.text()
        dts["endTime"] = wndMain.edtEndTime.text()
        dts["duration"] = wndMain.edtDurTime.text()
        dts["testPlat"] = wndMain.edtTestPlat.text()
        dts["jobId"] = wndMain.edtJobId.text()
        dts["modelType"] = wndMain.edtModelType.text()
        dts["macAddr"] = wndMain.edtMacAddr.text()
        dts["status"] = wndMain.lblTestRlt.text()
        dts["data"] = Attest_Case_Data.mAllCases
        Excel_Writer.saveToFile(exeFileName, dts)

        # 提示保存文件成功
        self.showInformationInfo(f"成功保存日志文件:\n{logFileName}\n测试结果文件:\n{exeFileName}")

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
        wndMain.cmbBaudrateSlt.setCurrentIndex(len(Baudrates) - 1)

        # 串口选项
        wndMain.cmbNumSlt.addItem("None")
        # 设置默认选项
        wndMain.cmbNumSlt.setCurrentIndex(0)

    # 初始化按钮事件
    @classmethod
    def initEvents(self):
        # 添加选择项
        self.addCmbItems()

        wndMain = self.mView
        # 设置标题颜色
        wndMain.lblTitle.setStyleSheet("color:blue")
        # wndMain.lblTitle.setStyleSheet("QLabel{background-color:gray;}")
        wndMain.lblTestRlt.setStyleSheet("color:gray")

        # 添加按钮事件
        wndMain.btnLoad.clicked.connect(self.on_btn_load)
        wndMain.btnComFresh.clicked.connect(self.on_btn_comfresh)
        wndMain.btnTestAll.clicked.connect(self.on_btn_testall)
        wndMain.btnSaveData.clicked.connect(self.on_btn_savedata)
        wndMain.btnEndTest.clicked.connect(self.on_stop_test)

        # 设置按钮状态
        wndMain.btnTestAll.setEnabled(True)
        wndMain.btnEndTest.setEnabled(False)
        wndMain.btnSaveData.setEnabled(False)
        # 隐藏测试结果状态
        wndMain.lblTestRlt.setVisible(False)
        # 隐藏二维码图片
        wndMain.lblQrcode.setVisible(False)

        # 清除数据
        Attest_Config_Data.clearData()

        # 加载数据
        self.on_btn_load()

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
        return Attest_Manager.mView

    @classmethod
    def solveUiProcess(self, fname, params):
        try:
            # print("fname=", fname)
            if fname == "showTestStartInfo":
                self.showTestStartInfo(params[0])
            elif fname == "showTestAtCmdInfo":
                self.showTestAtCmdInfo(params[0], params[1])
            elif fname == "showOperateTime":
                self.showOperateTime(params[0], params[1])
            elif fname == "showTestAtCmdResultInfo":
                self.showTestAtCmdResultInfo(params[0], params[1], params[2])
            elif fname == "showKeypressOperate":
                self.showKeypressOperate(params[0], params[1], params[2])
            elif fname == "showKeypressConfirm":
                self.showKeypressConfirm(params[0], params[1], params[2])
            elif fname == "showRltConfirmWaitTime":
                self.showRltConfirmWaitTime(params[0], params[1])
            elif fname == "showTestResultConfirm":
                self.showTestResultConfirm(params[0])
            elif fname == "endTestProcess":
                self.endTestProcess(params[0])
        except Exception as e:
            print("solveUiProcess.error?", repr(e))

    @classmethod
    def onWindowCloseEvent(self, event):
        print("attest_manager.onWindowCloseEvent...")
        if Attest_Config_Data.mIsTesting:
            sinfo = "当前正在执行指令功能测试,是否放弃测试?"
            answer = QMessageBox.question(self.getView().mMainWindow, '确认', sinfo, QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:
                # 这里需要设置停止信号状态
                Attest_Config_Data.mStopSignal = True
                # 异常结果测试逻辑
                self.endTestProcess("except")
                # 接受窗体关闭事件
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    @classmethod
    def addTextHint(self, sHint):
        wndMain = self.getView()
        wndMain.edtHint.append(sHint)

        # 测试开始时,滑动到最低端显示[用于提示当前测试用例]
        hVerticalBar = wndMain.edtHint.verticalScrollBar()
        if hVerticalBar:
            curValue = hVerticalBar.value()
            # minValue = hVerticalBar.minimum()
            maxValue = hVerticalBar.maximum()
            # print(f"cValue={curValue} minValue={minValue}, maxValue={maxValue}")
            if curValue < maxValue:
                hVerticalBar.setValue(maxValue)

    @classmethod
    def getTitleStyle(self, sHint):
        titleFormat = '<b><font color="#0000FF" size="4">{}</font></b>'
        return titleFormat.format(sHint)

    @classmethod
    def getKeyPressTitleStyle(self, sHint):
        titleFormat = '<b><font color="#0000FF" size="3">{}</font></b>'
        return titleFormat.format(sHint)

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