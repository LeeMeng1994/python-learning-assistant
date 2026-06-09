# 检查文件是否有BOM或编码问题
with open('main.py', 'rb') as f:
    raw = f.read()

print(f'文件总大小: {len(raw)} bytes')
print(f'前3字节: {raw[:3]}')
if raw[:3] == b'\xef\xbb\xbf':
    print('有UTF-8 BOM')
else:
    print('无BOM')

# 找到第72行的位置（按\n分割）
lines_raw = raw.split(b'\n')
print(f'总行数: {len(lines_raw)}')
if len(lines_raw) > 71:
    line72_raw = lines_raw[71]
    print(f'第72行原始长度: {len(line72_raw)} bytes')
    print(f'第72行原始内容(前100bytes): {line72_raw[:100]}')
    
    # 检查是否有异常字节
    for i, b in enumerate(line72_raw):
        if b > 127:
            # 检查是否是合法的UTF-8序列
            if i+1 < len(line72_raw) and (line72_raw[i+1] & 0xC0) == 0x80:
                pass  # 可能是多字节UTF-8
            elif i > 0 and (line72_raw[i-1] & 0xC0) == 0xC0:
                pass  # 多字节UTF-8的后续字节
            else:
                print(f'位置{i}: 异常字节 0x{b:02X}')
