import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

for i in range(1, len(pages), 2):
    page_num = int(pages[i])
    if 24 <= page_num <= 196:
        page_text = pages[i+1].strip()
        if "Look at the graphic" in page_text or "look at the graphic" in page_text:
            # Find which questions
            qs = re.findall(r'(\d+)\.', page_text)
            print(f"Page {page_num}: Qs: {qs}")
