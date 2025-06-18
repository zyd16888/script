import json
import json5
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from argparse import ArgumentParser

# ========== 配置 ==========
TIMEOUT = 10
MAX_WORKERS = 10
PROXY = "http://127.0.0.1:7890"  # 可设为 None 不使用代理

# 构建 requests 参数
requests_kwargs = {
    "timeout": TIMEOUT
}
if PROXY:
    requests_kwargs["proxies"] = {
        "http": PROXY,
        "https": PROXY
    }

# ========== 检测函数 ==========
def is_url_alive(url):
    try:
        res = requests.get(url, **requests_kwargs)
        return res.status_code == 200
    except Exception:
        return False

def check_site(site, allow_jar):
    name = site.get("name", "Unknown")
    api = site.get("api")

    if api and api.startswith("csp_"):
        if not allow_jar:
            return (name, False, None)
        else:
            # 允许检测 jar，但不认为它是 http，可根据需要扩展检测逻辑
            return (name, False, None)  # 或实现 jar 检测逻辑

    api_ok = is_url_alive(api) if api and api.startswith("http") else False

    lives_ok = True
    lives = site.get("lives")
    if isinstance(lives, list):
        for live_url in lives:
            if not is_url_alive(live_url):
                lives_ok = False
                break

    success = api_ok and lives_ok
    return (name, success, site if success else None)

# ========== 主处理函数 ==========
def process_json_file(filepath, allow_jar, all_valid_apis, all_jar_sites):
    print(f"\n📂 正在处理: {os.path.basename(filepath)}")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json5.load(f)

    sites = data.get("sites", [])
    valid_sites = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for site in sites:
            api = site.get("api", "")
            if api.startswith("csp_"):
                all_jar_sites.append(site)
            futures.append(executor.submit(check_site, site, allow_jar))

        for future in as_completed(futures):
            name, success, site_data = future.result()
            if success:
                print(f"[✓] {name}")
                valid_sites.append(site_data)
                api = site_data.get("api")
                if api and api not in all_valid_apis:
                    all_valid_apis[api] = site_data
            else:
                print(f"[✗] {name}")

    data["sites"] = valid_sites
    output_path = os.path.splitext(filepath)[0] + "_checked.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ 写入完成: {output_path}（保留 {len(valid_sites)} 个有效线路）")

# ========= 启动入口 =========
def main():
    parser = ArgumentParser(description="检测 JSON 中 API 和 Live 地址连通性")
    parser.add_argument("directory", help="包含 JSON 文件的目录")
    parser.add_argument("--allow-jar", action="store_true", help="是否检测以 csp_ 开头的 jar 类型线路")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"❌ 目录不存在: {args.directory}")
        return

    json_files = [f for f in os.listdir(args.directory) if f.endswith(".json")]
    if not json_files:
        print("❗ 未发现任何 JSON 文件")
        return

    all_valid_apis = {}
    all_jar_sites = []

    for filename in json_files:
        filepath = os.path.join(args.directory, filename)
        process_json_file(filepath, args.allow_jar, all_valid_apis, all_jar_sites)

    # 生成 summary.json
    summary_data = {
        "sites": list(all_valid_apis.values())
    }
    summary_path = os.path.join(args.directory, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    print(f"\n📄 汇总完成，共 {len(summary_data['sites'])} 个唯一可用 API，写入：{summary_path}")

    # 生成 jar_sites.json
    jar_path = os.path.join(args.directory, "jar_sites.json")
    with open(jar_path, "w", encoding="utf-8") as f:
        json.dump({"sites": all_jar_sites}, f, indent=2, ensure_ascii=False)
    print(f"📦 已收集 {len(all_jar_sites)} 条 jar 类型线路，写入：{jar_path}")

if __name__ == "__main__":
    main()
