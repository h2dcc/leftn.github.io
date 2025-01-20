import os
import re
from openai import OpenAI

# 配置
API_KEY = ""  # 从环境变量中获取 API 密钥
CONTENT_DIR = "d:/hugo/lawtee.github.io/content/posts"  # 相对于仓库根目录的路径
MAX_TOKENS = 8192  # API的最大token限制
CHUNK_SIZE = 6000  # 每块的最大token数量（根据实际情况调整）

# 固定翻译映射
CATEGORY_TRANSLATIONS = {
    "瞬间": "Moments",
    "生活": "Life",
    "法律": "Law",
    "IT互联网": "Network",
    "社会": "Society"
}

# 初始化OpenAI客户端
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

# 翻译函数
def translate_text(text):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful translator. Translate the following text into English."},
            {"role": "user", "content": text},
        ],
        max_tokens=MAX_TOKENS,  # 指定最大输出长度
        stream=False
    )
    return response.choices[0].message.content

# 分块翻译函数
def translate_long_text(text, chunk_size=CHUNK_SIZE):
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    translated_chunks = []
    for chunk in chunks:
        try:
            translated_chunk = translate_text(chunk)
            translated_chunks.append(translated_chunk)
        except Exception as e:
            print(f"分块翻译失败，错误：{e}")
            translated_chunks.append("")  # 如果失败，添加空字符串
    return "".join(translated_chunks)

# 提取并处理Front Matter
def process_front_matter(content):
    # 匹配Front Matter部分
    front_matter_match = re.search(r"---\n(.*?)\n---", content, re.DOTALL)
    if not front_matter_match:
        return content  # 如果没有Front Matter，直接返回原文

    front_matter = front_matter_match.group(1)
    body = content[front_matter_match.end():].strip()

    # 处理Front Matter中的categories字段
    if "categories:" in front_matter:
        for cn_category, en_category in CATEGORY_TRANSLATIONS.items():
            front_matter = front_matter.replace(f"categories: {cn_category}", f"categories: {en_category}")

    # 重新组合Front Matter和正文
    return f"---\n{front_matter}\n---\n\n{body}"

# 遍历content目录
for root, dirs, files in os.walk(CONTENT_DIR):
    # 检查是否存在index.md但不存在index.en.md
    if "index.md" in files and "index.en.md" not in files:
        index_md_path = os.path.join(root, "index.md")
        index_en_md_path = os.path.join(root, "index.en.md")

        # 读取index.md内容
        with open(index_md_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 处理Front Matter
        content = process_front_matter(content)

        # 分块翻译内容
        try:
            translated_content = translate_long_text(content)
            # 保存翻译后的内容为index.en.md
            with open(index_en_md_path, "w", encoding="utf-8") as f:
                f.write(translated_content)
            print(f"已翻译并保存：{index_en_md_path}")
        except Exception as e:
            print(f"翻译失败：{index_md_path}，错误：{e}")

print("批量翻译完成！")