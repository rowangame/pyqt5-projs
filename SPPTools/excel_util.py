# -*- coding: utf-8 -*-

import xlwings as xlws

from attest_case_data import Keypress_Test_Data


class Excel_Writer(object):
    @classmethod
    def saveToFile(self, fileName, dts: dict):
        try:
            tmpApp = xlws.App(visible=False)
            workbook = tmpApp.books.add()
            worksheet = workbook.sheets.add(f"{dts['modelType']}测试结果")

            # 单元格属性
            Range_Tags = ["", "A", "B", "C", "D", "E", "F", "G", "H"]
            Column_Width = 28
            Row_Height = 24

            # 标题名字
            Title_Names = ["", "结果状态值", "指令集", "指令功能定义", "指令结果", "验证状态", ""]
            # 标题颜色
            Title_Color = (0, 255, 0)
            # 标题字体大小
            Title_Size = 12
            # 指令状态颜色
            At_Error_Color = (255, 0, 0)
            At_Pass_Color = (0, 255, 0)
            # 测试结果状态颜色
            Rlt_Error_Color = (255, 0, 0)
            Rlt_Pass_Color = (0, 255, 0)

            # 写标题
            rowIdx = 1
            for colIndex in range(1, len(Title_Names)):
                cellIndex = "%s%d" % (Range_Tags[colIndex], rowIdx)
                worksheet.range(cellIndex).value = Title_Names[colIndex]
                if colIndex < 6:
                    worksheet.range(cellIndex).color = Title_Color
                    worksheet.range(cellIndex).font.bold = True
                    worksheet.range(cellIndex).font.size = Title_Size
                else:
                    worksheet.range(cellIndex).font.bold = True
                    worksheet.range(cellIndex).font.size = Title_Size
                worksheet.range(cellIndex).column_width = Column_Width
                worksheet.range(cellIndex).row_height = Row_Height

            # 写测试内容
            rowIdx += 1
            allCases = dts["data"]
            for tmpData in allCases:
                # 如果是子按键测试数据,则跳过
                if Keypress_Test_Data.isBubKeypressType(tmpData.atRefResult):
                    continue
                # 结果状态值
                tmpCellIndex = "%s%d" % (Range_Tags[1], rowIdx)
                worksheet.range(tmpCellIndex).value = tmpData.atRefResult

                # 指令集
                tmpCellIndex = "%s%d" % (Range_Tags[2], rowIdx)
                worksheet.range(tmpCellIndex).value = tmpData.atCmd

                # 指令功能定义
                tmpCellIndex = "%s%d" % (Range_Tags[3], rowIdx)
                worksheet.range(tmpCellIndex).value = tmpData.atDesc

                # 指令结果
                tmpCellIndex = "%s%d" % (Range_Tags[4], rowIdx)
                if tmpData.errorStatus:
                    worksheet.range(tmpCellIndex).value = tmpData.atValue
                    worksheet.range(tmpCellIndex).font.color = At_Error_Color
                    worksheet.range(tmpCellIndex).font.bold = True
                else:
                    worksheet.range(tmpCellIndex).value = tmpData.atValue
                    worksheet.range(tmpCellIndex).font.color = At_Pass_Color
                    worksheet.range(tmpCellIndex).font.bold = True

                # 验证状态
                tmpCellIndex = "%s%d" % (Range_Tags[5], rowIdx)
                if tmpData.rltStatus:
                    worksheet.range(tmpCellIndex).value = "PASS"
                    worksheet.range(tmpCellIndex).font.color = At_Pass_Color
                    worksheet.range(tmpCellIndex).font.bold = True
                else:
                    worksheet.range(tmpCellIndex).value = "FAIL"
                    worksheet.range(tmpCellIndex).font.color = At_Error_Color
                    worksheet.range(tmpCellIndex).font.bold = True
                # 行索引值增加
                rowIdx += 1

                # 如果是按键状态测试,则添加按键测试的几项值
                if Keypress_Test_Data.isKeypressTest(tmpData.atRefResult):
                    for tmpKeyIdx in range(1, 6):
                        tmpKeyData = Keypress_Test_Data.mAllCases[tmpKeyIdx]
                        # 按键功能定义
                        tmpCellIndex = "%s%d" % (Range_Tags[3], rowIdx)
                        worksheet.range(tmpCellIndex).value = tmpKeyData.keyValue
                        # 指令结果
                        tmpCellIndex = "%s%d" % (Range_Tags[4], rowIdx)
                        if tmpKeyData.errorStatus:
                            worksheet.range(tmpCellIndex).value = "FAIL"
                            worksheet.range(tmpCellIndex).font.color = At_Error_Color
                            worksheet.range(tmpCellIndex).font.bold = True
                        else:
                            worksheet.range(tmpCellIndex).value = "OK"
                            worksheet.range(tmpCellIndex).font.color = At_Pass_Color
                            worksheet.range(tmpCellIndex).font.bold = True
                        # 功能结果
                        tmpCellIndex = "%s%d" % (Range_Tags[5], rowIdx)
                        if not tmpKeyData.errorStatus:
                            worksheet.range(tmpCellIndex).value = "PASS"
                            worksheet.range(tmpCellIndex).font.color = At_Pass_Color
                            worksheet.range(tmpCellIndex).font.bold = True
                        else:
                            worksheet.range(tmpCellIndex).value = "FAIL"
                            worksheet.range(tmpCellIndex).font.color = At_Error_Color
                            worksheet.range(tmpCellIndex).font.bold = True
                        # 行索引值增加
                        rowIdx += 1

            # 中间隔几行
            rowIdx += 2

            # 开始时间
            tmpCellIndex = "%s%d" % (Range_Tags[1], rowIdx)
            worksheet.range(tmpCellIndex).value = "开始时间:"
            worksheet.range(tmpCellIndex).font.bold = True
            tmpCellIndex = "%s%d" % (Range_Tags[2], rowIdx)
            worksheet.range(tmpCellIndex).value = dts["startTime"]
            # 结束时间
            tmpCellIndex = "%s%d" % (Range_Tags[3], rowIdx)
            worksheet.range(tmpCellIndex).value = "结束时间:"
            worksheet.range(tmpCellIndex).font.bold = True
            tmpCellIndex = "%s%d" % (Range_Tags[4], rowIdx)
            worksheet.range(tmpCellIndex).value = dts["endTime"]
            # 持续时间
            tmpCellIndex = "%s%d" % (Range_Tags[5], rowIdx)
            worksheet.range(tmpCellIndex).value = "持续时间:"
            worksheet.range(tmpCellIndex).font.bold = True
            tmpCellIndex = "%s%d" % (Range_Tags[6], rowIdx)
            worksheet.range(tmpCellIndex).value = dts["duration"]
            rowIdx += 1

            # 测试员ID
            tmpCellIndex = "%s%d" % (Range_Tags[1], rowIdx)
            worksheet.range(tmpCellIndex).value = "测试员ID:"
            worksheet.range(tmpCellIndex).font.bold = True
            tmpCellIndex = "%s%d" % (Range_Tags[2], rowIdx)
            worksheet.range(tmpCellIndex).value = dts["jobId"]
            # 测试平台
            tmpCellIndex = "%s%d" % (Range_Tags[3], rowIdx)
            worksheet.range(tmpCellIndex).value = "测试平台:"
            worksheet.range(tmpCellIndex).font.bold = True
            tmpCellIndex = "%s%d" % (Range_Tags[4], rowIdx)
            worksheet.range(tmpCellIndex).value = dts["testPlat"]
            # 产线ID
            tmpCellIndex = "%s%d" % (Range_Tags[5], rowIdx)
            worksheet.range(tmpCellIndex).value = "产品 MAC:"
            worksheet.range(tmpCellIndex).font.bold = True
            tmpCellIndex = "%s%d" % (Range_Tags[6], rowIdx)
            # 这里防止excel将mac地址转化为数字显示
            worksheet.range(tmpCellIndex).value = "mac:" + dts["macAddr"]
            rowIdx += 1

            # 产品类型
            tmpCellIndex = "%s%d" % (Range_Tags[1], rowIdx)
            worksheet.range(tmpCellIndex).value = "产品类型:"
            worksheet.range(tmpCellIndex).font.bold = True
            tmpCellIndex = "%s%d" % (Range_Tags[2], rowIdx)
            worksheet.range(tmpCellIndex).value = dts["modelType"]
            # 测试结果
            tmpCellIndex = "%s%d" % (Range_Tags[3], rowIdx)
            worksheet.range(tmpCellIndex).value = "测试结果:"
            worksheet.range(tmpCellIndex).font.bold = True
            tmpCellIndex = "%s%d" % (Range_Tags[4], rowIdx)
            if dts["status"] == "PASS":
                worksheet.range(tmpCellIndex).value = "PASS"
                worksheet.range(tmpCellIndex).font.bold = True
                worksheet.range(tmpCellIndex).font.color = Rlt_Pass_Color
            else:
                worksheet.range(tmpCellIndex).value = "FAIL"
                worksheet.range(tmpCellIndex).font.bold = True
                worksheet.range(tmpCellIndex).font.color = Rlt_Error_Color
            rowIdx += 1

            # 保存文件
            workbook.save(fileName)
            # 关闭excel
            workbook.close()
            #退出
            tmpApp.quit()

            return True
        except Exception as e:
            print(repr(e))
            return False
