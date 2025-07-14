from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import platform

def get_chinese_font_path():
    """
    自动检测系统可用的中文字体路径。
    """
    system = platform.system()
    font_paths = []

    if system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",       # 微软雅黑
            "C:/Windows/Fonts/simsun.ttc",     # 宋体
            "C:/Windows/Fonts/simhei.ttf",     # 黑体
        ]
    elif system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/PingFang.ttc",
        ]
    elif system == "Linux":
        font_paths = [
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        ]

    for path in font_paths:
        if os.path.exists(path):
            return path

    return None  # 未找到中文字体

def generate_wordcloud(freq_dict, font_path=None):
    """
    使用关键词频率生成中文词云图。
    :param freq_dict: dict, 关键词 -> 频率
    :param font_path: str, 可选字体路径（如无则自动检测）
    """
    if not font_path:
        font_path = get_chinese_font_path()
        if not font_path:
            print("❌ 未检测到可用的中文字体，可能导致词云无法显示中文。")
            return

    wc = WordCloud(
        font_path=font_path,
        width=1000,
        height=600,
        background_color='white',
        max_words=200,
        max_font_size=120,
        scale=2,
        random_state=42
    )
    wc.generate_from_frequencies(freq_dict)

    # 显示词云图
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout()
    plt.show()
