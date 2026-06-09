# 修复第72行的语法错误
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 第72行（索引71）有语法错误，替换为正确的内容
lines[71] = """    {'title': '20. 文件读写进阶', 'theory': 'CSV格式、路径操作、上下文管理器进阶。\\n示例：csv模块读写表格数据', 'code': 'import csv\\nimport os\\n\\n# 写入CSV\\ndata = [["姓名", "年龄"], ["小明", 18], ["小红", 20]]\\nwith open("test.csv", "w", newline="", encoding="utf-8") as f:\\n    writer = csv.writer(f)\\n    writer.writerows(data)\\n\\n# 读取CSV\\nwith open("test.csv", "r", encoding="utf-8") as f:\\n    reader = csv.reader(f)\\n    for row in reader:\\n        print(row)\\n\\nprint(f"文件大小: {os.path.getsize(chr(39)+chr(116)+chr(101)+chr(115)+chr(116)+chr(46)+chr(99)+chr(115)+chr(118)+chr(39))} 字节")', 'task': '创建一个CSV文件存储3个学生的成绩', 'hint': 'csv.writer(f).writerow([...])'},\n"""

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Line 72 fixed')
