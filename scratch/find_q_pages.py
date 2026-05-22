import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

# Pages 24 to 196 are the Test Book pages.
# Let's map Test Book pages to Test 01 ~ Test 10.
# We know:
# Test 1: page 24-41
# Test 2: page 42-59
# Test 3: page 60-76
# Test 4: page 77-93
# Test 5: page 94-110
# Test 6: page 111-127
# Test 7: page 128-144
# Test 8: page 145-162
# Test 9: page 163-179
# Test 10: page 180-196

# Let's verify which questions appear on which pages.
test_ranges = [
    (1, 24, 41),
    (2, 42, 59),
    (3, 60, 76),
    (4, 77, 93),
    (5, 94, 110),
    (6, 111, 127),
    (7, 128, 144),
    (8, 145, 162),
    (9, 163, 179),
    (10, 180, 196)
]

page_contents = {}
for i in range(1, len(pages), 2):
    p_num = int(pages[i])
    page_contents[p_num] = pages[i+1]

with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch/question_page_map.txt", "w", encoding="utf-8") as out:
    for test_idx, start_p, end_p in test_ranges:
        out.write(f"=== TEST {test_idx:02d} ===\n")
        for p in range(start_p, end_p + 1):
            text = page_contents.get(p, "")
            # Find question numbers at the start of a line or after spaces, followed by a dot
            # e.g., 34. or 65.
            qs = re.findall(r'(?:^|\n|\s)(\d+)\.', text)
            # Filter qs to keep only valid question numbers 1-100 (and preserve order)
            valid_qs = []
            for q in qs:
                try:
                    q_num = int(q)
                    if 1 <= q_num <= 100:
                        valid_qs.append(q_num)
                except ValueError:
                    pass
            # De-duplicate while preserving order
            seen = set()
            unique_qs = []
            for q in valid_qs:
                if q not in seen:
                    seen.add(q)
                    unique_qs.append(q)
            out.write(f"Page {p:3d}: Qs {unique_qs}\n")
