import os
from urllib.parse import quote

# 支持的视频文件扩展名列表
SUPPORTED_VIDEO_EXTENSIONS = [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"]


def is_video_file(file):
    return any(file.lower().endswith(ext) for ext in SUPPORTED_VIDEO_EXTENSIONS)


def process_directory(root_dir, output_dir, domain):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if is_video_file(file):
                # 构建原始文件的完整路径
                original_path = os.path.join(root, file)

                # 构建相对路径，并拼接域名
                relative_path = os.path.relpath(original_path, root_dir)

                # 对domain和相对路径进行编码，然后拼接域名
                encoded_domain = quote(domain, safe=":/")
                encoded_relative_path = quote(relative_path.replace(os.sep, "/"))
                full_url = f"{encoded_domain}/{encoded_relative_path}"

                # 获取原始文件名的第一个空格前的部分
                base_name = os.path.splitext(file)[0]

                # 构建新目录的完整路径，以原始目录名命名
                new_dir = os.path.join(output_directory, os.path.basename(root))

                # 创建新目录
                os.makedirs(new_dir, exist_ok=True)

                # 构建.strm文件的完整路径
                strm_file = os.path.join(new_dir, base_name + ".strm")

                # 如果.strm文件已经存在，跳过处理
                if os.path.exists(strm_file):
                    print(f"Skipping existing file: {strm_file}")
                    continue

                # 将链接写入.strm文件
                with open(strm_file, "w") as strm:
                    strm.write(full_url)

                # 输出处理信息
                print(f"Processed: {original_path} => {strm_file}")


if __name__ == "__main__":
    # 源目录
    source_directory = "X:\\pikpakShare"

    # 输出目录
    output_directory = "E:\\output"

    # 特定域名
    domain = "https://pikpak.share.host/d/pikpakShare/alienshare"

    # 处理目录
    process_directory(source_directory, output_directory, domain)
