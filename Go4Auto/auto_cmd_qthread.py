
# -*- coding: utf-8 -*-
# 因子线程会阻塞UI主线程,导致UI程序卡,因止使用QThread线程来执行费时间的逻辑
# 此线程只能关联在Pyqt5内使用,否则不起用

from PyQt5.QtCore import QThread, pyqtSignal
import time

import serial.tools.list_ports
import bo4_cache_data
import serial_util as SUtil
from bo4_cache_data import Uart_Data


class MyProcessQThread(QThread):
    call_fun_signal = pyqtSignal(tuple)  # 信号类型:tuple

    mSerObj = None
    mAutoThread = None
    mStopSignal = False
    mObserver = None
    mRunning = False

    # 串口可用状态列表
    mLstCmdData: list[bo4_cache_data.Com_Data] = []
    # 测试设备数据列表
    mLstDevData: list[bo4_cache_data.Device_Data] = []
    # 通知更换设备提示
    mNoticeTag = False
    # 等待时间
    mMaxWaitTime = 5
    # 运行次数
    mRunTimes = 0

    @classmethod
    def clearData(cls):
        cls.mSerObj = None
        cls.mAutoThread = None
        cls.mStopSignal = False
        cls.mObserver = None
        cls.mRunning = False
        cls.mLstCmdData.clear()
        cls.mLstDevData.clear()
        cls.mNoticeTag = False
        cls.mRunTimes = 0

    @classmethod
    def stopAutoProcess(cls):
        cls.mStopSignal = True
        MyProcessQThread.mAutoThread.wait()
        MyProcessQThread.mAutoThread = None
        cls.mStopSignal = False

    @classmethod
    def existsComName(cls, comName):
        size = len(cls.mLstCmdData)
        if size > 0:
            for i in range(size):
                if cls.mLstCmdData[i].comName == comName:
                    return True, i
        return False, -1

    @classmethod
    def getDeviceDataByMac(cls, macAddr):
        for tmpDev in cls.mLstDevData:
            if tmpDev.macAddr == macAddr:
                return True, tmpDev
        return False, None

    @classmethod
    def closeSerial(cls):
        try:
            if cls.mSerObj != None:
                cls.mSerObj.close()
                return True
        except Exception as e:
            print("关闭串口出错:")
            print(repr(e))
            return False
        finally:
            cls.mSerObj = None

    def __init__(self, parent=None):
        super(MyProcessQThread, self).__init__(parent)

    def run(self):
        print("autoCmdProcess...")
        MyProcessQThread.mRunning = True
        print("self.id", id(self.mRunning), "MyProcessQThread.id", id(MyProcessQThread.mRunning))
        print("self.mRunning", self.mRunning, "MyProcessQThread.mRunning", MyProcessQThread.mRunning)
        while True:
            if self.mStopSignal:
                break

            # 第一次运行(不等待)
            if self.mRunTimes > 0:
                # 串口刷新等待时间(成功发送了指令则不计入等待时间状态)
                print("Wait time:%d(s)" % self.mMaxWaitTime)
                for i in range(self.mMaxWaitTime):
                    if self.mStopSignal:
                        break
                    time.sleep(1)
            self.mRunTimes += 1

            # step1: 刷新串口数据
            plist = list(serial.tools.list_ports.comports())
            if len(plist) == 0:
                print("Empty com, try to refresh com")
                continue

            # step2: 向串口发送数据,分析是否有回应
            for tmpP in plist:
                try:
                    if self.mStopSignal:
                        break
                    isDone = False
                    Uart_Data.mComNum = tmpP.name
                    # 分析串口是否存在于列表中(如果存在于列表中,则分析是否可用;如果不可用,则等待)
                    boExists, index = self.existsComName(tmpP.name)
                    if boExists:
                        comData = self.mLstCmdData[index]
                        if not comData.cmdOK:
                            if not comData.canRetry():
                                continue
                    else:
                        comData = bo4_cache_data.Com_Data()
                        comData.comName = tmpP.name
                        comData.testStartTime = time.time()
                        comData.cmdOK = False
                        self.mLstCmdData.append(comData)
                    # 记录开始测试的时间
                    comData.testStartTime = time.time()

                    try:
                        # 关闭当前串口(防止被占用的错误的情况,或者其它异常情况)
                        boClosedTag = self.closeSerial()
                        if boClosedTag:
                            time.sleep(1)
                        # 打开串口
                        serObj = SUtil.openSerialCom(Uart_Data.mComNum, Uart_Data.mBaudrate, Uart_Data.mTimeOut)
                        MyProcessQThread.mSerObj = serObj
                    except Exception as e:
                        print("Error,打开串口异常...")
                        print(repr(e))
                        # 串口异常,继续使用其它串口
                        continue

                    # 获取蓝牙地址(以蓝牙地址作为唯一标记)
                    boSuccess, rlt = SUtil.sendATByHexBaseEx(bo4_cache_data.Cmd_Data.AT_GetMac, MyProcessQThread.mSerObj,
                                                             "success")
                    print(boSuccess, rlt)

                    # 如果获取蓝牙地址成功,则发送进入RF测试指令
                    if boSuccess:
                        comData.cmdOK = True
                        self.mNoticeTag = True
                        macValue = bo4_cache_data.Cmd_Data.getMacValue(rlt[0])
                        print("macValue:", macValue)

                        info = ("comInfo", comData.comName, True, f"可用.成功获取设备MAC地址:{macValue}!")
                        self.call_fun_signal.emit(info)

                        # 分析是否重复进入RF产测指令
                        boFound, curDevice = self.getDeviceDataByMac(macValue)
                        if not boFound:
                            # 如果当前设备数据量过大,则保存数据到日志中,并删除当前数据
                            dataLen = len(self.mLstDevData)
                            if dataLen > bo4_cache_data.Device_Data.Max_Device_Cnt:
                                # 保存到日志文件中
                                if self.mObserver != None:
                                    self.mObserver.saveToExcelFile()
                                    print("清除列表.")
                                    self.mLstDevData.clear()

                            # 不存在当前设备,则将当前设备添加到列表中
                            curDevice = bo4_cache_data.Device_Data()
                            curDevice.index = len(self.mLstDevData) + 1
                            curDevice.macAddr = macValue
                            curDevice.processOk = False
                            self.mLstDevData.append(curDevice)
                        else:
                            if curDevice.processOk:
                                print(f"设备已经成功进入RF产测状态,不需要再次发送指令")
                                self.mNoticeTag = False
                                info = ("change", self.mMaxWaitTime)
                                self.call_fun_signal.emit(info)
                                continue

                        # 发送进入RF测试指令
                        stateEx, rltEx = SUtil.sendATByHexBaseEx(bo4_cache_data.Cmd_Data.AT_SetRfMode,
                                                                 MyProcessQThread.mSerObj, "success")
                        print(stateEx, rltEx)
                        if stateEx:
                            print(f"{comData.comName}可用,指令发送成功!")
                            isDone = True
                            curDevice.processOk = True
                            info = ("at", curDevice)
                            self.call_fun_signal.emit(info)
                        else:
                            print(f"{comData.comName}可用,发送(进入RF产测)指令失败!")
                            isDone = False
                            curDevice.processOk = False
                            info = ("at", curDevice)
                            self.call_fun_signal.emit(info)
                    else:
                        print(f"{comData.comName}不可用.等待一段时间后,尝试再测试!")
                        comData.cmdOK = False
                        info = ("comInfo", comData.comName, False,
                                f"不可用.等待({bo4_cache_data.Com_Data.RetryWaitTime})秒后,尝试再测试!")
                        self.call_fun_signal.emit(info)

                    # 分析执行成功的状态
                    if isDone:
                        if self.mNoticeTag:
                            self.mNoticeTag = False
                            info = ("change", self.mMaxWaitTime * 2)
                            self.call_fun_signal.emit(info)
                        # 等待几秒种,用于测试员可以更换设备
                        for i in range(self.mMaxWaitTime):
                            if self.mStopSignal:
                                break
                            time.sleep(1)
                        # 有一个串口数据能执行成功，就不要处理其它串口了
                        break
                except Exception as e:
                    print(repr(e))
                finally:
                    # 关闭当前串口(防止被占用的错误的情况)
                    self.closeSerial()

        # 结束标记状态
        MyProcessQThread.mRunning = False