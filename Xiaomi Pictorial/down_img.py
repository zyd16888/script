import os
import pymongo
import httpx


def get_collections():
    # 连接 MongoDB
    client = pymongo.MongoClient("mongodb://192.168.4.150:27017/")
    db = client["xiaomiPandora"]
    collections = db.list_collection_names()
    return collections


def get_data(collection_name):
    # 连接 MongoDB
    client = pymongo.MongoClient("mongodb://192.168.4.150:27017/")
    db = client["xiaomiPandora"]
    collection = db[collection_name]
    data = collection.find()
    name = data[0]["categoriy_name"]
    return data


def down_image(data, collection_name, output_folder="images"):
    collection_folder = os.path.join(output_folder, collection_name)
    if not os.path.exists(collection_folder):
        os.makedirs(collection_folder)

    for item in data:
        img_id = item["id"]
        img_url = item["image_url"]
        img_name = item["title"]
        img_extension = "webp"  # 获取图片扩展名

        try:
            # 下载图片
            with httpx.stream(
                "GET", img_url, proxies="http://127.0.0.1:7890"
            ) as response:
                if response.status_code == 200:
                    with open(
                        os.path.join(
                            collection_folder, f"{img_id}-{img_name}.{img_extension}"
                        ),
                        "wb",
                    ) as f:
                        f.write(response.read())
                    print(
                        f"Downloaded image: {collection_name}/{img_name}.{img_extension}"
                    )
                else:
                    print(
                        f"Failed to download image: {collection_name}/{img_name}.{img_extension}"
                    )
        except Exception as e:
            print(
                f"Failed to download image: {collection_name}/{img_name}.{img_extension}"
            )
            print(e)


if __name__ == "__main__":
    collections = get_collections()

    # 假设我们想要将图片保存在当前目录下的 images 文件夹中
    output_folder = "images"

    for collection_name in collections:
        data = get_data(collection_name)
        down_image(data, collection_name, output_folder)
