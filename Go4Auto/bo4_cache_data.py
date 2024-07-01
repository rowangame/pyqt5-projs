
import re
import time


class Uart_Data:
    mComNum = ""
    mBaudrate = 921600
    mTimeOut = 1.5


class Cmd_Data:
    # 获取设备序列号
    AT_GetSerialNo = "0F F0 36 00 41 54 2B 48 4D 44 65 76 53 4E 52 45 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FD 2A"

    # 获取蓝牙地址
    AT_GetMac = "0F F0 36 00 41 54 2B 48 4D 44 65 76 4D 41 43 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 27 E3"

    # 进入RF产测模式
    AT_SetRfMode = "0F 7F 36 00 41 54 2B 48 4D 44 65 76 44 55 54 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF 4D"

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
    def getMacValue(self, maxSrcValue: str):
        Mac_Tag = "AT+HMDevMAC="
        index = maxSrcValue.find("AT+HMDevMAC=")
        if index != -1:
            sIdx = index + len(Mac_Tag)
            eIdx = sIdx + 12
            macValue = maxSrcValue[sIdx:eIdx]
        else:
            macValue = ""
        return macValue


class Com_Data:
    # 串口不可用,下次测试此串口的等待时间
    RetryWaitTime = 15

    def __init__(self):
        super(Com_Data, self).__init__()
        # 串口名
        self.comName = ""
        # 当前串口测试的开始时间(串口不能用后,等待一段时间后再测试)
        self.testStartTime = 0
        # 向当前串发送指令是否是成功的(不成功表示不可用,可能不是要测试设备的串口)
        self.cmdOK = False

    def canRetry(self):
        return time.time() - self.testStartTime > self.RetryWaitTime


class Device_Data:
    # 最大允许的缓存设备数量
    Max_Device_Cnt = 4000

    def __init__(self):
        super(Device_Data, self).__init__()
        # 索引值
        self.index = 0
        # mac地址
        self.macAddr = ""
        # 是否发送指令成功(成功进入RF产测模式)
        self.processOk = False