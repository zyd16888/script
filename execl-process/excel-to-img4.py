def create_save_img(file_path, sheetname, img_name):
    """
    Parameters
    ----------
    file_path : string
        Excel文件的路径，最好是绝对路径.
    sheetname : string
        需要复制成图片的Excel文件的sheet名.
    img_name : string
        最终图片保存的名字及路径.

    Returns
    -------
    None.

    """
    # 读取excel内容转换为图片
    from PIL import ImageGrab
    import xlwings as xw
    import pythoncom
    import os
    import time

    os.system("taskkill /IM EXCEL.exe /F")
    pythoncom.CoInitialize()
    # 使用xlwings的app启动
    app = xw.App(
        visible=False,
        add_book=False,
    )
    # 打开文件
    file_path = os.path.abspath(file_path)
    wb = app.books.open(file_path)
    # 选定sheet
    sheet = wb.sheets(sheetname)
    # 获取有内容的区域
    all = sheet.used_range
    # 复制图片区域
    all.api.CopyPicture()
    # 粘贴
    sheet.api.Paste()
    # 当前图片
    pic = sheet.pictures[-1]
    # 复制图片
    pic.api.Copy()
    time.sleep(5)  # 延迟一下操作，不然获取不到图片
    # 获取剪贴板的图片数据
    img = ImageGrab.grabclipboard()
    # 保存图片
    img.save(img_name)
    # 删除sheet上的图片
    pic.delete()
    # 不保存，直接关闭
    wb.close()
    # 退出xlwings的app启动
    app.quit()
    pythoncom.CoUninitialize()  # 关闭多线程
    # os.remove(file_path)


# 路径
data_path = "./"
filename = data_path + "output_reversed_daily_month_percentage2.xlsx"
create_save_img(
    filename, "Sheet", data_path + "output_reversed_daily_month_percentage2.png"
)
