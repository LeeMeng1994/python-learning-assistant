with open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

s = c.find('COURSES = [')
e = c.find('class PythonLearnApp')
cs = c[s:e].split('=', 1)[1].strip()

# 找到第20课dict的结束 - 使用更简单的方法
idx20 = cs.find("'20. 文件读写进阶'")
print(f'第20课起始位置: {idx20}')

# 从title前面5个字符开始（应该是 { 或空格）
start = idx20 - 5
print(f'从位置{start}开始查找:')
print(repr(cs[start:start+20]))

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
            print(f'  位置{i}: 遇到 }}, brace_count={brace_count}')
            if brace_count == 0:
                end_pos = i
                print(f'第20课dict结束位置: {end_pos}')
                print('结束后的30字符:')
                print(repr(cs[end_pos:end_pos+30]))
                break
    else:
        if ch == string_char:
            # 检查前一个字符是否是反斜杠
            if cs[i-1] == '\\':
                pass
            else:
                in_string = False

print(f'\n最终brace_count: {brace_count}')
print(f'end_pos: {end_pos}')
