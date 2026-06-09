import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到第20课的完整条目并替换
old_course = """    {'title': '20. 文件读写进阶', 'theory': 'CSV格式、路径操作、上下文管理器进阶。\\n示例：csv模块读写表格数据', 'code': 'import csv\\nimport os\\n\\n# 写入CSV\\ndata = [["姓名", "年龄"], ["小明", 18], ["小红", 20]]\\nwith open("test.csv", "w", newline="", encoding="utf-8") as f:\\n    writer = csv.writer(f)\\n    writer.writerows(data)\\n\\n# 读取CSV\\nwith open("test.csv", "r", encoding="utf-8") as f:\\n    reader = csv.reader(f)\\n    for row in reader:\\n        print(row)\\n\\nprint(f"文件大小: {os.path.getsize(\\'test.csv\\')} 字节")', 'task': '创建一个CSV文件存储3个学生的成绩', 'hint': 'csv.writer(f).writerow([...])'},"""

new_course = """    {
        'title': '20. 文件读写进阶',
        'theory': 'CSV格式、路径操作、上下文管理器进阶。\\n示例：csv模块读写表格数据',
        'code': '''import csv
import os

# 写入CSV
data = [["姓名", "年龄"], ["小明", 18], ["小红", 20]]
with open("test.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(data)

# 读取CSV
with open("test.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)

print(f"文件大小: {os.path.getsize('test.csv')} 字节")''',
        'task': '创建一个CSV文件存储3个学生的成绩',
        'hint': 'csv.writer(f).writerow([...])'
    },"""

if old_course in content:
    content = content.replace(old_course, new_course)
    print("替换成功（长版本）")
else:
    # 尝试查找并替换（可能格式略有不同）
    print("长版本未找到，尝试查找第20课...")
    start = content.find("'20. 文件读写进阶'")
    if start > 0:
        # 找到这个条目的开始（前面的空格和{）
        entry_start = content.rfind('{', start-20, start)
        # 找到这个条目的结束（},）
        entry_end = content.find("'hint': 'csv.writer(f).writerow([...])'}", start)
        if entry_end > 0:
            entry_end = entry_end + len("'hint': 'csv.writer(f).writerow([...])'}") + 1  # +1 for }
            old = content[entry_start:entry_end]
            print(f"找到旧内容，长度: {len(old)}")
            print("旧内容前100字符:", repr(old[:100]))
            print("旧内容后100字符:", repr(old[-100:]))
            content = content[:entry_start] + new_course + content[entry_end:]
            print("替换成功")
        else:
            print("找不到hint结束标记")
    else:
        print("找不到第20课")

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("文件已保存")
