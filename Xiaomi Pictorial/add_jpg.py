import os


def add_extension(folder_path):
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 构建文件的完整路径
        file_path = os.path.join(folder_path, filename)
        # 如果是文件而不是文件夹
        if os.path.isfile(file_path):
            # 分割文件名和扩展名
            name, ext = os.path.splitext(filename)
            # 如果没有扩展名或者扩展名不是 .jpg
            if not ext or ext.lower() != ".jpg":
                # 重命名文件，添加 .jpg 后缀
                new_filename = name + ".jpg"
                new_file_path = os.path.join(folder_path, new_filename)
                os.rename(file_path, new_file_path)
                print(f"Renamed: {filename} -> {new_filename}")


# 指定文件夹路径
folder_path = "E:\\小米画报"

# 添加扩展名
add_extension(folder_path)
