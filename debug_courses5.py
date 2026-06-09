with open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

s = c.find('COURSES = [')
e = c.find('class PythonLearnApp')
cs = c[s:e].split('=', 1)[1].strip()

# 找到第20课dict的结束
idx20 = cs.find("'20. 文件读写进阶'")
start = idx20 - 5

# 手动计数大括号
brace_count = 0
in_string = False
string_char = None
end_pos = None

for i in range(start, len(cs)):
    ch = cs[i]
    if not in_string:
        if ch in "'\"":
            in_string = True
            string_char = ch
        elif ch == '{':
            brace_count += 1
        elif ch == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i
                break
    else:
        if ch == string_char:
            if cs[i-1] == '\\':
                pass
            else:
                in_string = False

if end_pos:
    # 提取完整的第20课
    course20 = cs[start:end_pos+1]
    print('第20课内容长度:', len(course20))
    print('第20课内容:')
    print(course20)
    print()
    print('结束后的20字符:', repr(cs[end_pos+1:end_pos+21]))
