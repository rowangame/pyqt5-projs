# -*- coding: utf-8 -*-

import time

# 按键测试单元类
class Keypress_Case_Data:
    def __init__(self):
        # 测试用例索引值
        self.caseIndex = -1
        # 按键值
        self.keyValue = ""
        # 按键结果参考值
        self.rltRefValue = ""
        # 按键操作最大等待时间
        self.opMaxWaitTime = 0

        # 当前操作等待时间[用于执行操作的等待时间]
        self.opCurWaitTime = 0
        # 发送操作提示次数记录
        self.opHintTimes = 0
        # 操作结果是否确认[只确认过操作结果,才能执行下一步操作]
        self.opConfirmed = False
        # 操作结果提示次数记录
        self.opConfirmedHintTimes = 0
        # 当前操作结果等待确认时间[用于提示操作确认的等待时间]
        self.opConfirmedCurWaitTime = 0

        # 重试次数
        self.retryTimes = 0
        # 按键结果状态值
        self.errorStatus = True
        # 按键结果数值
        self.testData = ""

    def resetData(self):
        self.opCurWaitTime = 0
        self.opHintTimes = 0
        self.opConfirmed = False
        self.opConfirmedHintTimes = 0
        self.opConfirmedCurWaitTime = 0

        self.retryTimes = 0
        self.errorStatus = True
        self.testData = ""

# 按键测试数据类
class Keypress_Test_Data:
    # 按键类型值[通过此值判断是否为按键操作]
    KeyType_Value = "CMD_PT_KEY_TEST_START"
    # 关闭按键测试
    Stop_KeyType_Value = "CMD_PT_KEY_TEST_STOP"
    # 成功结束标记
    Stop_Success_Tag = "CMD_KEY_TEST stop"
    # 子按键测试标记
    Sub_KeyType_Value = "SUB_PT_KEY_TEST"
    # 子按键指令值设定
    Sub_KeyType_Cmd_Value = "None"
    # 子按键测试描述
    Sub_KeyType_Descs = ["Power键测试", "Anc键测试", "Mfb键测试", "Vol+键测试", "Vol-键测试"]

    # 操作等待时间(秒)
    Operate_Times = [10, 8, 8, 8, 8, 8, 10]
    # 按键枚举值
    Key_Values = ["拔掉数据线提示", "电源键", "Anc键", "Mfb键", "音量+键", "音量-键", "连接数据线提示"]
    # 按键结果参考值
    Key_Results = ["Operate","Power key ok!","anc key ok!", "mfb key ok!", "Volume Up key ok!", "Volume Down key ok!", "Operate"]

    # 所有按键测试用例
    mAllCases = []

    # 是否在测试状态中
    mIsTesting = False
    # 当前按键测试的索引值
    mTestIndex = -1
    # 按键结果状态[只要有一个按键不符合要求,则结果为出错状态]
    mErrorStatus = True

    @classmethod
    def resetData(self):
        self.mIsTesting = False
        self.mTestIndex = -1
        self.mErrorStatus = True
        # 复位用例数据
        if len(self.mAllCases) > 0:
            for tmpCaseData in self.mAllCases:
                tmpCaseData.resetData()

    @classmethod
    def initKeypressTestData(self):
        for i in range(len(self.Key_Values)):
            tmpCaseData = Keypress_Case_Data()
            tmpCaseData.caseIndex = i
            tmpCaseData.keyValue = self.Key_Values[i]
            tmpCaseData.rltRefValue = self.Key_Results[i]
            tmpCaseData.opMaxWaitTime = self.Operate_Times[i]
            self.mAllCases.append(tmpCaseData)

    @classmethod
    def isOperateNeedEnd(self):
        return self.mTestIndex >= len(self.Key_Values)

    @classmethod
    def isKeypressTest(self, atRefResult):
        return Keypress_Test_Data.KeyType_Value == atRefResult

    @classmethod
    def isBubKeypressType(self, atRefResult):
        return Keypress_Test_Data.Sub_KeyType_Value == atRefResult

    @classmethod
    def isStopKeypressTest(self, atRefResult):
        return Keypress_Test_Data.Stop_KeyType_Value == atRefResult

