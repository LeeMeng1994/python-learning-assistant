import sys
import json
import os
import io
import contextlib
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QListWidget, QListWidgetItem,
    QProgressBar, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor

CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.python_learn')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'learn_progress.json')

def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []
        kw = QTextCharFormat()
        kw.setForeground(QColor('#ff79c6'))
        kw.setFontWeight(QFont.Weight.Bold)
        keywords = ['def','class','if','else','elif','for','while','return','import','from','try','except','True','False','None']
        for w in keywords:
            self.rules.append((r'\b' + w + r'\b', kw))
        s = QTextCharFormat()
        s.setForeground(QColor('#f1fa8c'))
        self.rules.append((r'"[^"]*"', s))
        self.rules.append((r"'[^']*'", s))
        c = QTextCharFormat()
        c.setForeground(QColor('#6272a4'))
        self.rules.append((r'#[^\n]*', c))
        f = QTextCharFormat()
        f.setForeground(QColor('#50fa7b'))
        self.rules.append((r'\b[A-Za-z0-9_]+(?=\()', f))
        n = QTextCharFormat()
        n.setForeground(QColor('#bd93f9'))
        self.rules.append((r'\b\d+\b', n))

    def highlightBlock(self, text):
        import re
        for p, fmt in self.rules:
            for m in re.finditer(p, text):
                self.setFormat(m.start(), m.end()-m.start(), fmt)

