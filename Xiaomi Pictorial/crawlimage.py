import uuid
import httpx
import asyncio

import pymongo


# 连接 MongoDB 并检查是否存在相同 id 的文档
def check_existing_id(id, collection_name):
    # 连接 MongoDB
    client = pymongo.MongoClient("mongodb://192.168.4.150:27017/")
    db = client["xiaomiPandora"]
    collection = db[collection_name]

    # 查询是否存在相同 id 的文档
    existing_document = collection.find_one({"id": id})
    return existing_document is not None


# 连接 MongoDB 并插入文档的函数
def insert_into_mongodb(documents, collection_name):
    # 连接 MongoDB
    client = pymongo.MongoClient("mongodb://192.168.4.150:27017/")
    db = client["xiaomiPandora"]
    collection = db[collection_name]

    # 插入文档到 MongoDB
    collection.insert_many(documents)


async def request_and_process(url, params, proxy_url):
    try:
        async with httpx.AsyncClient(proxies=proxy_url) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                # to json
                res_json = response.json()
                items = res_json["items"]
                # print(items)

                documents = []  # 用于存储要插入到数据库的文档列表

                for item in items:
                    id = item["id"]
                    image_url = item["images"][0]["cl_url"]["url_h"]
                    meta = item["meta"]
                    categoriy_id = meta["categories"][0]["id"]
                    categoriy_name = meta["categories"][0]["name"]
                    desc = meta["desc"]
                    title = meta["title"]
                    tags = meta["tags"]

                    collection_name = f"{categoriy_id}_{categoriy_name}"
                    # 检查是否已存在相同 id 的文档
                    if check_existing_id(id, collection_name):
                        print(f"ID {id} 已存在，跳过插入")
                        continue

                    # 写入csv文件
                    # print(
                    #     id, image_url, categoriy_id, categoriy_name, desc, title, tags
                    # )
                    file_name = params["_devid"]
                    with open(f"{file_name}.csv", "a", encoding="utf-8") as f:
                        f.write(
                            f"{id},{title},{image_url},{categoriy_id},{categoriy_name},{desc},{tags}\n"
                        )
                    # 构建要插入到 MongoDB 的文档
                    document = {
                        "id": id,
                        "title": title,
                        "image_url": image_url,
                        "categoriy_id": categoriy_id,
                        "categoriy_name": categoriy_name,
                        "desc": desc,
                        "tags": tags,
                    }
                    documents.append(document)

                if documents.__len__() > 0:
                    print("插入到 MongoDB 的文档数量:", len(documents))
                    insert_into_mongodb(documents, collection_name)
                # insert_into_mongodb(documents)

            else:
                print("请求失败，状态码:", response.status_code)
    except httpx.HTTPError as e:
        print("请求发生异常:", e)


async def main():
    loop = asyncio.get_event_loop()
    proxy_url = "http://127.0.0.1:7890"
    if proxy_url:
        base_url = "https://w.pandora.xiaomi.com/api/a2/lock/lock_view"
        for i in range(1, 5):
            channel_id = f"CC000000{i:02d}"
            url = base_url
            uuid_without_hyphen = str(uuid.uuid4()).replace("-", "")
            params = {
                "_devid": uuid_without_hyphen,
                "channel_id": "8532cf1f-39a4-11e5-83cb-70e52b253bb7",
                "page_size": 300,
            }
            print("请求:", url, params)
            # loop.run_until_complete(request_and_process(url, params, proxy_url))
            await request_and_process(url, params, proxy_url)


if __name__ == "__main__":
    asyncio.run(main())
    # loop = asyncio.get_event_loop()
    # proxy_url = "http://127.0.0.1:7890"
    # if proxy_url:
    #     base_url = "https://w.pandora.xiaomi.com/api/a2/lock/lock_view"
    #     for i in range(1, 31):
    #         channel_id = f"CC010000{i:02d}"
    #         url = base_url
    #         uuid_without_hyphen = uuid.uuid4().replace("-", "")
    #         params = {
    #             "_devid": uuid_without_hyphen,
    #             "channel_id": channel_id,
    #             "page_size": 300,
    #         }
    #     loop.run_until_complete(request_and_process(url, params, proxy_url))