# 测试用例单元数据
class TestCase_Data(object):
    def __init__(self):
        # 测试用例索引值
        self.caseIndex = -1
        # 指令出错状态
        self.errorStatus = True
        # 指令结果值OK,FAIL,其它特定值
        self.atValue = ""
        # 开始时间
        self.startTime = ""
        # 结束时间
        self.endTime = ""
        # 重试次数
        self.retryTimes = 0

        # 测试数据
        self.testData = ""
        # 指令结果值参考
        self.atRefResult = ""
        # 测试指令
        self.atCmd = ""
        # 指令描述
        self.atDesc = ""
        # 人工操作等待时间
        self.opWaitTime = 5
        # 是否需要人工确认结果
        self.needConfirm = 1
        # 功能结果状态
        self.rltStatus = False

    def clearData(self):
        self.caseIndex = -1
        self.errorStatus = True
        self.atValue = ""
        self.startTime = ""
        self.endTime = ""
        self.retryTimes = 0

        self.testData = ""
        self.atRefResult = ""
        self.atCmd = ""
        self.atDesc = ""
        self.opWaitTime = 5
        self.needConfirm = 1
        self.rltStatus = False

    def resetData(self):
        self.errorStatus = True
        self.atValue = ""
        self.startTime = ""
        self.endTime = ""
        self.retryTimes = 0

        self.testData = ""
        self.rltStatus = False

    # 开始测试
    def startTest(self):
        self.errorStatus = True
        self.rltStatus = False
        self.startTime = time.strftime("%Y%m%d-%H_%M_%S", time.localtime(time.time()))
        self.endTime = ""
        self.retryTimes = 0
        self.testData = ""

    # 结束测试
    def endTest(self):
        self.endTime = time.strftime("%Y%m%d-%H_%M_%S", time.localtime(time.time()))

# 测试用例数据类
class Attest_Case_Data:
    mIsTesting = False
    mCurrentCaseIndex = -1
    mTotalCases = 0
    mAllCases = []

    @classmethod
    def clearData(self):
        self.mIsTesting = False
        self.mCurrentCaseIndex = -1
        self.mTotalCases = 0
        self.mAllCases = []

    @classmethod
    def setAllCases(self, lstCases):
        # 这里要除去字段描述数据
        tmpAllCases = []
        size = len(lstCases)
        for i in range(1, size):
            tmpAtData = lstCases[i]

            tmpCaseData = TestCase_Data()
            tmpCaseData.clearData()
            tmpCaseData.caseIndex = i
            tmpCaseData.atRefResult = tmpAtData[0]
            tmpCaseData.atCmd = tmpAtData[1]
            tmpCaseData.atDesc = tmpAtData[2]
            tmpCaseData.opWaitTime = int(tmpAtData[3])
            tmpCaseData.needConfirm = int(tmpAtData[4])

            tmpAllCases.append(tmpCaseData)

        # 添加测试用例数据[如果有按键测试配置,添加增加按键测试用例数据,同时后继用例数据索引值要同步]
        totalSize = len(tmpAllCases)
        tmpIndex = 0
        while tmpIndex < totalSize:
            # 添加用例
            tmpCaseData = tmpAllCases[tmpIndex]
            self.mAllCases.append(tmpCaseData)
            # 如果有按键测试配置
            if Keypress_Test_Data.isKeypressTest(tmpCaseData.atRefResult):
                # 记录按键测试开始索引值
                keypressCaseIndex = tmpCaseData.caseIndex
                tmpCount = 0
                # 初始化五个子按键测试数据
                for i in range(5):
                    tmpCount += 1
                    tmpCaseData = TestCase_Data()
                    tmpCaseData.clearData()
                    tmpCaseData.caseIndex = keypressCaseIndex + tmpCount
                    tmpCaseData.atRefResult = Keypress_Test_Data.Sub_KeyType_Value
                    tmpCaseData.atCmd = Keypress_Test_Data.Sub_KeyType_Cmd_Value
                    tmpCaseData.atDesc = Keypress_Test_Data.Sub_KeyType_Descs[i]
                    tmpCaseData.opWaitTime = 0
                    tmpCaseData.needConfirm = 0
                    self.mAllCases.append(tmpCaseData)
                # 后继用例数据索引值相应相加
                for tmpIdxEx in range(tmpIndex + 1, totalSize):
                    tmpCaseData = tmpAllCases[tmpIdxEx]
                    tmpCaseData.caseIndex += tmpCount
                    self.mAllCases.append(tmpCaseData)
                break
            tmpIndex += 1

        print(f"setAllCases size={len(self.mAllCases)}")

    @classmethod
    def validateCaseData(self):
        return len(self.mAllCases) > 0

    @classmethod
    def findCaseData(self, caseIndex):
        for tmpCaseData in self.mAllCases:
            if tmpCaseData.caseIndex == caseIndex:
                return tmpCaseData
        return None


