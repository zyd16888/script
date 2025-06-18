import re
import socket
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from collections import defaultdict


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


def is_url_accessible(url, timeout=10):
    try:
        response = requests.head(url, timeout=timeout)
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
    domain_cache = {}

    def domain_filter(url):
        domain = urllib.parse.urlparse(url).netloc
        if domain not in domain_cache:
            domain_cache[domain] = is_domain_accessible(domain)
        return domain_cache[domain]

    process_file(input_file, output_file, domain_filter)


def filter_urls(input_file, output_file, max_workers=5, timeout=10):
    url_cache = {}

    def url_filter(urls):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {}
            for url in urls:
                if url not in url_cache:
                    future_to_url[executor.submit(is_url_accessible, url, timeout)] = (
                        url
                    )

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    url_cache[url] = future.result()
                except Exception as exc:
                    print(f"{url} generated an exception: {exc}")
                    url_cache[url] = False

        return {url: url_cache[url] for url in urls}

    urls = []
    url_to_lines = {}
    with open(input_file, "r", encoding="utf-8") as infile:
        for line in infile:
            if line.startswith("#EXTINF"):
                info_line = line
                continue
            url = extract_url(line)
            if url:
                urls.append(url)
                url_to_lines[url] = (info_line, line)

    # Group URLs by domain
    domain_to_urls = defaultdict(list)
    for url in urls:
        domain = urllib.parse.urlparse(url).netloc
        domain_to_urls[domain].append(url)

    # Process URLs by domain
    with open(output_file, "w", encoding="utf-8") as outfile:
        total_urls = len(urls)
        processed_urls = 0
        for domain, domain_urls in domain_to_urls.items():
            results = url_filter(domain_urls)
            for url, is_accessible in results.items():
                if is_accessible:
                    info_line, content_line = url_to_lines[url]
                    outfile.write(info_line)
                    outfile.write(content_line)
            processed_urls += len(domain_urls)
            print(f"Processed {processed_urls}/{total_urls} URLs")


def main():
    input_file = "input.m3u"
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
