import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

out_lines = []
for i in range(1, len(pages), 2):
    page_num = int(pages[i])
    page_text = pages[i+1].strip()
    test_matches = re.findall(r'TEST \d+|Test \d+', page_text)
    part_matches = re.findall(r'PART \d+|Part \d+', page_text)
    q_matches = re.findall(r'(?:^|\n)(\d+)\.', page_text)
    q_ranges = f"Q{q_matches[0]}-Q{q_matches[-1]}" if q_matches else "No Qs"
    out_lines.append(f"Page {page_num:3d} (len={len(page_text):5d}): Tests: {test_matches}, Parts: {part_matches}, Qs: {q_ranges}")

with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch/page_details.txt", "w", encoding="utf-8") as out:
    out.write("\n".join(out_lines))
