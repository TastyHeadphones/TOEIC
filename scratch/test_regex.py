import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

start_pages = [197, 256, 312, 369, 425, 481, 537, 593, 650, 706]
for idx, sp in enumerate(start_pages):
    page_text = pages[sp*2]
    keys = re.findall(r"(\d+)\.\s*（\s*([A-D])\s*）", page_text)
    print(f"Test {idx+1:02d} (starts page {sp}): found {len(keys)} keys")
