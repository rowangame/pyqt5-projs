# -*- coding: utf-8 -*-

# 测试配置参数对象


class Attest_Config_Data:
    # 串口
    mComNum = None
    # 波特率
    mBaudrate = 0
    # 超时时间
    mTimeOut = 1.5
    # 串口对象
    mSerObj = None

    # 测试状态
    mIsTesting = False

    # 开始时间
    mStarTime = 0.0
    # 结束时间
    mEndTime = 0.0
    # 测试耗时
    mDuration = 0

    # 观查者对象
    mObserver = None
    # 测试线程
    mTestThread = None
    # 结果人工确认状态
    mRltConfirming = False

    # 人工关闭信号
    mStopSignal = False

    # 正常测试结束标记(用于保存数据)
    mSuccessState = 0

    # 是否成功获得了产品版本信息和mac地址信息[用于保存对应的文件]
    mGetInfoSuccess = False

    # 固件版本号[用于区分设备信息]
    mFwVersion = "0.0.0.0"

    # 产品MAC:
    mMacAddr = "none"

    @classmethod
    def clearData(self):
        self.mComNum = None
        self.mBaudrate = 0
        self.mTimeOut = 1.5
        self.mSerObj = None
        self.mIsTesting = False

        self.mStarTime = 0.0
        self.mEndTime = 0.0
        self.mDuration = 0

        self.mObserver = None
        self.mTestThread = None
        self.mRltConfirming = False

        self.mStopSignal = False
        self.mSuccessState = 0
        self.mGetInfoSuccess = False
        self.mFwVersion = "0.0.0.0"
        self.mMacAddr = "none"
