import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

# Let's inspect page 197 and 198
for p in [197, 198, 199, 200]:
    p_idx = p * 2
    if p_idx < len(pages):
        p_num = pages[p_idx-1]
        p_text = pages[p_idx]
        print(f"=== Page {p_num} ===")
        # find code blocks
        blocks = re.findall(r"```text\n(.*?)\n```", p_text, re.DOTALL)
        if not blocks:
            blocks = re.findall(r"```\n(.*?)\n```", p_text, re.DOTALL)
        for idx, block in enumerate(blocks):
            print(f"  Block {idx}: (lines: {len(block.splitlines())})")
            lines = block.splitlines()
            for i in range(min(40, len(lines))):
                print(f"    {lines[i]!r}")
