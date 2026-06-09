import ast

with open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

s = c.find('COURSES = [')
e = c.find('class PythonLearnApp')
cs = c[s:e].split('=', 1)[1].strip()

# 找到第20课dict的结束
idx20 = cs.find("'20. 文件读写进阶'")
print(f'第20课起始位置: {idx20}')

brace_count = 0
in_string = False
string_char = None
end_pos = None

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
                end_pos = idx20 + i
                print(f'第20课dict结束位置: {end_pos}')
                print('结束后的30字符:')
                print(repr(cs[end_pos:end_pos+30]))
                break
    else:
        if ch == string_char:
            # 检查是否是转义
            if i > 0 and cs[idx20+i-1] == '\\':
                pass  # 转义引号，继续
            else:
                in_string = False

if end_pos:
    # 提取完整的第20课
    course20 = cs[idx20-5:end_pos+1]  # 包含前面的空格和后面的}
    print('\n第20课完整内容:')
    print(course20)
    
    # 尝试单独解析
    print('\n尝试解析第20课...')
    try:
        # 包装成列表
        ast.literal_eval('[' + course20.strip() + ']')
        print('第20课单独解析成功!')
    except Exception as ex:
        print(f'第20课单独解析失败: {ex}')
