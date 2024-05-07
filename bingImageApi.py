import random
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from PIL import Image, ImageFilter
from io import BytesIO
import requests
from cachetools import TTLCache

app = FastAPI()

# JSON 文件的 URL
json_url = "https://raw.githubusercontent.com/zkeq/Bing-Wallpaper-Action/main/data/zh-CN_all.json"

# 创建一个 TTL 缓存，设置过期时间为 300 秒
json_cache = TTLCache(maxsize=1, ttl=300)

def fetch_json_data():
    try:
        response = requests.get(json_url)
        json_data = response.json()
        print("request json success")
        return json_data
    except Exception as e:
        print("Error fetching JSON data:", e)
        return None

def get_random_image_url(json_data):
    if json_data :
        urls = [data["url"] for data in json_data["data"]]
        return random.choice(urls)
    else:
        return None

@app.get("/get_image")
async def get_image(blur_radius: int = 10):
    # 获取缓存的 JSON 数据
    json_data = json_cache.get("json_data")
    if json_data is None:
        json_data = fetch_json_data()
        json_cache["json_data"] = json_data
    
    if json_data:
        # 获取图片 URL
        image_url = get_random_image_url(json_data)
        
        if image_url:
            response = requests.get(url=f"https://www.bing.com{image_url}")
            image_data = response.content

            image_io = BytesIO(image_data)
            image = Image.open(image_io)

            blurred_image = image.filter(ImageFilter.GaussianBlur(blur_radius))

            blurred_image_io = BytesIO()
            blurred_image.save(blurred_image_io, format="JPEG")
            blurred_image_io.seek(0)

            return StreamingResponse(blurred_image_io, media_type="image/jpeg")
        else:
            return {"message": "无法获取图片 URL。"}
    else:
        return {"message": "无法获取 JSON 数据。"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8881)
