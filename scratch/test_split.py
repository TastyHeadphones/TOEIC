import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

# Collect Test 1 lines
test_lines = []
for p in range(197, 256):
    p_text = pages[p*2]
    blocks = re.findall(r"```text\n(.*?)\n```", p_text, re.DOTALL)
    if not blocks:
        blocks = re.findall(r"```\n(.*?)\n```", p_text, re.DOTALL)
    for block in blocks:
        for line in block.splitlines():
            line_clean = line.strip()
            if line_clean.isdigit():
                val = int(line_clean)
                if 197 <= val <= 255:
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

passage_headers = []
for idx, line in enumerate(explanation_lines):
    if re.match(r"^Questions\s+\d+\s+through\s+\d+\s+refer\s+to\s+the\s+following", line, re.IGNORECASE):
        passage_headers.append((line, idx))

def is_speaker_label(s):
    s_clean = re.sub(r'[:：]$', '', s.strip()).strip()
    return bool(re.match(r"^(?:M\d?|W\d?|Man\s*\d?|Woman\s*\d?)$", s_clean, re.IGNORECASE))

def ends_with_sentence_punctuation(s):
    s = s.strip()
    if not s:
        return False
    return s[-1] in ["。", "？", "！", "”", "；", "：", ".", "?", "!"]

def is_vocab_start(line, last_chi_line):
    line = line.strip()
    if not line:
        return False
    if not any(c.isalpha() for c in line):
        return False
    if last_chi_line and ends_with_sentence_punctuation(last_chi_line):
        return True
    clean_start = line.lstrip("…·-—–. ")
    if clean_start and clean_start[0].islower():
        return True
    return False

def split_transcript_vocab(lines):
    eng_trans = []
    chi_trans = []
    vocab = []
    
    state = "english"
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in line_clean)
        
        if state == "english":
            if has_chinese:
                state = "chinese"
                if eng_trans and is_speaker_label(eng_trans[-1]):
                    chi_trans.append(eng_trans.pop())
        elif state == "chinese":
            if not has_chinese:
                if not is_speaker_label(line_clean):
                    last_chi_line = ""
                    for l in reversed(chi_trans):
                        if any('\u4e00' <= char <= '\u9fff' for char in l):
                            last_chi_line = l
                            break
                    if is_vocab_start(line_clean, last_chi_line):
                        state = "vocab"
                    
        if state == "english":
            eng_trans.append(line_clean)
        elif state == "chinese":
            chi_trans.append(line_clean)
        elif state == "vocab":
            vocab.append(line_clean)
            
    return eng_trans, chi_trans, vocab

def find_real_question_index(lines, q_num, start_idx=0):
    q_str = str(q_num)
    for idx in range(start_idx, len(lines)):
        if lines[idx] == q_str:
            is_indicator = False
            if idx > 0 and lines[idx-1] == "（":
                if idx + 1 < len(lines) and lines[idx+1].startswith("）"):
                    is_indicator = True
            if not is_indicator:
                return idx
    raise ValueError(f"Question {q_num} not found")

for p_idx in range(len(passage_headers)):
    start_line_idx = passage_headers[p_idx][1]
    end_line_idx = passage_headers[p_idx+1][1] if p_idx < len(passage_headers)-1 else len(explanation_lines)
    
    p_lines = explanation_lines[start_line_idx:end_line_idx]
    header_text = p_lines[0]
    
    match_qs = re.search(r"Questions\s+(\d+)\s+through\s+(\d+)", header_text, re.IGNORECASE)
    if not match_qs:
        continue
    q_start = int(match_qs.group(1))
    
    try:
        idx_q1 = find_real_question_index(p_lines, q_start, 0)
        idx_q2 = find_real_question_index(p_lines, q_start + 1, idx_q1 + 1)
        idx_q3 = find_real_question_index(p_lines, q_start + 2, idx_q2 + 1)
    except ValueError as e:
        print(f"Passage Q{q_start}: Error finding sub-questions: {e}")
        continue
        
    terminal_nouns = ["talk", "conversation", "speech", "message", "announcement", "advertisement", "report", "broadcast", "introduction"]
    def is_header_end(line):
        line = line.strip()
        if line.endswith("."):
            return True
        words = re.findall(r"\b\w+\b", line.lower())
        if words and words[-1] in terminal_nouns:
            return True
        return False

    header_len = 1
    if len(p_lines) > 1 and not is_header_end(p_lines[0]):
        header_len = 2

    trans_vocab_lines = p_lines[header_len:idx_q1]
    eng_trans, chi_trans, vocab = split_transcript_vocab(trans_vocab_lines)
    
    print(f"Passage Q{q_start}-{q_start+2}:")
    print(f"  English transcript lines: {len(eng_trans)}")
    print(f"  Chinese translation lines: {len(chi_trans)}")
    print(f"  Vocabulary lines: {len(vocab)}")
    if eng_trans:
        print(f"    First eng: {eng_trans[0]!r}")
    if chi_trans:
        print(f"    First chi: {chi_trans[0]!r}")
    if vocab:
        print(f"    First vocab: {vocab[0]!r}")
