# -*- coding: utf-8 -*-

# 串口配置参数对象
import time


class PortConfig_Data:
    mComNum = None
    mBaudrate = 0
    mIsOpen = False
    mTimeOut = 1.5
    mSerObj = None
    mReadThread = None
    mReadState = False
    mStopSignal = False
    mObserver = None

    @classmethod
    def clearData(self):
        self.mComNum = None
        self.mBaudrate = 0
        self.mIsOpen = False
        self.mTimeOut = 1.5
        self.mSerObj = None
        self.mReadThread = None
        self.mStopSignal = False
        self.mObserver = None

    @classmethod
    def stopReadProcess(self):
        self.mStopSignal = True
        PortConfig_Data.mReadThread.join()
        PortConfig_Data.mReadThread = None
        self.mStopSignal = False

    @classmethod
    def readProcess(self, value, observer):
        print("readProcess...", value, type(observer))
        while True:
            if self.mStopSignal:
                break
            time.sleep(1)
            try:
                if PortConfig_Data.mSerObj.in_waiting:
                    response = PortConfig_Data.mSerObj.read(PortConfig_Data.mSerObj.in_waiting).decode("gbk")
                    # print("RX->", response)
                    if self.mObserver:
                        self.mObserver.on_read_data(response)
            except Exception as e:
                print("readProcess error?" + repr(e))

