import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

# Search for pages containing Part 3 indicators
for p in range(197, 256):
    p_text = pages[p*2]
    if "Questions 32" in p_text or "Questions 32-34" in p_text or "Q32" in p_text or "32" in p_text:
        print(f"Page {p} contains 32-related text. Let's see some lines:")
        blocks = re.findall(r"```text\n(.*?)\n```", p_text, re.DOTALL)
        if not blocks:
            blocks = re.findall(r"```\n(.*?)\n```", p_text, re.DOTALL)
        for idx, block in enumerate(blocks):
            lines = block.splitlines()
            for line_idx, line in enumerate(lines):
                if "32" in line or "Questions" in line:
                    start = max(0, line_idx - 5)
                    end = min(len(lines), line_idx + 15)
                    print(f"  Block {idx}, lines {start}-{end}:")
                    for i in range(start, end):
                        print(f"    {lines[i]!r}")
