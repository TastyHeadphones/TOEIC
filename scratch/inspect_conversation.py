import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

for p in range(209, 213):
    p_text = pages[p*2]
    print(f"=== Page {p} ===")
    blocks = re.findall(r"```text\n(.*?)\n```", p_text, re.DOTALL)
    if not blocks:
        blocks = re.findall(r"```\n(.*?)\n```", p_text, re.DOTALL)
    for idx, block in enumerate(blocks):
        print(f"  Block {idx}:")
        for line in block.splitlines():
            print(f"    {line}")
