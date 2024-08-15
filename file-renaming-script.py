import os
import pymongo
import re

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]
collection = db["your_collection_name"]

# Directory containing the files
base_dir = "V:\\"


def sanitize_filename(filename):
    """
    将文件名中的无效字符移除或替换。

    参数:
        filename (str): 需要处理的文件名。

    返回:
        str: 移除或替换无效字符后的文件名。
    """
    # Remove or replace invalid characters
    return re.sub(r'[<>:"/\\|?*]', "", filename)


def find_matching_document(filename):
    """
    查找匹配的文档。

    参数:
        filename (str): 要查找的文件名。

    返回:
        tuple: 包含两个元素的元组。第一个元素是匹配的文档（如果找到），否则为 None。第二个元素是一个布尔值，表示文件名是否包含 "-C" 后缀。
    """
    # Remove file extension and "-C" suffix for search, but keep track of "-C"
    search_name = os.path.splitext(filename)[0]
    has_c_suffix = search_name.endswith("-C")
    search_name = re.sub(r"-C$", "", search_name)

    # Search in the database
    result = collection.find_one(
        {"Title": {"$regex": f"^{re.escape(search_name)}$", "$options": "i"}}
    )
    return result, has_c_suffix


def rename_files():
    """
    重命名文件和目录的函数。

    此函数遍历指定目录中的所有文件和子目录，查找以.mp4结尾的文件（可以根据需要调整文件类型）。
    对于每个匹配的文件，它会在MongoDB中查找匹配的文档，并根据文档中的信息生成新的文件名。
    如果找到匹配的文档，它会重命名文件和匹配的父目录（如果父目录名称与旧文件名（不带扩展名）匹配）。

    Raises:
        Exception: 重命名文件或目录时发生的任何异常。

    """
    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if filename.endswith(".mp4"):  # Adjust this if you have other file types
                old_path = os.path.join(root, filename)

                # Find matching document in MongoDB
                doc, has_c_suffix = find_matching_document(filename)

                if doc:
                    title = doc.get("Title", "")
                    if has_c_suffix:
                        title += "-C"
                    movie_name = doc.get("Movie Name", "")
                    actress = doc.get("Actress", "")

                    # Create the new filename
                    new_name = f"{title}-{movie_name}-{actress}"
                    new_name = sanitize_filename(new_name)
                    new_path = os.path.join(
                        root, new_name + os.path.splitext(filename)[1]
                    )

                    try:
                        os.rename(old_path, new_path)
                        print(f"Renamed: {old_path} -> {new_path}")
                    except Exception as e:
                        print(f"Error renaming {old_path}: {str(e)}")

                    # Rename the parent directory if it matches the old filename (without extension)
                    dir_name = os.path.basename(root)
                    if dir_name == os.path.splitext(filename)[0]:
                        old_dir_path = root
                        new_dir_path = os.path.join(os.path.dirname(root), new_name)
                        try:
                            os.rename(old_dir_path, new_dir_path)
                            print(
                                f"Renamed directory: {old_dir_path} -> {new_dir_path}"
                            )
                        except Exception as e:
                            print(f"Error renaming directory {old_dir_path}: {str(e)}")
                else:
                    print(f"No matching document found for: {filename}")

if __name__ == "__main__":
    rename_files()
