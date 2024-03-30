import os
import asyncio
import pymongo
import httpx
import aiofiles


async def get_collections():
    # 连接 MongoDB
    client = pymongo.MongoClient("mongodb://192.168.4.150:27017/")
    db = client["xiaomiPandora"]
    collections = db.list_collection_names()
    return collections


async def get_data(collection_name):
    # 连接 MongoDB
    client = pymongo.MongoClient("mongodb://192.168.4.150:27017/")
    db = client["xiaomiPandora"]
    collection = db[collection_name]
    data = collection.find()
    name = data[0]["categoriy_name"]
    return data, name


async def download_image(img_url, img_name, collection_folder):
    img_extension = "webp"  # 获取图片扩展名
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream(
                "GET", img_url, proxies="http://127.0.0.1:7890"
            ) as response:
                if response.status_code == 200:
                    async with aiofiles.open(
                        os.path.join(collection_folder, f"{img_name}.{img_extension}"),
                        "wb",
                    ) as f:
                        async for chunk in response.aiter_bytes():
                            await f.write(chunk)
                    print(f"Downloaded image: {img_name}.{img_extension}")
                else:
                    print(f"Failed to download image: {img_name}.{img_extension}")
        except Exception as e:
            print(f"Error downloading image: {img_name}.{img_extension}, {e}")


async def download_images(data, collection_name, output_folder):
    collection_folder = os.path.join(output_folder, collection_name)
    if not os.path.exists(collection_folder):
        os.makedirs(collection_folder)

    tasks = []
    for item in data:
        img_url = item["image_url"]
        img_name = item["title"]
        tasks.append(download_image(img_url, img_name, collection_folder))

    await asyncio.gather(*tasks)


async def main():
    collections = await get_collections()

    # 假设我们想要将图片保存在当前目录下的 images 文件夹中
    output_folder = "images"

    tasks = []
    for collection_name in collections:
        data, output_folder = await get_data(collection_name)
        tasks.append(download_images(data, collection_name, output_folder))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
