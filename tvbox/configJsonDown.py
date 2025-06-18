import os
import requests
from urllib.parse import urljoin

def sanitize_filename(name):
    """移除文件名中非法字符"""
    return "".join(c for c in name if c not in r'\/:*?"<>|')

def download_jsons(aggregate_url, output_dir='downloaded_jsons'):
    os.makedirs(output_dir, exist_ok=True)

    try:
        response = requests.get(aggregate_url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"下载聚合文件失败: {e}")
        return

    base_url = aggregate_url.rsplit('/', 1)[0] + '/'

    for item in data.get("urls", []):
        relative_url = item.get("url")
        name = item.get("name")

        if not relative_url or not name:
            continue

        full_url = urljoin(base_url, relative_url)
        filename = sanitize_filename(name) + ".json"
        save_path = os.path.join(output_dir, filename)

        print(f"正在下载: {full_url} → {filename}")

        try:
            res = requests.get(full_url)
            res.raise_for_status()
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(res.text)
            print(f"保存到: {save_path}")
        except Exception as e:
            print(f"下载失败: {full_url}, 错误: {e}")

if __name__ == "__main__":
    download_jsons("https://tvboxconfig.singlelovely.cn/tvbox-r18.json")
