import ast

with open('main.py', 'r', encoding='utf-8') as f:
    c = f.read()

s = c.find('COURSES = [')
e = c.find('class PythonLearnApp')
cs = c[s:e].split('=', 1)[1].strip()

# 找到第20课附近
idx = cs.find("'20.")
print('第20课位置:', idx)
print('前面50字符:')
print(repr(cs[idx-50:idx]))
print('第20课开始200字符:')
print(repr(cs[idx:idx+200]))
