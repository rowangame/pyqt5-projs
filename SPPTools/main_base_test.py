# -*- coding: utf-8 -*-
import time
from io import BytesIO

import qrcode
from qrcode.image.pure import PyPNGImage

def testTime():
    last = time.time()
    tinfo = time.strftime("%Y%m%d-%H_%M_%S", time.localtime(time.time()))
    time.sleep(3)
    now = time.time()
    print(tinfo, "last=", last, "now=", now, "delta=", (now - last))
    print("dtime=%.2f" % (now - last))

def testStrTrunc():
    rlts="SID:0\n\nPrj: A3040 Fw_Version:  0.1.3.3\n\nBLE Name:BES_BLE,\nBLE Addr:\naf 7e 43 cc ee e8\n\nBT Name:soundcore Space Q45,\nBT Addr:\naf 7e 43 cc ee e8\n\n"
    print(rlts)
    index = rlts.find("Fw_Version")
    print("index=", index)
    index2 = rlts.find("\n\n", index, len(rlts))
    print("index2=", index2, "ord(\n)=", ord("\n"))
    version = rlts[index + len("Fw_Version:"):index2]
    version = version.strip()
    print("len(version)=", len(version), "version=", version.strip())

    macSIdx = rlts.find("BT Addr:\n")
    macEIdx = rlts.find("\n", macSIdx + len("BT Addr:\n") + 1, len(rlts))
    macAddr = rlts[macSIdx + len("BT Addr:") + 1 : macEIdx]
    macAddr = macAddr.strip()
    print("len(macAddr)=", len(macAddr), "macAddr=", macAddr)
    macAddrNew = macAddr.replace(" ","")
    print("macAddrNew=", macAddrNew)

    arrs = rlts.split("\n\n")
    print(arrs)

    rlts2="SID:0\n\nBT Name:soundcore Space Q45\n\nBT Addr:\naf 7e 43 cc ee e8\n\n"
    print("rlts2")

def testStrBase():
    str = "abcdefgh"
    sub = str[3:5]
    print(sub)

    for i in range(1,6):
        print(f"id={i}")

def testQrCode():
    # https://blog.csdn.net/cnds123/article/details/123158166
    # https://blog.csdn.net/CYK_byte/article/details/126560782
    # https://pypi.org/project/qrcode/#files
    macAddr = "001122334455"
    try:
        print(macAddr)
        # img = qrcode.make(macAddr)
        # img.save(".qrcode/qrcode.png")

        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=4, border=2)

        # version：值为1~40的整数，控制二维码的大小（最小值是1，是个21×21的矩阵）
        # error_correction：控制二维码的错误纠正功能。可取值下列4个常量：
        '''
        qrcode.constants.ERROR_CORRECT_X：
            1. X=L时，大约7%或更少的错误能被纠正。
            2. X=M（默认）时，大约15%或更少的错误能被纠正。
            3. X=Q时，25%以下的错误会被纠正。
            4. X=H时，大约30%或更少的错误能被纠正。
        '''
        # box_size：控制二维码中每个小格子包含的像素数。
        # border：控制边框（二维码与图片边界的距离）包含的格子数（默认为4)

        # 向二维码中添加信息
        # qr.add_data("https://www.csdn.net/")
        qr.add_data(macAddr)
        qr.make(fit=True)

        img = qr.make_image()
        img.save("./qrcode/test.png")
        print("success")
    except Exception as e:
        print(repr(e))

def testQrCode2():
    try:
        macAddr = "001122334455"

        # img = qrcode.make('Some data here', image_factory=PyPNGImage)
        # img.save("./qrcode/test2.png")
        # print("sucess!")

        # 保存到文件
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=4, border=2)
        qr.add_data(macAddr)
        qr.make(fit=True)
        # 这里已经转化为png数据流了
        img = qr.make_image(image_factory=PyPNGImage)
        # img.save("./qrcode/test3.png")

        # 保存到内存中
        stream = BytesIO()
        img.save(stream,"PNG")
        stream.seek(0)
        bts = stream.read()
        print(type(stream))
        print("len(bts)=", len(bts), "type(bts)", type(bts), bts)

        # 将流数据保存到文件中
        binFile = "./qrcode/x.png"
        # https://blog.csdn.net/qq_44537267/article/details/106959554
        pngFile = open(binFile, "wb+")
        pngFile.write(bts)
        pngFile.close()

        print("success")
    except Exception as e:
        print(repr(e))

def testBase():
    for tmpIndex in range(1, 6):
        print("tmpIndex[%d]=%d", [tmpIndex, tmpIndex])

if __name__ == '__main__':
    # testStrTrunc()
    # testStrBase()
    # testQrCode()
    # testQrCode2()
    testBase()