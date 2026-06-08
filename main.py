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
        return 8

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
        if completed >= len(COURSES) and 'master' not in self.achievements:
            self.achievements.add('master')
            new_ach.append('🏆 Python大师 - 完成所有课程')
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
