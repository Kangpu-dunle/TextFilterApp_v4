import tkinter as tk
import re

def highlight_keywords(text_widget: tk.Text, content: str, keywords: set):
    """
    在 Tkinter Text 控件中高亮关键词，使用淡黄色背景。
    - 优先匹配长关键词，避免重叠错配。
    """
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, content)
    text_widget.tag_remove("highlight", "1.0", tk.END)
    text_widget.tag_configure("highlight", background="#fff2a8", foreground="black")

    # 关键词按照长度降序排序，避免“专业”先匹配后导致“专业课”无法匹配
    sorted_keywords = sorted(keywords, key=len, reverse=True)

    for kw in sorted_keywords:
        if not kw.strip():
            continue
        escaped_kw = re.escape(kw)
        start = "1.0"
        while True:
            pos = text_widget.search(escaped_kw, start, stopindex=tk.END, regexp=True)
            if not pos:
                break
            end = f"{pos}+{len(kw)}c"
            text_widget.tag_add("highlight", pos, end)
            start = end
