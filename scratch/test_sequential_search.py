import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

def check_boundaries():
    start_pages = [197, 256, 312, 369, 425, 481, 537, 593, 650, 706, 762]
    
    for test_idx in range(1, 11):
        sp = start_pages[test_idx - 1]
        ep = start_pages[test_idx]
        
        test_lines = []
        for p in range(sp, ep):
            p_text = pages[p*2]
            blocks = re.findall(r"```text\n(.*?)\n```", p_text, re.DOTALL)
            if not blocks:
                blocks = re.findall(r"```\n(.*?)\n```", p_text, re.DOTALL)
            for block in blocks:
                for line in block.splitlines():
                    line_clean = line.strip()
                    if line_clean.isdigit():
                        val = int(line_clean)
                        if sp <= val <= ep:
                            continue
                    test_lines.append(line_clean)
                    
        key_end_idx = 0
        for idx, line in enumerate(test_lines):
            if line == "100.":
                for j in range(idx+1, min(idx+10, len(test_lines))):
                    if test_lines[j] == "）" or test_lines[j].startswith("）"):
                        key_end_idx = j + 1
                        break
                if key_end_idx > 0:
                    break
                    
        explanation_lines = test_lines[key_end_idx:]
        
        # Sequential search
        current_idx = 0
        q_indices = {}
        for q in range(1, 33):
            target = str(q)
            found = False
            for idx in range(current_idx, len(explanation_lines)):
                if explanation_lines[idx] == target:
                    # Let's inspect if this is likely a false positive
                    # Real question numbers are usually followed by English question text or options
                    # For Part 1 (1-6): followed by （, then option letter, then ）
                    # For Part 2 (7-31): followed by question text or （ or Q
                    # Let's look at lines immediately after
                    is_real = True
                    if q <= 6:
                        # Should have a （ A ） or similar nearby
                        has_opt = False
                        for offset in range(1, min(15, len(explanation_lines) - idx)):
                            if explanation_lines[idx+offset] == "（" or re.match(r"^[（(][A-D][）)]", explanation_lines[idx+offset]):
                                has_opt = True
                                break
                        if not has_opt:
                            is_real = False
                    else:
                        # Should have some lines before the next question, and shouldn't be too short
                        # Let's just check if it's not a single digit inside a sentence
                        # If the line before is "（" and the line after is "）", it's a transcript indicator!
                        if idx > 0 and explanation_lines[idx-1] == "（":
                            if idx + 1 < len(explanation_lines) and explanation_lines[idx+1].startswith("）"):
                                is_real = False
                    
                    if is_real:
                        q_indices[q] = idx
                        current_idx = idx + 1
                        found = True
                        break
            if not found:
                print(f"Test {test_idx:02d}: Failed to find Q{q}")
                
        # Print lengths of question blocks to see if any are suspicious
        for q in range(1, 32):
            if q in q_indices and (q+1) in q_indices:
                length = q_indices[q+1] - q_indices[q]
                if length < 6:
                    print(f"Test {test_idx:02d}: Q{q} block is very short ({length} lines):")
                    for offset in range(length):
                        print(f"  {explanation_lines[q_indices[q]+offset]}")

check_boundaries()
