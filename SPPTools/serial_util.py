# -*- coding: utf-8 -*-
# @Time    : 2023/06/20 16:30
# @Software: PyCharm
import time
import serial

# 打开串口
def openSerialCom(port, baudrate, timeout):
    serObj = serial.Serial()
    serObj.port = port
    serObj.baudrate = baudrate
    serObj.timeout = timeout
    serObj.open()
    return serObj

def sendATByHexBase(atCmd, serObj):
    # 发送指令
    result = serObj.write(bytes.fromhex(atCmd))
    # logging.info(f"send:{AT},写总字节数:{result}")
    print("send:{atCmd},写总字节数:{result}")
    return True

# 发送指令
def sendATByHexBaseEx(atCmd, serObj, refResult):
    # 结果状态
    success = False
    rlts = []

    # 发送指令
    result = serObj.write(bytes.fromhex(atCmd))
    # logging.info(f"send:{AT},写总字节数:{result}")
    print(f"send:{atCmd},写总字节数:{result}")

    # 读取结果数据
    Max_WaitTime = 3
    curWaitTime = 0
    errorTimes = 0
    while curWaitTime < Max_WaitTime:
        time.sleep(1)
        curWaitTime += 1
        if serObj.in_waiting:
            response = ""
            try:
                response = serObj.read(serObj.in_waiting).decode("gbk")
                # tmpBts = serObj.read(serObj.in_waiting)
                # for tmpB in tmpBts:
                #     response += chr(tmpB)
                # print(type(tmpBts), len(tmpBts), response)
            except Exception as e:
                errorTimes += 1
                response = ""
                print("sendATByHexBaseEx error?", repr(e))
            if len(response) == 0:
                continue
            rlts.append(response)
            if "SID:0" in response:
                success = True
                break
    if success:
        # 返回结果状态,读取数据内容
        return success, rlts
    else:
        # 读取数据异常
        if errorTimes > 0:
            return False, ["#error"]
        else:
            return False, rlts

# 按键操作后需要读取串口数据
def readKeypressResult(serObj):
    try:
        if serObj.in_waiting:
            response = serObj.read(serObj.in_waiting).decode("gbk")
            if (response != None) and (len(response) > 0):
                return True, response
    except Exception as e:
        print("readKeypressResult error?", repr(e))
    return False, ""

def testHexAtCmd():
    at = "bb030000000001000b00ca"
    bts = bytes.fromhex(at)
    print("type=", type(bts), "len=", len(bts))
    print(bts)
