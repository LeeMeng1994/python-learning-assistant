# 直接读取文件的第72行（索引71）
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

line72 = lines[71]
print('第72行内容:')
print(line72)
print()
print('第72行repr:')
print(repr(line72))
print()

# 检查是否有异常字符
for i, ch in enumerate(line72):
    if ord(ch) > 127 and ch not in '。，、；：？！""''（）【】《》…—～｜　abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
        print(f'位置{i}: 字符 {repr(ch)} (U+{ord(ch):04X})')
