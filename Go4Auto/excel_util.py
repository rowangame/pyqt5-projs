# -*- coding: utf-8 -*-

import xlwings as xlws

class Excel_Writer(object):
    @classmethod
    def saveToFile(self, fileName, dts: dict):
        try:
            tmpApp = xlws.App(visible=False)
            workbook = tmpApp.books.add()
            worksheet = workbook.sheets.add(f"产测指令结果")

            # 单元格属性
            Range_Tags = ["", "A", "B", "C", "D", "E", "F", "G", "H"]
            Column_Width = 28
            Row_Height = 24

            # 标题名字
            Title_Names = ["", "ID", "设备MAC", "指令类型", "指令状态"]
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

                worksheet.range(cellIndex).color = Title_Color
                worksheet.range(cellIndex).font.bold = True
                worksheet.range(cellIndex).font.size = Title_Size

                worksheet.range(cellIndex).column_width = Column_Width
                worksheet.range(cellIndex).row_height = Row_Height

            # 写测试内容
            rowIdx += 1
            lstDevData = dts["data"]
            for tmpDev in lstDevData:
                # ID
                tmpCellIndex = "%s%d" % (Range_Tags[1], rowIdx)
                worksheet.range(tmpCellIndex).value = "%04d" % tmpDev.index

                # 设备MAC
                tmpCellIndex = "%s%d" % (Range_Tags[2], rowIdx)
                worksheet.range(tmpCellIndex).value = tmpDev.macAddr

                # 指令类型
                tmpCellIndex = "%s%d" % (Range_Tags[3], rowIdx)
                worksheet.range(tmpCellIndex).value = "RF产测模式"

                # 指令状态
                tmpCellIndex = "%s%d" % (Range_Tags[4], rowIdx)
                if tmpDev.processOk:
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
            rowIdx += 1

            # 结束时间
            tmpCellIndex = "%s%d" % (Range_Tags[1], rowIdx)
            worksheet.range(tmpCellIndex).value = "结束时间:"
            worksheet.range(tmpCellIndex).font.bold = True
            tmpCellIndex = "%s%d" % (Range_Tags[2], rowIdx)
            worksheet.range(tmpCellIndex).value = dts["endTime"]
            rowIdx += 1

            # 持续时间
            tmpCellIndex = "%s%d" % (Range_Tags[1], rowIdx)
            worksheet.range(tmpCellIndex).value = "总用时:"
            worksheet.range(tmpCellIndex).font.bold = True
            tmpCellIndex = "%s%d" % (Range_Tags[2], rowIdx)
            worksheet.range(tmpCellIndex).value = dts["duration"]
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