COURSES = [
    {'title': '1. Hello World', 'theory': 'print()函数输出内容到屏幕。\n示例：print("Hello, World!")', 'code': 'print("Hello, World!")', 'task': '输出：你好，Python！', 'hint': '用print()包裹你的文字'},
    {'title': '2. 变量', 'theory': '变量是存储数据的容器。\n示例：name = "小明"\nage = 18', 'code': 'name = "小明"\nprint(name)', 'task': '创建一个变量存储你的年龄并打印', 'hint': 'age = 你的年龄'},
    {'title': '3. if判断', 'theory': 'if语句根据条件执行代码。\n示例：if age >= 18: print("成年")', 'code': 'age = 20\nif age >= 18:\n    print("成年")\nelse:\n    print("未成年")', 'task': '判断一个数是否大于10', 'hint': '用if x > 10:'},
    {'title': '4. for循环', 'theory': 'for循环遍历序列。\n示例：for i in range(5): print(i)', 'code': 'for i in range(5):\n    print(i)', 'task': '打印1到10的所有数字', 'hint': 'range(1, 11)'},
    {'title': '5. 列表', 'theory': '列表存储多个数据。\n示例：fruits = ["苹果", "香蕉"]', 'code': 'fruits = ["苹果", "香蕉"]\nprint(fruits[0])', 'task': '创建一个包含3个颜色的列表并打印第二个', 'hint': 'colors = ["红", "绿", "蓝"]'},
    {'title': '6. 字典', 'theory': '字典存储键值对。\n示例：person = {"name": "小明", "age": 18}', 'code': 'person = {"name": "小明", "age": 18}\nprint(person["name"])', 'task': '创建一个字典存储你的姓名和年龄', 'hint': '{"name": "...", "age": ...}'},
    {'title': '7. 函数', 'theory': '函数封装可重用代码。\n示例：def greet(name): return "你好" + name', 'code': 'def greet(name):\n    return "你好, " + name\nprint(greet("小明"))', 'task': '写一个函数计算两数之和', 'hint': 'def add(a, b): return a + b'},
    {'title': '8. 文件操作', 'theory': '读写文件。\n示例：with open("test.txt", "w") as f: f.write("Hello")', 'code': 'with open("test.txt", "w") as f:\n    f.write("Hello")\nwith open("test.txt", "r") as f:\n    print(f.read())', 'task': '创建一个文件写入"Python学习"并读取打印', 'hint': 'open("file.txt", "w")'},
    {'title': '9. 异常处理', 'theory': 'try/except捕获错误，让程序更健壮。\n示例：try: 1/0 except: print("除零错误")', 'code': 'try:\n    result = 10 / 0\nexcept ZeroDivisionError:\n    print("不能除以零！")\nfinally:\n    print("程序继续运行")', 'task': '用try/except处理输入非数字的情况', 'hint': 'try: int(input()) except ValueError:'},
    {'title': '10. 字符串操作', 'theory': '字符串切片、查找、替换等操作。\n示例：s = "Hello"; s.upper() → "HELLO"', 'code': 's = "Hello, Python!"\nprint(s.upper())\nprint(s.replace("Python", "世界"))\nprint(s.split(", "))', 'task': '将"apple,banana,orange"分割成列表', 'hint': '使用split(",")'},
    {'title': '11. 列表进阶', 'theory': '列表切片、排序、列表推导式。\n示例：[x*2 for x in range(5)] → [0,2,4,6,8]', 'code': 'nums = [3, 1, 4, 1, 5]\nprint(sorted(nums))\nsquares = [x**2 for x in nums]\nprint(squares)', 'task': '用列表推导式生成1-10的平方列表', 'hint': '[x**2 for x in range(1, 11)]'},
    {'title': '12. 模块与包', 'theory': '用import导入模块，复用代码。\n示例：import random; random.randint(1,6)', 'code': 'import random\nimport datetime\nprint(random.randint(1, 100))\nprint(datetime.datetime.now())', 'task': '用random模块生成10个1-50的随机数', 'hint': 'for _ in range(10): print(random.randint(1,50))'},
    {'title': '13. 面向对象基础', 'theory': '类(class)是对象的蓝图，封装数据和方法。\n示例：class Dog: def bark(self): print("汪！")', 'code': 'class Dog:\n    def __init__(self, name):\n        self.name = name\n    def bark(self):\n        return f"{self.name}说：汪！"\n\ndog = Dog("旺财")\nprint(dog.bark())', 'task': '创建一个Student类，包含name和age属性', 'hint': 'class Student: def __init__(self, name, age): ...'},
    {'title': '14. 字典进阶', 'theory': '字典遍历、嵌套、get方法安全取值。\n示例：for k, v in d.items(): print(k, v)', 'code': 'scores = {"小明": 85, "小红": 92, "小刚": 78}\nfor name, score in scores.items():\n    print(f"{name}: {score}分")\nprint(scores.get("小李", "未找到"))', 'task': '统计字符串中每个字符出现的次数', 'hint': '用字典，遍历字符串，d[char] = d.get(char, 0) + 1'},
    {'title': '15. JSON数据处理', 'theory': 'JSON是数据交换格式，json模块可读写。\n示例：json.dumps({"a":1}) → "{\\"a\\":1}"', 'code': 'import json\ndata = {"name": "小明", "age": 18, "hobbies": ["读书", "编程"]}\njson_str = json.dumps(data, ensure_ascii=False)\nprint(json_str)\nparsed = json.loads(json_str)\nprint(parsed["name"])', 'task': '将字典{"city": "北京", "temp": 25}转为JSON字符串', 'hint': 'json.dumps(dict, ensure_ascii=False)'},
    {'title': '16. 综合练习', 'theory': '综合运用所学知识完成一个小项目。\n本课任务：制作一个简单的学生成绩管理系统', 'code': '# 学生成绩管理系统\nstudents = []\n\ndef add_student(name, score):\n    students.append({"name": name, "score": score})\n\ndef show_all():\n    for s in students:\n        print(s["name"] + ": " + str(s["score"]) + "分")\n\nadd_student("小明", 85)\nadd_student("小红", 92)\nshow_all()', 'task': '扩展系统：添加删除学生、计算平均分功能', 'hint': 'sum(s["score"] for s in students) / len(students)'},
    {'title': '17. 正则表达式', 'theory': '正则表达式用于匹配字符串模式。\n示例：re.findall(r"\\d+", "abc123") → ["123"]', 'code': 'import re\ntext = "我的电话是138-1234-5678，邮箱是test@example.com"\nphones = re.findall(r"\\d{3}-\\d{4}-\\d{4}", text)\nprint("电话号码:", phones)\nemails = re.findall(r"[\\w.]+@[\\w.]+\\.\\w+", text)\nprint("邮箱:", emails)', 'task': '从文本中提取所有数字', 'hint': 're.findall(r"\\d+", text)'},
    {'title': '18. 装饰器', 'theory': '装饰器在不修改原函数的情况下增强功能。\n示例：@timer 计算函数执行时间', 'code': 'import time\n\ndef timer(func):\n    def wrapper(*args, **kwargs):\n        start = time.time()\n        result = func(*args, **kwargs)\n        print(f"执行时间: {time.time()-start:.4f}秒")\n        return result\n    return wrapper\n\n@timer\ndef slow_function():\n    time.sleep(1)\n    return "Done"\n\nprint(slow_function())', 'task': '写一个装饰器，记录函数被调用的次数', 'hint': '用闭包保存count变量'},
    {'title': '19. 生成器', 'theory': '生成器用yield按需产生数据，节省内存。\n示例：def gen(): yield 1; yield 2', 'code': 'def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        yield a\n        a, b = b, a + b\n\nfor num in fibonacci(10):\n    print(num, end=" ")\nprint()\n\n# 生成器表达式\nsquares = (x**2 for x in range(10))\nprint(list(squares))', 'task': '写一个生成器，产生1-100的偶数', 'hint': 'if x % 2 == 0: yield x'},
    {'title': '20. 文件读写进阶', 'theory': 'CSV格式、路径操作、上下文管理器进阶。\n示例：csv模块读写表格数据', 'code': 'import csv\nimport os\n\n# 写入CSV\ndata = [["姓名", "年龄"], ["小明", 18], ["小红", 20]]\nwith open("test.csv", "w", newline="", encoding="utf-8") as f:\n    writer = csv.writer(f)\n    writer.writerows(data)\n\n# 读取CSV\nwith open("test.csv", "r", encoding="utf-8") as f:\n    reader = csv.reader(f)\n    for row in reader:\n        print(row)\n\nprint(f"文件大小: {os.path.getsize(chr(39)+chr(116)+chr(101)+chr(115)+chr(116)+chr(46)+chr(99)+chr(115)+chr(118)+chr(39))} 字节")', 'task': '创建一个CSV文件存储3个学生的成绩', 'hint': 'csv.writer(f).writerow([...])'},
    {'title': '21. 网络请求', 'theory': '用requests库发送HTTP请求，获取网络数据。\n示例：requests.get("https://api.github.com")', 'code': 'import urllib.request\nimport json\n\n# 使用标准库获取数据\nurl = "https://jsonplaceholder.typicode.com/posts/1"\ntry:\n    with urllib.request.urlopen(url) as response:\n        data = json.loads(response.read())\n        print(f"标题: {data[\'title\']}")\n        print(f"内容: {data[\'body\'][:50]}...")\nexcept Exception as e:\n    print(f"请求失败: {e}")', 'task': '请求一个API并打印返回的JSON数据', 'hint': 'urllib.request.urlopen(url)'},
    {'title': '22. 多线程', 'theory': '多线程让程序同时执行多个任务。\n示例：threading.Thread(target=func)', 'code': 'import threading\nimport time\n\ndef worker(name, delay):\n    print(f"{name} 开始工作")\n    time.sleep(delay)\n    print(f"{name} 完成工作")\n\n# 创建两个线程\nt1 = threading.Thread(target=worker, args=("线程A", 2))\nt2 = threading.Thread(target=worker, args=("线程B", 1))\n\nt1.start()\nt2.start()\nt1.join()\nt2.join()\nprint("所有线程完成")', 'task': '创建3个线程，分别打印不同的数字', 'hint': 'for i in range(3): threading.Thread(target=print_num, args=(i,)).start()'},
    {'title': '23. 数据库操作', 'theory': 'SQLite是轻量级数据库，无需服务器。\n示例：sqlite3.connect("test.db")', 'code': 'import sqlite3\n\n# 连接数据库（不存在则创建）\nconn = sqlite3.connect(":memory:")\ncursor = conn.cursor()\n\n# 创建表\ncursor.execute("""CREATE TABLE users (\n    id INTEGER PRIMARY KEY,\n    name TEXT,\n    age INTEGER\n)""")\n\n# 插入数据\ncursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("小明", 18))\ncursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("小红", 20))\nconn.commit()\n\n# 查询\ncursor.execute("SELECT * FROM users")\nfor row in cursor.fetchall():\n    print(row)\n\nconn.close()', 'task': '创建一个书籍表，包含书名和作者', 'hint': 'CREATE TABLE books (title TEXT, author TEXT)'},
    {'title': '24. 综合项目', 'theory': '综合运用所学知识完成一个实用项目。\n本课任务：制作一个简单的天气查询工具', 'code': 'import urllib.request\nimport json\n\ndef get_weather(city):\n    # 模拟天气数据（实际应调用天气API）\n    weather_data = {\n        "北京": {"temp": 25, "weather": "晴"},\n        "上海": {"temp": 28, "weather": "多云"},\n        "广州": {"temp": 32, "weather": "雨"}\n    }\n    return weather_data.get(city, {"temp": "未知", "weather": "未知"})\n\ncity = "北京"\nresult = get_weather(city)\nprint(f"{city}的天气: {result[\'weather\']}, 温度: {result[\'temp\']}°C")\n\n# 扩展任务：尝试调用真实天气API\n# API示例: http://wttr.in/Beijing?format=%C+%t', 'task': '扩展工具：支持查询多个城市，格式化输出', 'hint': 'for city in ["北京", "上海"]: print(get_weather(city))'},
]

class PythonLearnApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('🐍 Python学习助手')
        self.setMinimumSize(900, 650)
        self.current_course = 0
        self.progress = {}
        self.achievements = set()
        self.load_progress()
        self.init_ui()
        self.check_achievements()

    def init_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        layout = QHBoxLayout(cw)

        # 左侧课程列表
        left = QVBoxLayout()
        left.addWidget(QLabel('📚 课程列表'))
        self.course_list = QListWidget()
        for c in COURSES:
            item = QListWidgetItem(c['title'])
            if self.progress.get(c['title'], {}).get('completed'):
                item.setText('✅ ' + c['title'])
            self.course_list.addItem(item)
        self.course_list.currentRowChanged.connect(self.load_course)
        left.addWidget(self.course_list)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(COURSES))
        self.update_progress_bar()
        left.addWidget(QLabel('📊 学习进度'))
        left.addWidget(self.progress_bar)

        # 成就
        self.ach_label = QLabel('🏆 成就: 0/' + str(self.total_achievements()))
        left.addWidget(self.ach_label)

        # 按钮
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton('▶ 运行代码')
        self.run_btn.clicked.connect(self.run_code)
        btn_layout.addWidget(self.run_btn)

        self.quiz_btn = QPushButton('📝 练习题')
        self.quiz_btn.clicked.connect(self.show_quiz)
        btn_layout.addWidget(self.quiz_btn)

        self.reset_btn = QPushButton('🔄 重置代码')
        self.reset_btn.clicked.connect(self.reset_code)
        btn_layout.addWidget(self.reset_btn)

        self.complete_btn = QPushButton('✅ 完成课程')
        self.complete_btn.clicked.connect(self.complete_course)
        btn_layout.addWidget(self.complete_btn)
        left.addLayout(btn_layout)

        layout.addLayout(left, 1)

        # 右侧内容区
        right = QVBoxLayout()

        # 理论
        right.addWidget(QLabel('📖 理论知识'))
        self.theory_text = QTextEdit()
        self.theory_text.setReadOnly(True)
        right.addWidget(self.theory_text, 1)

        # 代码编辑器
        right.addWidget(QLabel('💻 代码编辑器'))
        self.code_edit = QTextEdit()
        self.highlighter = PythonHighlighter(self.code_edit.document())
        font = QFont('Consolas', 11)
        self.code_edit.setFont(font)
        self.code_edit.setStyleSheet('background-color: #282a36; color: #f8f8f2;')
        right.addWidget(self.code_edit, 2)

        # 输出
        right.addWidget(QLabel('📤 输出结果'))
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet('background-color: #1e1e1e; color: #4ec9b0;')
        right.addWidget(self.output, 1)

        layout.addLayout(right, 3)
        self.load_course(0)

    def total_achievements(self):
        return 10

    def update_progress_bar(self):
        completed = sum(1 for c in COURSES if self.progress.get(c['title'], {}).get('completed'))
        self.progress_bar.setMaximum(len(COURSES))
        self.progress_bar.setValue(completed)

    def load_course(self, index):
        if 0 <= index < len(COURSES):
            self.current_course = index
            c = COURSES[index]
            self.theory_text.setText(c['theory'])
            self.code_edit.setText(c['code'])
            self.output.clear()

    def reset_code(self):
        c = COURSES[self.current_course]
        self.code_edit.setText(c['code'])
        self.output.setText('🔄 代码已重置为默认代码')

    def run_code(self):
        code = self.code_edit.toPlainText()
        self.output.clear()
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            exec(code, {'__name__': '__main__'})
            output = sys.stdout.getvalue()
            self.output.setText(output or '(无输出)')
            self.check_run_achievement()
        except Exception as e:
            self.output.setText(f'❌ 错误: {str(e)}')
        finally:
            sys.stdout = old_stdout

    def show_quiz(self):
        c = COURSES[self.current_course]
        dialog = QDialog(self)
        dialog.setWindowTitle('📝 练习题')
        dialog.setMinimumSize(400, 300)
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel(f'课程: {c["title"]}'))
        layout.addWidget(QLabel('任务: ' + c['task']))
        layout.addWidget(QLabel('💡 提示: ' + c['hint']))

        # 代码输入
        code_input = QTextEdit()
        code_input.setPlaceholderText('在这里写代码...')
        code_input.setText(c['code'])
        layout.addWidget(code_input)

        # 运行按钮
        run_btn = QPushButton('▶ 运行')
        output = QTextEdit()
        output.setReadOnly(True)
        output.setStyleSheet('background-color: #1e1e1e; color: #4ec9b0;')

        def run_quiz():
            code = code_input.toPlainText()
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                exec(code, {'__name__': '__main__'})
                out = sys.stdout.getvalue()
                output.setText(out or '(无输出)')
            except Exception as e:
                output.setText(f'❌ 错误: {str(e)}')
            finally:
                sys.stdout = old_stdout

        run_btn.clicked.connect(run_quiz)
        layout.addWidget(run_btn)
        layout.addWidget(output)

        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def reset_code(self):
        c = COURSES[self.current_course]
        self.code_edit.setText(c['code'])
        self.output.setText('代码已重置为默认示例')

    def complete_course(self):
        c = COURSES[self.current_course]
        self.progress[c['title']] = {'completed': True, 'date': datetime.now().isoformat()}
        self.save_progress()
        self.update_progress_bar()
        self.course_list.item(self.current_course).setText('✅ ' + c['title'])
        self.check_achievements()
        QMessageBox.information(self, '恭喜！', f'完成课程: {c["title"]}')

    def check_achievements(self):
        completed = sum(1 for c in COURSES if self.progress.get(c['title'], {}).get('completed'))
        new_ach = []
        if completed >= 1 and 'first' not in self.achievements:
            self.achievements.add('first')
            new_ach.append('🎉 初次学习 - 完成第一门课程')
        if completed >= 3 and 'starter' not in self.achievements:
            self.achievements.add('starter')
            new_ach.append('🌟 学习起步 - 完成3门课程')
        if completed >= 8 and 'chapter1' not in self.achievements:
            self.achievements.add('chapter1')
            new_ach.append('📘 基础完成 - 完成第一章（1-8课）')
        if completed >= 12 and 'advanced' not in self.achievements:
            self.achievements.add('advanced')
            new_ach.append('🚀 进阶学习 - 完成12门课程')
        if completed >= 16 and 'chapter2' not in self.achievements:
            self.achievements.add('chapter2')
            new_ach.append('📗 进阶完成 - 完成第二章（9-16课）')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 高级学习 - 完成20门课程')
        if completed >= 16 and 'chapter2' not in self.achievements:
            self.achievements.add('chapter2')
            new_ach.append('📗 进阶完成 - 完成第二章（9-16课）')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 高级学习 - 完成20门课程')
        if completed >= 16 and 'chapter2' not in self.achievements:
            self.achievements.add('chapter2')
            new_ach.append('📗 进阶完成 - 完成第二章（9-16课）')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 高级学习 - 完成20门课程')
        if completed >= 16 and 'chapter2' not in self.achievements:
            self.achievements.add('chapter2')
            new_ach.append('📗 进阶完成 - 完成第二章（9-16课）')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 高级学习 - 完成20门课程')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 Python专家 - 完成20门课程')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 Python专家 - 完成20门课程')
        if completed >= 16 and 'chapter2' not in self.achievements:
            self.achievements.add('chapter2')
            new_ach.append('📗 进阶完成 - 完成第二章（9-16课）')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 高级学习 - 完成20门课程')
        if completed >= 16 and 'chapter2' not in self.achievements:
            self.achievements.add('chapter2')
            new_ach.append('📗 进阶完成 - 完成第二章（9-16课）')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 高级学习 - 完成20门课程')
        if completed >= 16 and 'chapter2' not in self.achievements:
            self.achievements.add('chapter2')
            new_ach.append('📗 进阶完成 - 完成第二章（9-16课）')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 高级学习 - 完成20门课程')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 Python专家 - 完成20门课程')
        if completed >= 16 and 'chapter2' not in self.achievements:
            self.achievements.add('chapter2')
            new_ach.append('📗 进阶完成 - 完成第二章（9-16课）')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 Python高手 - 完成20门课程')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 Python专家 - 完成20门课程')
        if completed >= 16 and 'chapter2' not in self.achievements:
            self.achievements.add('chapter2')
            new_ach.append('📗 进阶完成 - 完成第二章（9-16课）')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 高级学习 - 完成20门课程')
        if completed >= 16 and 'chapter2' not in self.achievements:
            self.achievements.add('chapter2')
            new_ach.append('📗 进阶完成 - 完成第二章（9-16课）')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 高级学习 - 完成20门课程')
        if completed >= 16 and 'master' not in self.achievements:
            self.achievements.add('master')
            new_ach.append('🏆 Python大师 - 完成所有课程')
        if completed >= 20 and 'expert' not in self.achievements:
            self.achievements.add('expert')
            new_ach.append('🎯 Python专家 - 完成20门课程')
        if completed >= len(COURSES) and 'legend' not in self.achievements:
            self.achievements.add('legend')
            new_ach.append('👑 Python传奇 - 完成所有课程（24门）')
        if new_ach:
            self.save_progress()
            self.ach_label.setText(f'🏆 成就: {len(self.achievements)}/{self.total_achievements()}')
            QMessageBox.information(self, '获得成就！', '\n'.join(new_ach))

    def check_run_achievement(self):
        runs = self.progress.get('total_runs', 0) + 1
        self.progress['total_runs'] = runs
        self.save_progress()
        if runs >= 10 and 'runner' not in self.achievements:
            self.achievements.add('runner')
            self.save_progress()
            self.ach_label.setText(f'🏆 成就: {len(self.achievements)}/{self.total_achievements()}')
            QMessageBox.information(self, '获得成就！', '⚡ 代码奔跑者 - 运行代码10次')

    def load_progress(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.progress = data.get('progress', {})
                    self.achievements = set(data.get('achievements', []))
            except:
                pass

    def save_progress(self):
        ensure_config_dir()
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'progress': self.progress, 'achievements': list(self.achievements)}, f, ensure_ascii=False)

    def closeEvent(self, event):
        self.save_progress()
        event.accept()

def main():
    ensure_config_dir()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = PythonLearnApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
