# -*- coding: utf-8 -*-
# 因子线程会阻塞UI主线程,导致UI程序卡死,因止使用QThread线程来执行费时间的逻辑
# 此线程只能关联在Pyqt5内使用,否则不起用

import time
from PyQt5.QtCore import QThread, pyqtSignal

from attest_case_data import Attest_Case_Data, Keypress_Test_Data
import serial_util as SUtil

from attest_config_data import Attest_Config_Data

class MyProcessThread(QThread):
    call_fun_signal = pyqtSignal(str, list)  # 信号类型:str, list

    def __init__(self,parent = None):
        super(MyProcessThread, self).__init__(parent)

    def run(self):
        Max_RetryTimes = 3
        # 全指令测试
        All_Test_Size = len(Attest_Case_Data.mAllCases)
        for tmpIndex in range(All_Test_Size):
            # 如果有停止状态,则退出测试1
            if Attest_Config_Data.mStopSignal:
                print("有停止状态信号,退出测试1")
                return

            # 获得测试用例数据
            tmpAtData = Attest_Case_Data.mAllCases[tmpIndex]
            # 这里需要跳过子按键测试数据
            if Keypress_Test_Data.isBubKeypressType(tmpAtData.atRefResult):
                continue
            tmpAtData.startTest()

            # 开始测试提示
            self.call_fun_signal.emit("showTestStartInfo", [tmpAtData])
            lasttick = int(time.time())
            # 指令发送
            for tmpTimes in range(Max_RetryTimes):
                if Attest_Config_Data.mStopSignal:
                    print("有停止状态信号,退出测试2")
                    return

                # 验证AT指令功能
                tmpAtData.retryTimes += 1

                # 指令发送提示
                self.call_fun_signal.emit("showTestAtCmdInfo",[tmpAtData, tmpAtData.retryTimes])
                state, rlts = SUtil.sendATByHexBaseEx(tmpAtData.atCmd, Attest_Config_Data.mSerObj, "")
                # 因指令格式问题,需要需要判断关闭按键测试的特殊情况
                if (not state) and (Keypress_Test_Data.isStopKeypressTest(tmpAtData.atRefResult)):
                    if (len(rlts) > 0) and (Keypress_Test_Data.Stop_Success_Tag in rlts[0]):
                        state = True
                # 指令结果提示
                self.call_fun_signal.emit("showTestAtCmdResultInfo", [tmpAtData, state, rlts])
                if state == True:
                    tmpAtData.errorStatus = False
                    # 判断是否是按键测试,设置按键测试状态
                    if Keypress_Test_Data.isKeypressTest(tmpAtData.atRefResult):
                        # 复位数据
                        Keypress_Test_Data.resetData()
                        # 设置测试状态
                        Keypress_Test_Data.mIsTesting = True
                        # 设置按键操作索引值
                        Keypress_Test_Data.mTestIndex = 0
                    break

            # 如果为按键测试逻辑,则需要执行按键测试流程
            if Keypress_Test_Data.mIsTesting:
                while True:
                    if Attest_Config_Data.mStopSignal:
                        print("有停止状态信号,退出按键测试3")
                        return
                    tmpKeyData = Keypress_Test_Data.mAllCases[Keypress_Test_Data.mTestIndex]
                    # 操作等待时间
                    if tmpKeyData.opCurWaitTime < tmpKeyData.opMaxWaitTime:
                        if tmpKeyData.opHintTimes == 0:
                            tmpKeyData.opHintTimes += 1
                            # 操作提示
                            self.call_fun_signal.emit("showKeypressOperate", [tmpAtData, tmpKeyData, "operate"])
                        # 操作等待时间增加
                        time.sleep(1)
                        tmpKeyData.opCurWaitTime += 1
                        # 操作等待时间提示
                        self.call_fun_signal.emit("showKeypressOperate", [tmpAtData, tmpKeyData, "hint"])

                    # 执行操作结果确认
                    if tmpKeyData.opCurWaitTime >= tmpKeyData.opMaxWaitTime:
                        if not tmpKeyData.opConfirmed:
                            if tmpKeyData.opConfirmedHintTimes == 0:
                                tmpKeyData.opConfirmedHintTimes += 1
                                # 操作结果确认
                                self.call_fun_signal.emit("showKeypressConfirm", [tmpAtData, tmpKeyData, "operate"])
                            time.sleep(1)
                            tmpKeyData.opConfirmedCurWaitTime += 1
                            # 操作结果确认等待时间提示
                            self.call_fun_signal.emit("showKeypressConfirm",[tmpAtData, tmpKeyData, "hint"])
                        else:
                            # 执行下一步操作
                            Keypress_Test_Data.mTestIndex += 1
                            # 按键操作流程是否结束
                            if Keypress_Test_Data.isOperateNeedEnd():
                                # 按键测试状态设置为False
                                Keypress_Test_Data.mIsTesting = False
                                break

            # 等等几秒钟时间，用于人工确认功能是否正常
            curttick = int(time.time())
            dtime = curttick - lasttick
            waittime = tmpAtData.opWaitTime - dtime
            boNeedSend = True
            while waittime > 0:
                if Attest_Config_Data.mStopSignal:
                    print("有停止状态信号,退出测试3")
                    return
                if boNeedSend:
                    boNeedSend = False
                    # 人工执行相关操作等待中
                    self.call_fun_signal.emit("showOperateTime", [tmpAtData, waittime])
                time.sleep(1)
                waittime -= 1

            # 设置结果状态为确认中
            Attest_Config_Data.mRltConfirming = True
            tmpWaitTime = 0

            # 指令功能人工确认
            self.call_fun_signal.emit("showTestResultConfirm", [tmpAtData])

            # 设置结果状态为确认中
            while True:
                if Attest_Config_Data.mStopSignal:
                    print("有停止状态信号,退出测试4")
                    return
                if not Attest_Config_Data.mRltConfirming:
                    break
                time.sleep(1)
                # 每隔几秒钟提示一次
                if tmpWaitTime % 5 == 0:
                    # 人工确认结果等待中
                    self.call_fun_signal.emit("showRltConfirmWaitTime", [tmpAtData, tmpWaitTime])
                # 等待时间累加
                tmpWaitTime += 1

            # 结束测试
            tmpAtData.endTest()

        # 测试结束
        print("测试结束...")
        self.call_fun_signal.emit("endTestProcess", ["success"])