import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

def get_test_lines(test_idx):
    start_pages = [197, 256, 312, 369, 425, 481, 537, 593, 650, 706]
    sp = start_pages[test_idx - 1]
    ep = start_pages[test_idx] if test_idx < 10 else len(pages)//2
    
    test_lines = []
    for p in range(sp, ep):
        page_text = pages[p*2]
        # Find code blocks
        blocks = re.findall(r"```text\n(.*?)\n```", page_text, re.DOTALL)
        if not blocks:
            blocks = re.findall(r"```\n(.*?)\n```", page_text, re.DOTALL)
        for block in blocks:
            for line in block.splitlines():
                line_clean = line.strip()
                # Skip page numbers
                if line_clean == str(p) or line_clean == str(p-1) or line_clean == str(p+1):
                    continue
                test_lines.append(line)
    return test_lines

test_lines = get_test_lines(1)
print(f"Test 1 answer book: total lines = {len(test_lines)}")
print("First 20 lines of Test 1:")
for l in test_lines[:20]:
    print(repr(l))
print("="*40)
print("Lines 100 to 140:")
for l in test_lines[100:140]:
    print(repr(l))
