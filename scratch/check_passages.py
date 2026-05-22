import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

for test_idx in range(1, 11):
    start_pages = [197, 256, 312, 369, 425, 481, 537, 593, 650, 706, 762]
    sp = start_pages[test_idx - 1]
    ep = start_pages[test_idx]
    
    test_text = ""
    for p in range(sp, ep):
        p_text = pages[p*2]
        test_text += p_text
        
    # Find all occurrences of "Questions" followed by digits
    matches = re.findall(r"(Questions\s+\d+\s+through\s+\d+\s+refer\s+to\s+the\s+following\s+\w+)", test_text, re.IGNORECASE)
    print(f"Test {test_idx:02d}: found {len(matches)} standard matches")
    if len(matches) != 23: # 13 for Part 3, 10 for Part 4
        # Let's print what we found or look for any deviations
        print(f"  Expected 23, but found {len(matches)}!")
        # Let's print all lines starting with "Questions"
        all_qs = re.findall(r"(Questions.*)", test_text)
        print("  All 'Questions' lines:")
        for q in all_qs:
            print(f"    {q!r}")
