import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

# Let's collect all lines from the code blocks of Test 1 (pages 197 to 255)
test1_lines = []
for p in range(197, 256):
    p_text = pages[p*2]
    # find code blocks
    blocks = re.findall(r"```text\n(.*?)\n```", p_text, re.DOTALL)
    if not blocks:
        blocks = re.findall(r"```\n(.*?)\n```", p_text, re.DOTALL)
    for block in blocks:
        for line in block.splitlines():
            line_clean = line.strip()
            # Skip page numbers of the Answer Book
            if line_clean.isdigit():
                val = int(line_clean)
                if 197 <= val <= 255:
                    continue
            test1_lines.append(line_clean)

# Find where the answer key ends.
# The answer key has 1. ... 100.
# Let's find the index of "100." and its closing "）"
key_end_idx = 0
for idx, line in enumerate(test1_lines):
    if line == "100.":
        # look ahead for "）"
        for j in range(idx+1, min(idx+10, len(test1_lines))):
            if test1_lines[j] == "）":
                key_end_idx = j + 1
                break
        if key_end_idx > 0:
            break

print(f"Key end index: {key_end_idx}")
explanation_lines = test1_lines[key_end_idx:]

# Now find all lines in explanation_lines that are exactly digits 1 to 100
found_qs = []
for idx, line in enumerate(explanation_lines):
    if line.isdigit():
        val = int(line)
        if 1 <= val <= 100:
            found_qs.append((val, idx))

print(f"Found {len(found_qs)} question boundaries in explanations:")
print([q[0] for q in found_qs])
