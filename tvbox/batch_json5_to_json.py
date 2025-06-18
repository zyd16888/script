import os
import json5
import json

def convert_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json5.load(f)  # 解析不标准 JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)  # 标准 JSON 输出

def batch_convert(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    success_count, fail_count = 0, 0

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.json', '.json5')):
            input_path = os.path.join(input_dir, filename)
            output_filename = os.path.splitext(filename)[0]+ "-transform" + '.json'
            # 处理空格
            output_filename = output_filename.replace(' ', '_')
            output_path = os.path.join(output_dir, output_filename)

            try:
                convert_file(input_path, output_path)
                print(f"✔ 转换成功：{filename} -> {output_filename}")
                success_count += 1
            except Exception as e:
                print(f"✘ 转换失败：{filename}，错误：{e}")
                fail_count += 1

    print(f"\n完成：成功 {success_count} 个，失败 {fail_count} 个")

if __name__ == '__main__':
    input_directory = './downloaded_jsons'    # 输入目录，放不标准的 JSON 文件
    output_directory = './downloaded_jsons/output'  # 输出目录，保存标准 JSON 文件

    batch_convert(input_directory, output_directory)
