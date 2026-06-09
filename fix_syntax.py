import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到COURSES列表
start = content.find('COURSES = [')
end = content.find('class PythonLearnApp')

if start == -1 or end == -1:
    print("找不到COURSES或class定义")
    exit(1)

courses_text = content[start:end]
print(f"COURSES区域长度: {len(courses_text)} chars")

# 尝试找到问题：检查每个课程条目是否以},结尾，然后跟着\n和下一个{
# 使用正则表达式查找所有课程条目
pattern = r"\{'title': '([^']+)'"
matches = list(re.finditer(pattern, courses_text))
print(f"找到 {len(matches)} 个课程标题")

for i, m in enumerate(matches):
    title = m.group(1)
    # 找到这个条目的结束位置
    entry_start = m.start()
    if i + 1 < len(matches):
        entry_end = matches[i+1].start()
    else:
        entry_end = courses_text.rfind(']')
    
    entry = courses_text[entry_start:entry_end]
    
    # 检查这个条目是否能被解析
    # 简单检查：条目应该以},或}结尾
    entry_stripped = entry.rstrip()
    if not (entry_stripped.endswith('},') or entry_stripped.endswith('}')):
        print(f"\n问题发现！课程 '{title}' 结尾异常:")
        print(f"  结尾20字符: {repr(entry_stripped[-20:])}")
    
    # 检查条目内部是否有未闭合的引号
    single_quotes = entry.count("'") - entry.count("\\'")
    double_quotes = entry.count('"') - entry.count('\\"')
    if single_quotes % 2 != 0:
        print(f"\n课程 '{title}' 单引号数量为奇数: {single_quotes}")
    if double_quotes % 2 != 0:
        print(f"\n课程 '{title}' 双引号数量为奇数: {double_quotes}")

print("\n检查完成")
