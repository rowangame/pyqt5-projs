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
    rlt = []

    Max_WaitTimes = 3
    curTimes = 0
    errorTimes = 0
    try:
        # 发送指令
        result = serObj.write(bytes.fromhex(atCmd))
        # logging.info(f"send:{AT},写总字节数:{result}")
        print(f"send:{atCmd[:6]}...,写总字节数:{result}")
        # 读取结果数据
        while curTimes < Max_WaitTimes:
            time.sleep(0.5)
            curTimes += 1
            if serObj.in_waiting:
                response = ""
                try:
                    tmpBts = serObj.read(serObj.in_waiting)
                    for tmpB in tmpBts:
                        # 过滤掉空字符
                        if tmpB > 0:
                            response += chr(tmpB)
                    # print(type(tmpBts), len(tmpBts), response)
                except Exception as e:
                    errorTimes += 1
                    response = ""
                    print("sendATByHexBaseEx error?", repr(e))
                if len(response) == 0:
                    continue
                rlt.append(response)
                if refResult in response:
                    success = True
                    break
    except Exception as e:
        print(repr(e))
        success = False
        errorTimes += 1

    if success:
        # 返回结果状态,读取数据内容
        return success, rlt
    else:
        # 读取数据异常
        if errorTimes > 0:
            return False, ["#error"]
        else:
            return False, rlt
