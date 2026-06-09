with open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

s = c.find('COURSES = [')
e = c.find('class PythonLearnApp')
cs = c[s:e].split('=', 1)[1].strip()

# 找到第20课dict的结束位置（正确的结束）
idx20 = cs.find("'20. 文件读写进阶'")

# 从"test.csv") 字节")' 后面找
hint_end = cs.find("'hint': 'csv.writer(f).writerow([...])'}", idx20)
if hint_end > 0:
    actual_end = hint_end + len("'hint': 'csv.writer(f).writerow([...])'}")
    print(f'第20课实际结束位置: {actual_end}')
    print('结束后的50字符:')
    print(repr(cs[actual_end:actual_end+50]))
    
    # 检查是否有逗号
    after = cs[actual_end:actual_end+20].strip()
    print(f'结束后trim后的内容: {repr(after)}')
    if after.startswith(','):
        print('有逗号分隔 ✓')
    else:
        print('缺少逗号分隔 ✗')
