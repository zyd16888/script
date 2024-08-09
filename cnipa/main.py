import os
import json
import pandas as pd

# 定义JSON字段与Excel列名的对应关系
field_mapping = {
    "zhuanlisqh": "申请号/专利号",
    "zhuanlimc": "发明名称",
    "shenqingrxm": "申请人",
    "zhuanlilx": "专利类型",  # 1: 发明专利, 2:实用新型, 3: 外观设计
    "shenqingr": "申请日",
    "famingzlsqgbg": "发明专利申请公布号",
    "shouquanggh": "授权公告",
    "gongkaiggh": "公开公告号",
    "falvzt": "法律状态",
    "gongkaiggr": "授权公告日",
    "shouquanggr": "shouquanggr",
    "zhufenlh": "主分类号",
    "anjianywzt": "案件状态",
    "attention": "attention"  # 直接使用原字段名
}

# 专利类型的映射
patent_type_mapping = {
    "1": "发明专利",
    "2": "实用新型",
    "3": "外观设计"
}

# 创建一个空的DataFrame来存储所有数据
all_records = pd.DataFrame()

# 定义JSON文件所在的目录
json_folder_path = './json'  # 替换为你的文件夹路径

# 获取所有JSON文件名，并按文件名排序
file_list = sorted([f for f in os.listdir(json_folder_path) if f.endswith('.json')], key=lambda x: int(os.path.splitext(x)[0]))


# 遍历排序后的文件名列表
for filename in file_list:
    file_path = os.path.join(json_folder_path, filename)
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        records = data.get('data', {}).get('records', [])
        
        # 转换每条记录
        for record in records:
            processed_record = {}
            for json_field, excel_column in field_mapping.items():
                value = record.get(json_field)
                # 如果字段是专利类型，则进行映射转换
                if json_field == 'zhuanlilx':
                    value = patent_type_mapping.get(value, value)
                processed_record[excel_column] = value
            
            # 将记录添加到DataFrame中
            all_records = pd.concat([all_records, pd.DataFrame([processed_record])], ignore_index=True)


# 将所有记录保存到Excel文件
output_path = 'output2.xlsx'
all_records.to_excel(output_path, index=False)

print(f"数据已保存到 {output_path}")
