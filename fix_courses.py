import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到COURSES列表的开始和结束
start_idx = content.find('COURSES = [')
end_idx = content.find(']\n\nclass PythonLearnApp')

# 提取前16个课程
courses_part = content[start_idx:end_idx+1]

# 构建新的课程列表
new_courses = courses_part[:-1]  # 去掉末尾的 ]

# 添加新课程17-24（使用三引号避免转义问题）
course_17 = """
    {'title': '17. 正则表达式', 'theory': '正则表达式用于匹配字符串模式。\\n示例：re.findall(r"\\\\d+", "abc123") → ["123"]', 'code': 'import re\\ntext = "我的电话是138-1234-5678，邮箱是test@example.com"\\nphones = re.findall(r"\\\\d{3}-\\\\d{4}-\\\\d{4}", text)\\nprint("电话号码:", phones)\\nemails = re.findall(r"[\\\\w.]+@[\\\\w.]+\\\\.\\\\w+", text)\\nprint("邮箱:", emails)', 'task': '从文本中提取所有数字', 'hint': 're.findall(r"\\\\d+", text)'},"""

course_18 = """
    {'title': '18. 装饰器', 'theory': '装饰器在不修改原函数的情况下增强功能。\\n示例：@timer 计算函数执行时间', 'code': 'import time\\n\\ndef timer(func):\\n    def wrapper(*args, **kwargs):\\n        start = time.time()\\n        result = func(*args, **kwargs)\\n        print(f"执行时间: {time.time()-start:.4f}秒")\\n        return result\\n    return wrapper\\n\\n@timer\\ndef slow_function():\\n    time.sleep(1)\\n    return "Done"\\n\\nprint(slow_function())', 'task': '写一个装饰器，记录函数被调用的次数', 'hint': '用闭包保存count变量'},"""

course_19 = """
    {'title': '19. 生成器', 'theory': '生成器用yield按需产生数据，节省内存。\\n示例：def gen(): yield 1; yield 2', 'code': 'def fibonacci(n):\\n    a, b = 0, 1\\n    for _ in range(n):\\n        yield a\\n        a, b = b, a + b\\n\\nfor num in fibonacci(10):\\n    print(num, end=" ")\\nprint()\\n\\n# 生成器表达式\\nsquares = (x**2 for x in range(10))\\nprint(list(squares))', 'task': '写一个生成器，产生1-100的偶数', 'hint': 'if x % 2 == 0: yield x'},"""

course_20 = """
    {'title': '20. 文件读写进阶', 'theory': 'CSV格式、路径操作、上下文管理器进阶。\\n示例：csv模块读写表格数据', 'code': 'import csv\\nimport os\\n\\n# 写入CSV\\ndata = [["姓名", "年龄"], ["小明", 18], ["小红", 20]]\\nwith open("test.csv", "w", newline="", encoding="utf-8") as f:\\n    writer = csv.writer(f)\\n    writer.writerows(data)\\n\\n# 读取CSV\\nwith open("test.csv", "r", encoding="utf-8") as f:\\n    reader = csv.reader(f)\\n    for row in reader:\\n        print(row)\\n\\nprint(f"文件大小: {os.path.getsize(\\'test.csv\\')} 字节")', 'task': '创建一个CSV文件存储3个学生的成绩', 'hint': 'csv.writer(f).writerow([...])'},"""

course_21 = """
    {'title': '21. 网络请求', 'theory': '用urllib发送HTTP请求，获取网络数据。\\n示例：urllib.request.urlopen("https://api.github.com")', 'code': 'import urllib.request\\nimport json\\n\\n# 使用标准库获取数据\\nurl = "https://jsonplaceholder.typicode.com/posts/1"\\ntry:\\n    with urllib.request.urlopen(url) as response:\\n        data = json.loads(response.read())\\n        print(f"标题: {data[\\'title\\']}")\\n        print(f"内容: {data[\\'body\\'][:50]}...")\\nexcept Exception as e:\\n    print(f"请求失败: {e}")', 'task': '请求一个API并打印返回的JSON数据', 'hint': 'urllib.request.urlopen(url)'},"""

course_22 = """
    {'title': '22. 多线程', 'theory': '多线程让程序同时执行多个任务。\\n示例：threading.Thread(target=func)', 'code': 'import threading\\nimport time\\n\\ndef worker(name, delay):\\n    print(f"{name} 开始工作")\\n    time.sleep(delay)\\n    print(f"{name} 完成工作")\\n\\n# 创建两个线程\\nt1 = threading.Thread(target=worker, args=("线程A", 2))\\nt2 = threading.Thread(target=worker, args=("线程B", 1))\\n\\nt1.start()\\nt2.start()\\nt1.join()\\nt2.join()\\nprint("所有线程完成")', 'task': '创建3个线程，分别打印不同的数字', 'hint': 'for i in range(3): threading.Thread(target=print_num, args=(i,)).start()'},"""

course_23 = """
    {'title': '23. 数据库操作', 'theory': 'SQLite是轻量级数据库，无需服务器。\\n示例：sqlite3.connect("test.db")', 'code': 'import sqlite3\\n\\n# 连接数据库（不存在则创建）\\nconn = sqlite3.connect(":memory:")\\ncursor = conn.cursor()\\n\\n# 创建表\\ncursor.execute("""CREATE TABLE users (\\n    id INTEGER PRIMARY KEY,\\n    name TEXT,\\n    age INTEGER\\n)""")\\n\\n# 插入数据\\ncursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("小明", 18))\\ncursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("小红", 20))\\nconn.commit()\\n\\n# 查询\\ncursor.execute("SELECT * FROM users")\\nfor row in cursor.fetchall():\\n    print(row)\\n\\nconn.close()', 'task': '创建一个书籍表，包含书名和作者', 'hint': 'CREATE TABLE books (title TEXT, author TEXT)'},"""

course_24 = """
    {'title': '24. 综合项目', 'theory': '综合运用所学知识完成一个实用项目。\\n本课任务：制作一个简单的天气查询工具', 'code': 'import urllib.request\\nimport json\\n\\ndef get_weather(city):\\n    # 模拟天气数据（实际应调用天气API）\\n    weather_data = {\\n        "北京": {"temp": 25, "weather": "晴"},\\n        "上海": {"temp": 28, "weather": "多云"},\\n        "广州": {"temp": 32, "weather": "雨"}\\n    }\\n    return weather_data.get(city, {"temp": "未知", "weather": "未知"})\\n\\ncity = "北京"\\nresult = get_weather(city)\\nprint(f"{city}的天气: {result[\\'weather\\']}, 温度: {result[\\'temp\\']}°C")\\n\\n# 扩展任务：尝试调用真实天气API\\n# API示例: http://wttr.in/Beijing?format=%C+%t', 'task': '扩展工具：支持查询多个城市，格式化输出', 'hint': 'for city in ["北京", "上海"]: print(get_weather(city))'},
]"""

new_courses += course_17 + course_18 + course_19 + course_20 + course_21 + course_22 + course_23 + course_24

# 构建新文件
new_content = content[:start_idx] + new_courses + content[end_idx+1:]

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('File rebuilt successfully')
