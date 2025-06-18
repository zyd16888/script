import re
import socket
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests


def extract_url(line):
    match = re.search(r"https?://\S+", line)
    return match.group(0) if match else None


def is_domain_accessible(domain):
    try:
        socket.gethostbyname(domain)
        print(f"Domain {domain} is accessible.")
        return True
    except socket.gaierror:
        return False


def is_url_accessible(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def process_file(input_file, output_file, filter_func):
    with open(input_file, "r", encoding="utf-8") as infile, open(
        output_file, "w", encoding="utf-8"
    ) as outfile:
        for line in infile:
            if line.startswith("#EXTINF"):
                info_line = line
                continue
            url = extract_url(line)
            if url and filter_func(url):
                outfile.write(info_line)
                outfile.write(line)


def filter_domains(input_file, output_file):
    def domain_filter(url):
        domain = urllib.parse.urlparse(url).netloc
        return is_domain_accessible(domain)

    process_file(input_file, output_file, domain_filter)


def filter_urls(input_file, output_file):
    process_file(input_file, output_file, is_url_accessible)


def main():
    input_file = r"C:\Users\zyd47\Downloads\A.m3u"
    domain_filtered_file = "domain_filtered.m3u"
    final_filtered_file = "final_filtered.m3u"

    print("开始域名筛选...")
    filter_domains(input_file, domain_filtered_file)
    print("域名筛选完成。结果保存在", domain_filtered_file)

    print("开始URL可用性筛选...")
    filter_urls(domain_filtered_file, final_filtered_file)
    print("URL可用性筛选完成。最终结果保存在", final_filtered_file)


if __name__ == "__main__":
    main()
