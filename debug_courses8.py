import py_compile
import sys

# 捕获详细的语法错误信息
try:
    py_compile.compile('main.py', doraise=True)
    print('语法检查通过!')
except py_compile.PyCompileError as e:
    print(f'错误: {e}')
    print(f'错误文件: {e.file}')
    print(f'错误行号: {e.lineno}')
    print(f'错误位置: {e.offset}')
    print(f'错误文本: {e.text}')
    print(f'错误类型: {e.exc_type_name}')
