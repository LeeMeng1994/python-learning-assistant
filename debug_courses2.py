import ast

with open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

s = c.find('COURSES = [')
e = c.find('class PythonLearnApp')
cs = c[s:e].split('=', 1)[1].strip()

# 尝试逐行分析
lines = cs.split('\n')
for i, line in enumerate(lines):
    if '20.' in line and 'title' in line:
        print(f'找到第20课在第{i+1}行')
        # 显示前后5行
        for j in range(max(0, i-2), min(len(lines), i+8)):
            marker = '>>> ' if j == i else '    '
            print(f'{marker}{j+1}: {line[:120] if j == i else lines[j][:120]}')
        break

print('\n尝试找到问题...')
# 检查第20课条目是否完整
idx20 = cs.find("'20. 文件读写进阶'")
if idx20 > 0:
    # 找到这个dict的结束
    brace_count = 0
    in_string = False
    string_char = None
    for i, ch in enumerate(cs[idx20:]):
        if not in_string:
            if ch in "'\"":
                in_string = True
                string_char = ch
            elif ch == '{':
                brace_count += 1
            elif ch == '}':
                brace_count -= 1
                if brace_count == 0:
                    print(f'第20课dict结束位置: {idx20 + i}')
                    print('结束后的内容:')
                    print(repr(cs[idx20+i:idx20+i+30]))
                    break
        else:
            if ch == string_char and cs[idx20+i-1] != '\\':
                in_string = False
