import re
from chinese2digits import coreCHToDigits

def convert_chapter(chapter_str):
    """将中文章节编号转换为数字，并在'章'后添加空格"""
    match = re.match(r'第([一二三四五六七八九零百千万亿〇两]+)章(.*)', chapter_str)
    if match:
        chinese_num, title = match.groups()
        try:
            num = int(coreCHToDigits(chinese_num))  # 正确调用转换方法
            print(f'第{num}章 {title}')  # 输出转换后的章节标题
            return f'第{num}章 {title}'  # 添加空格
        except ValueError:
            return chapter_str
    return chapter_str

def process_txt_file(input_file, output_file):
    with open(input_file, 'r', encoding='gb2312', errors='ignore') as infile, \
         open(output_file, 'w', encoding='gb2312') as outfile:  # 转换为 UTF-8 方便处理
        for line in infile:
            outfile.write(convert_chapter(line.strip()) + '\n')

if __name__ == "__main__":
    input_filename = r"C:\Users\zyd47\Desktop\神话版三国精校版.txt"  # 替换为你的输入文件名
    output_filename = r"C:\Users\zyd47\Desktop\processed_神话版三国.txt"  # 处理后的文件
    process_txt_file(input_filename, output_filename)
    print("处理完成，结果已保存到", output_filename)
