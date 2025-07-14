import re
from collections import Counter


class TextProcessor:
    def __init__(self):
        self.keywords = set()

    def load_keywords(self, filepath):
        """
        加载关键词文件，支持中英文分隔符（空格、逗号、中文顿号、标点等）。
        自动过滤空词项，去重。
        """
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()

        # 使用广义分隔符分割，包括空格、中文符号、英文标点等
        separators = r"[\s,;，；、。.!@#$%^&*()_+=|\\/<>\[\]{}:\"'？“”‘’\-]+"
        words = re.split(separators, raw.strip())
        self.keywords = set(filter(None, words))

    def read_text_file(self, filepath):
        """
        读取文本文档（目前仅支持TXT），自动编码为UTF-8。
        """
        if filepath.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return ""

    def calculate_frequencies(self, text):
        """
        对每个关键词在整段文本中进行词频统计，结果为 Counter 类型。
        使用 str.count，避免正则误伤。
        """
        freq = Counter()
        for word in self.keywords:
            if word:
                freq[word] = text.count(word)
        return freq
