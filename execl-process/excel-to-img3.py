from spire.xls import *
from spire.xls.common import *

# 创建一个Workbook对象
workbook = Workbook()
# 加载一个Excel文件
workbook.LoadFromFile("output_reversed_daily_month.xlsx")

# 获取第一个工作表
sheet = workbook.Worksheets[0]

# 将工作表保存为图片
image = sheet.ToImage(
    sheet.FirstRow, sheet.FirstColumn, sheet.LastRow, sheet.LastColumn
)

# 将图片保存为PNG文件
image.Save("工作表.png")

# # 将图片保存为JPG文件
# image.Save("工作表.jpg")

# # 将图片保存为BMP文件
# image.Save("工作表.bmp")

workbook.Dispose()
