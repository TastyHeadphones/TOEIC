import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

for p in range(760, len(pages)//2 + 1):
    p_idx = p * 2
    if p_idx < len(pages):
        p_num = pages[p_idx-1]
        p_text = pages[p_idx].strip()
        lines = p_text.splitlines()
        non_empty = [l.strip() for l in lines if l.strip()]
        print(f"Page {p_num}: {len(non_empty)} non-empty lines. First 5 lines:")
        for idx, line in enumerate(non_empty[:5]):
            print(f"  {line!r}")
