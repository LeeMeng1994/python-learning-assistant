import sys
import json
import os
import io
import contextlib
import random
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QListWidget, QListWidgetItem,
    QProgressBar, QMessageBox, QFrame, QDialog,
    QRadioButton, QButtonGroup, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".python_learn")
CONFIG_FILE = os.path.join(CONFIG_DIR, "learn_progress.json")

def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor('#ff79c6'))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = ['and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'False', 'finally', 'for',
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'True', 'try', 'while', 'with', 'yield']
        for word in keywords:
            self.highlighting_rules.append((r'\b' + word + r'\b', keyword_format))
        string_format = QTextCharFormat()
        string_format.setForeground(QColor('#f1fa8c'))
        self.highlighting_rules.append((r" [^ ] *", string_format))
        self.highlighting_rules.append((r\[^\]*', string_format))
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor('#6272a4'))
        self.highlighting_rules.append((r'#[^\n]*', comment_format))
        function_format = QTextCharFormat()
        function_format.setForeground(QColor('#50fa7b'))
        self.highlighting_rules.append((r'\b[A-Za-z0-9_]+(?=\()', function_format))
        number_format = QTextCharFormat()
        number_format.setForeground(QColor('#bd93f9'))
        self.highlighting_rules.append((r'\b[0-9]+\b', number_format))

    def highlightBlock(self, text):
        import re
        for pattern, fmt in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, fmt)
class QuizDialog(QDialog):
x=1
x=1
