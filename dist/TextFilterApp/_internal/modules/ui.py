import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from modules.processor import TextProcessor
from modules.highlight import highlight_keywords
from modules.word_exporter import export_text_with_highlights
from modules.wordcloud_generator import generate_wordcloud
from pypinyin import lazy_pinyin
import csv


class TextFilterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("文本关键词筛选神器 V4.2 - 专业版")
        self.geometry("1200x800")
        self.configure(bg="#f5f5f5")
        self.resizable(True, True)

        self.processor = TextProcessor()
        self.raw_text = ""
        self.result_text = ""
        self.keyword_sort_reverse = False
        self.freq_sort_reverse = False
        self.current_stat_sort_col = None

        self.init_styles()
        self.create_widgets()

    def init_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", padding=6, relief="flat", font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=24, font=("Segoe UI", 10))
        style.configure("TLabel", background="#f5f5f5")

    def create_widgets(self):
        # 顶部功能按钮区
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", padx=12, pady=8)

        ttk.Button(control_frame, text="加载关键词", command=self.load_keywords).pack(side="left", padx=6)
        ttk.Button(control_frame, text="加载文档", command=self.load_document).pack(side="left", padx=6)
        ttk.Button(control_frame, text="导出为 Word", command=self.export_word).pack(side="left", padx=6)
        ttk.Button(control_frame, text="导出为 CSV", command=self.export_csv).pack(side="left", padx=6)
        ttk.Button(control_frame, text="生成词云图", command=self.generate_wordcloud).pack(side="left", padx=6)

        # 主体区域：上下可拖动（文本区域 + 关键词分析区）
        vertical_pane = tk.PanedWindow(self, orient=tk.VERTICAL)
        vertical_pane.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 文本内容区域
        self.text_area = tk.Text(vertical_pane, wrap="word", font=("Consolas", 11), relief="solid", bd=1)
        vertical_pane.add(self.text_area, stretch="always")

        # 下方左右可拖动：关键词列表 + 关键词频率
        horizontal_pane = tk.PanedWindow(vertical_pane, orient=tk.HORIZONTAL, sashwidth=6)
        vertical_pane.add(horizontal_pane)

        # 左侧关键词列表区域
        left_frame = ttk.Frame(horizontal_pane)
        horizontal_pane.add(left_frame, minsize=250)

        label_left = ttk.Label(left_frame, text="关键词（点击排序）", anchor="center", foreground="blue", cursor="hand2")
        label_left.pack(fill="x", pady=2)
        label_left.bind("<Button-1>", self.toggle_keyword_sort)

        self.keyword_listbox = tk.Listbox(left_frame, font=("Segoe UI", 10), height=18)
        self.keyword_scroll = ttk.Scrollbar(left_frame, command=self.keyword_listbox.yview)
        self.keyword_listbox.configure(yscrollcommand=self.keyword_scroll.set)
        self.keyword_listbox.pack(side="left", fill="both", expand=True)
        self.keyword_scroll.pack(side="right", fill="y")

        # 右侧关键词频率统计区域
        right_frame = ttk.Frame(horizontal_pane)
        horizontal_pane.add(right_frame)

        self.stat_tree = ttk.Treeview(right_frame, columns=("关键词", "频率"), show="headings", height=18)
        self.stat_tree.heading("关键词", text="关键词", anchor="center")
        self.stat_tree.heading("频率", text="频率", anchor="center")
        self.stat_tree.column("关键词", anchor="center", width=200)
        self.stat_tree.column("频率", anchor="center", width=100)

        tree_scroll = ttk.Scrollbar(right_frame, command=self.stat_tree.yview)
        self.stat_tree.configure(yscrollcommand=tree_scroll.set)

        self.stat_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        self.stat_tree.bind("<Button-1>", self.treeview_sort_handler)
        # 最底部版本显示区域
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", side="bottom")
        ttk.Separator(bottom_frame, orient="horizontal").pack(fill="x", padx=10)
        version_label = ttk.Label(
            bottom_frame,
            text="版本：4.2.0 - 本工具仅本地运行，不联网、不上传文档",
            anchor="e",
            font=("Segoe UI", 9, "italic"),
            foreground="#888"
        )
        version_label.pack(fill="x")

    def safe_pinyin(self, word):
        try:
            return ''.join(lazy_pinyin(word))
        except:
            return word

    def toggle_keyword_sort(self, event=None):
        self.keyword_sort_reverse = not self.keyword_sort_reverse
        sorted_keywords = sorted(
            self.processor.keywords,
            key=lambda x: self.safe_pinyin(x),
            reverse=self.keyword_sort_reverse
        )
        self.keyword_listbox.delete(0, tk.END)
        for kw in sorted_keywords:
            self.keyword_listbox.insert(tk.END, kw)
        self.keyword_listbox.insert(tk.END, f"—— 共 {len(sorted_keywords)} 个关键词 ——")

    def treeview_sort_handler(self, event):
        region = self.stat_tree.identify_region(event.x, event.y)
        if region != "heading":
            return

        col = self.stat_tree.identify_column(event.x)
        col_name = "关键词" if col == "#1" else "频率"

        if col_name == self.current_stat_sort_col:
            self.freq_sort_reverse = not self.freq_sort_reverse
        else:
            self.current_stat_sort_col = col_name
            self.freq_sort_reverse = False

        self.sort_stat_tree(by=col_name, reverse=self.freq_sort_reverse)

    def sort_stat_tree(self, by="关键词", reverse=False):
        children = self.stat_tree.get_children()
        if not children:
            return

        # 判断是否有 summary 行
        has_summary = False
        summary_values = None
        summary_item = children[-1]
        if "summary" in self.stat_tree.item(summary_item, "tags"):
            has_summary = True
            summary_values = self.stat_tree.item(summary_item, "values")
            data_items = children[:-1]
        else:
            data_items = children

        # 提取排序用数据
        data = [(self.stat_tree.set(iid, "关键词"), self.stat_tree.set(iid, "频率")) for iid in data_items]

        # 排序方式
        if by == "关键词":
            key_func = lambda x: self.safe_pinyin(x[0])
        else:
            key_func = lambda x: int(x[1])

        sorted_data = sorted(data, key=key_func, reverse=reverse)

        # 删除所有原始行（包括 summary）
        self.stat_tree.delete(*children)

        # 重新插入排序结果
        for word, count in sorted_data:
            self.stat_tree.insert("", tk.END, values=(word, count))

        # 插入 summary 行（锁死）
        if has_summary and summary_values:
            self.stat_tree.insert("", tk.END, values=summary_values, tags=("summary",))

    def load_keywords(self):
        path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt")])
        if not path:
            return
        self.processor.load_keywords(path)
        self.toggle_keyword_sort()
        messagebox.showinfo("成功", f"加载关键词 {len(self.processor.keywords)} 个")

    def load_document(self):
        messagebox.showinfo("使用说明", "✅ 本工具仅本地运行，不联网、不上传文档，请放心使用。")
        path = filedialog.askopenfilename(filetypes=[("文本文档", "*.txt"), ("Word文档", "*.docx")])
        if not path:
            return
        self.raw_text = self.processor.read_text_file(path)
        highlight_keywords(self.text_area, self.raw_text, self.processor.keywords)
        self.result_text = self.raw_text

        freq = self.processor.calculate_frequencies(self.raw_text)

        self.stat_tree.delete(*self.stat_tree.get_children())
        sorted_items = sorted(freq.items(), key=lambda x: self.safe_pinyin(x[0]))
        for word, count in sorted_items:
            self.stat_tree.insert("", tk.END, values=(word, count))

        total_keywords = len(freq)
        total_occurrences = sum(freq.values())

        self.stat_tree.insert(
            "", tk.END,
            values=(f"—— 共 {total_keywords} 个关键词 ——", f"{total_occurrences} 次总计 ——"),
            tags=("summary",)
        )

    def export_word(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word 文件", "*.docx")])
        if not save_path:
            return
        export_text_with_highlights(self.raw_text, list(self.processor.keywords), save_path)
        messagebox.showinfo("导出成功", f"已导出高亮Word至：{save_path}")

    def export_csv(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV 文件", "*.csv")])
        if not save_path:
            return
        freq = self.processor.calculate_frequencies(self.raw_text)
        with open(save_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["关键词", "频率"])
            for word, count in freq.items():
                writer.writerow([word, count])
        messagebox.showinfo("导出成功", f"已导出关键词统计CSV至：{save_path}")

    def generate_wordcloud(self):
        freq = self.processor.calculate_frequencies(self.raw_text)
        generate_wordcloud(freq)


def run_app():
    app = TextFilterApp()
    app.mainloop()
print("✅ 打包测试版本已生效")
