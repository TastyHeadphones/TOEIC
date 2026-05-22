import re
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
filepath = os.path.join(base_dir, "TOEIC_精读解析包", "01_听力1000题逐题解析索引.md")
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pages = re.split(r'## PDF 第 (\d+) 页', content)

# 1. Map Test Book pages to questions
def get_question_to_page_mapping():
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
    mapping = {} # (test_idx, q_num) -> page_num
    for test_idx, start_p, end_p in test_ranges:
        for p in range(start_p, end_p + 1):
            p_text = pages[p*2]
            qs = re.findall(r'(?:^|\n|\s)(\d+)\.', p_text)
            for q_str in qs:
                try:
                    q = int(q_str)
                    if 1 <= q <= 100:
                        if (test_idx, q) not in mapping:
                            mapping[(test_idx, q)] = p
                except ValueError:
                    pass
    return mapping

q_to_page = get_question_to_page_mapping()

# Cleaners
def clean_english_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\(\s*(\d+)\s*\)', r'(\1)', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def clean_chinese_text(text):
    if not text:
        return ""
    text = text.replace(',', '，').replace(';', '；').replace('?', '？').replace('!', '！')
    
    # Remove spaces between Chinese characters
    pattern_chi_chi = r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])'
    while re.search(pattern_chi_chi, text):
        text = re.sub(pattern_chi_chi, r'\1\2', text)
        
    # Remove spaces between Chinese character and Chinese punctuation
    pattern_chi_punc = r'([\u4e00-\u9fff])\s+([\u3000-\u303f\uff00-\uffef])'
    while re.search(pattern_chi_punc, text):
        text = re.sub(pattern_chi_punc, r'\1\2', text)
    pattern_punc_chi = r'([\u3000-\u303f\uff00-\uffef])\s+([\u4e00-\u9fff])'
    while re.search(pattern_punc_chi, text):
        text = re.sub(pattern_punc_chi, r'\1\2', text)
        
    # Remove spaces between Chinese punctuation and Chinese punctuation
    pattern_punc_punc = r'([\u3000-\u303f\uff00-\uffef])\s+([\u3000-\u303f\uff00-\uffef])'
    while re.search(pattern_punc_punc, text):
        text = re.sub(pattern_punc_punc, r'\1\2', text)
        
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_bilingual_option(letter, eng, chi):
    eng_clean = clean_english_text(eng)
    chi_clean = clean_chinese_text(chi)
    if eng_clean and chi_clean:
        return f"- ({letter}) {eng_clean} ({chi_clean})"
    elif eng_clean:
        return f"- ({letter}) {eng_clean}"
    else:
        return f"- ({letter}) {chi_clean}"

def format_bilingual_option_part2(letter, eng, chi):
    eng_clean = clean_english_text(eng)
    chi_clean = clean_chinese_text(chi)
    if eng_clean and chi_clean:
        return f"  - ({letter}) {eng_clean} ({chi_clean})"
    elif eng_clean:
        return f"  - ({letter}) {eng_clean}"
    else:
        return f"  - ({letter}) {chi_clean}"

# Dialogue Merging
def merge_english_dialogue(lines):
    preprocessed = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line == "（" and i + 2 < len(lines) and lines[i+2].strip() == "）" and lines[i+1].strip().isdigit():
            preprocessed.append(f"({lines[i+1].strip()})")
            i += 3
        elif line == "(" and i + 2 < len(lines) and lines[i+2].strip() == ")" and lines[i+1].strip().isdigit():
            preprocessed.append(f"({lines[i+1].strip()})")
            i += 3
        else:
            preprocessed.append(line)
            i += 1

    speaker_blocks = []
    current_speaker = None
    current_text = []
    
    for line in preprocessed:
        match_speaker = re.match(r"^(W\d?|M\d?|Woman\d?|Man\d?|Woman\s*\d|Man\s*\d)[:：]?$", line, re.IGNORECASE)
        if match_speaker:
            if current_speaker or current_text:
                speaker_blocks.append((current_speaker, " ".join(current_text)))
            current_speaker = match_speaker.group(1).upper()
            current_text = []
        else:
            match_inline = re.match(r"^(W\d?|M\d?|Woman\d?|Man\d?|Woman\s*\d|Man\s*\d)[:：]\s*(.*)$", line, re.IGNORECASE)
            if match_inline:
                if current_speaker or current_text:
                    speaker_blocks.append((current_speaker, " ".join(current_text)))
                current_speaker = match_inline.group(1).upper()
                current_text = [match_inline.group(2)]
            else:
                if (line.startswith(":") or line.startswith("：")) and not (line.startswith("::") or line.startswith("：：")):
                    line = line[1:].strip()
                current_text.append(line)
                
    if current_speaker or current_text:
        speaker_blocks.append((current_speaker, " ".join(current_text)))
        
    output_lines = []
    for spk, text in speaker_blocks:
        text_clean = clean_english_text(text)
        if spk:
            output_lines.append(f"**{spk}:** {text_clean}")
        else:
            output_lines.append(text_clean)
    return output_lines

def merge_chinese_dialogue(lines):
    preprocessed = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line == "（" and i + 2 < len(lines) and lines[i+2].strip() == "）" and lines[i+1].strip().isdigit():
            preprocessed.append(f"({lines[i+1].strip()})")
            i += 3
        elif line == "(" and i + 2 < len(lines) and lines[i+2].strip() == ")" and lines[i+1].strip().isdigit():
            preprocessed.append(f"({lines[i+1].strip()})")
            i += 3
        else:
            preprocessed.append(line)
            i += 1

    speaker_blocks = []
    current_speaker = None
    current_text = []
    
    for line in preprocessed:
        match_speaker = re.match(r"^(W\d?|M\d?|Woman\d?|Man\d?|Woman\s*\d|Man\s*\d)[:：]?$", line, re.IGNORECASE)
        if match_speaker:
            if current_speaker or current_text:
                speaker_blocks.append((current_speaker, "".join(current_text)))
            current_speaker = match_speaker.group(1).upper()
            current_text = []
        else:
            match_inline = re.match(r"^(W\d?|M\d?|Woman\d?|Man\d?|Woman\s*\d|Man\s*\d)[:：]\s*(.*)$", line, re.IGNORECASE)
            if match_inline:
                if current_speaker or current_text:
                    speaker_blocks.append((current_speaker, "".join(current_text)))
                current_speaker = match_inline.group(1).upper()
                current_text = [match_inline.group(2)]
            else:
                if (line.startswith(":") or line.startswith("：")) and not (line.startswith("::") or line.startswith("：：")):
                    line = line[1:].strip()
                current_text.append(line)
                
    if current_speaker or current_text:
        speaker_blocks.append((current_speaker, "".join(current_text)))
        
    output_lines = []
    for spk, text in speaker_blocks:
        text_clean = clean_chinese_text(text)
        if spk:
            output_lines.append(f"**{spk}：**{text_clean}")
        else:
            output_lines.append(text_clean)
    return output_lines

# 2. Options parser for Part 1
def parse_part1_options(lines):
    eng_opts = {}
    chi_opts = {}
    alt_exprs = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # Match English/Chinese option start
        if line == "（" and i + 2 < len(lines) and lines[i+2].strip().startswith("）"):
            opt_letter = lines[i+1].strip()
            closing_line = lines[i+2].strip()
            first_text_chunk = closing_line[1:].strip()
            
            opt_text_lines = []
            if first_text_chunk:
                opt_text_lines.append(first_text_chunk)
                
            j = i + 3
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line == "（" or next_line.startswith("·") or re.match(r"^[（(][A-D][）)]", next_line):
                    break
                opt_text_lines.append(next_line)
                j += 1
            opt_text = " ".join(opt_text_lines).strip()
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in opt_text)
            if has_chinese:
                chi_opts[opt_letter] = opt_text
            else:
                eng_opts[opt_letter] = opt_text
            i = j
            continue
            
        # Match "（A）选项文字"
        match = re.match(r"^[（(]([A-D])[）)](.*)", line)
        if match:
            opt_letter = match.group(1)
            opt_text = match.group(2).strip()
            opt_text_lines = [opt_text]
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line == "（" or next_line.startswith("·") or re.match(r"^[（(][A-D][）)]", next_line):
                    break
                opt_text_lines.append(next_line)
                j += 1
            opt_text_full = " ".join(opt_text_lines).strip()
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in opt_text_full)
            if has_chinese:
                chi_opts[opt_letter] = opt_text_full
            else:
                eng_opts[opt_letter] = opt_text_full
            i = j
            continue
            
        if line.startswith("·"):
            alt_exprs.append(line)
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith("·") or next_line == "（" or re.match(r"^[（(][A-D][）)]", next_line):
                    break
                alt_exprs.append(next_line)
                j += 1
            i = j
            continue
            
        i += 1
    return eng_opts, chi_opts, alt_exprs

# 3. Options parser for Part 2
def parse_part2_question(lines):
    eng_q = ""
    eng_opts = {}
    chi_q = ""
    chi_opts = {}
    script_qa = []
    
    lines = [l.strip() for l in lines if l.strip()]
    if not lines:
        return eng_q, eng_opts, chi_q, chi_opts, script_qa
        
    start_idx = 0
    if lines[0].isdigit():
        start_idx = 1
        
    i = start_idx
    eng_q_lines = []
    while i < len(lines):
        line = lines[i]
        if line == "（" or re.match(r"^[（(][A-C][）)]", line):
            break
        eng_q_lines.append(line)
        i += 1
    eng_q = " ".join(eng_q_lines).strip()
    
    # English options
    while i < len(lines):
        line = lines[i]
        if line == "（":
            if i + 2 < len(lines) and lines[i+2].startswith("）"):
                letter = lines[i+1]
                first_chunk = lines[i+2][1:].strip()
                opt_lines = []
                if first_chunk:
                    opt_lines.append(first_chunk)
                j = i + 3
                while j < len(lines):
                    next_line = lines[j]
                    if next_line == "（" or next_line.startswith("（A）") or next_line.startswith("（B）") or next_line.startswith("（C）") or any('\u4e00' <= char <= '\u9fff' for char in next_line):
                        break
                    opt_lines.append(next_line)
                    j += 1
                eng_opts[letter] = " ".join(opt_lines).strip()
                i = j
                continue
        match = re.match(r"^[（(]([A-C])[）)](.*)", line)
        if match:
            letter = match.group(1)
            eng_opts[letter] = match.group(2).strip()
            i += 1
            continue
        break
        
    # Chinese question translation
    chi_q_lines = []
    while i < len(lines):
        line = lines[i]
        if line == "（" or re.match(r"^[（(][A-C][）)]", line) or line.startswith("Q ") or line.startswith("Q:") or line.startswith("Q："):
            break
        chi_q_lines.append(line)
        i += 1
    chi_q = " ".join(chi_q_lines).strip()
    
    # Chinese options
    while i < len(lines):
        line = lines[i]
        if line == "（":
            if i + 2 < len(lines) and lines[i+2].startswith("）"):
                letter = lines[i+1]
                first_chunk = lines[i+2][1:].strip()
                opt_lines = []
                if first_chunk:
                    opt_lines.append(first_chunk)
                j = i + 3
                while j < len(lines):
                    next_line = lines[j]
                    if next_line == "（" or next_line.startswith("Q ") or next_line.startswith("Q:") or next_line.startswith("Q：") or next_line.startswith("（A）") or next_line.startswith("（B）") or next_line.startswith("（C）"):
                        break
                    opt_lines.append(next_line)
                    j += 1
                chi_opts[letter] = " ".join(opt_lines).strip()
                i = j
                continue
        match = re.match(r"^[（(]([A-C])[）)](.*)", line)
        if match:
            letter = match.group(1)
            chi_opts[letter] = match.group(2).strip()
            i += 1
            continue
        break
        
    while i < len(lines):
        script_qa.append(lines[i])
        i += 1
        
    return eng_q, eng_opts, chi_q, chi_opts, script_qa

# Script QA parsing for Part 2
def parse_part2_script_qa(lines):
    eng_q_lines = []
    eng_a_lines = []
    chi_q_lines = []
    chi_a_lines = []
    
    state = "eng_q"
    has_separator = False
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        if re.match(r'^[-—–_]+$', line_clean):
            has_separator = True
            state = "chi_a"
            continue
            
        if line_clean.startswith("Q ") or line_clean.startswith("Q:") or line_clean.startswith("Q："):
            state = "eng_q"
            line_clean = re.sub(r'^Q[:：\s]+', '', line_clean).strip()
        elif line_clean.startswith("A ") or line_clean.startswith("A:") or line_clean.startswith("A："):
            state = "eng_a"
            line_clean = re.sub(r'^A[:：\s]+', '', line_clean).strip()
        elif any('\u4e00' <= char <= '\u9fff' for char in line_clean):
            if state in ["eng_q", "eng_a"]:
                state = "chi_q"
                
        if state == "eng_q":
            eng_q_lines.append(line_clean)
        elif state == "eng_a":
            eng_a_lines.append(line_clean)
        elif state == "chi_q":
            chi_q_lines.append(line_clean)
        elif state == "chi_a":
            chi_a_lines.append(line_clean)
            
    eng_q = " ".join(eng_q_lines).strip()
    eng_a = " ".join(eng_a_lines).strip()
    
    if not has_separator and len(chi_q_lines) > 1 and not chi_a_lines:
        mid = len(chi_q_lines) // 2
        chi_a_lines = chi_q_lines[mid:]
        chi_q_lines = chi_q_lines[:mid]
        
    chi_q = "".join(chi_q_lines).strip()
    chi_a = "".join(chi_a_lines).strip()
    
    eng_q = clean_english_text(eng_q)
    eng_a = clean_english_text(eng_a)
    chi_q = clean_chinese_text(chi_q)
    chi_a = clean_chinese_text(chi_a)
    
    return eng_q, eng_a, chi_q, chi_a

# 4. Reconstruct options parser for sub-questions (Part 3/4)
def parse_sub_question(q_lines):
    q_lines = [l.strip() for l in q_lines if l.strip()]
    if not q_lines:
        return "", {}, "", {}
        
    eng_q_lines = []
    i = 0
    while i < len(q_lines):
        line = q_lines[i]
        if line == "（" or re.match(r"^[（(][A-D][）)]", line):
            break
        eng_q_lines.append(line)
        i += 1
    eng_q = " ".join(eng_q_lines).strip()
    
    eng_opts = {}
    while i < len(q_lines):
        line = q_lines[i]
        if line == "（":
            if i + 2 < len(q_lines) and q_lines[i+2].startswith("）"):
                letter = q_lines[i+1]
                first_chunk = q_lines[i+2][1:].strip()
                opt_lines = []
                if first_chunk:
                    opt_lines.append(first_chunk)
                j = i + 3
                while j < len(q_lines):
                    next_line = q_lines[j]
                    if next_line == "（" or next_line.startswith("（A）") or next_line.startswith("（B）") or next_line.startswith("（C）") or next_line.startswith("（D）") or any('\u4e00' <= char <= '\u9fff' for char in next_line):
                        break
                    opt_lines.append(next_line)
                    j += 1
                eng_opts[letter] = " ".join(opt_lines).strip()
                i = j
                continue
        match = re.match(r"^[（(][A-D][）)](.*)", line)
        if match:
            letter = match.group(1)
            eng_opts[letter] = match.group(2).strip()
            i += 1
            continue
        break
        
    chi_q_lines = []
    while i < len(q_lines):
        line = q_lines[i]
        if line == "（" or re.match(r"^[（(][A-D][）)]", line):
            break
        chi_q_lines.append(line)
        i += 1
    chi_q = " ".join(chi_q_lines).strip()
    
    chi_opts = {}
    while i < len(q_lines):
        line = q_lines[i]
        if line == "（":
            if i + 2 < len(q_lines) and q_lines[i+2].startswith("）"):
                letter = q_lines[i+1]
                first_chunk = q_lines[i+2][1:].strip()
                opt_lines = []
                if first_chunk:
                    opt_lines.append(first_chunk)
                j = i + 3
                while j < len(q_lines):
                    next_line = q_lines[j]
                    if next_line == "（":
                        break
                    opt_lines.append(next_line)
                    j += 1
                chi_opts[letter] = " ".join(opt_lines).strip()
                i = j
                continue
        match = re.match(r"^[（(][A-D][）)](.*)", line)
        if match:
            letter = match.group(1)
            chi_opts[letter] = match.group(2).strip()
            i += 1
            continue
        break
        
    return eng_q, eng_opts, chi_q, chi_opts

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
    if not re.search(r'[a-zA-Z]', line):
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

# Alternative expressions
def parse_alternative_expressions(lines):
    pairs = []
    current_eng = ""
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        line_clean = re.sub(r'^[·\-–—…\.\s~]+', '', line_clean)
        
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in line_clean)
        if has_chinese:
            if current_eng:
                pairs.append((current_eng, line_clean))
                current_eng = ""
            else:
                pairs.append(("", line_clean))
        else:
            if current_eng:
                pairs.append((current_eng, ""))
            current_eng = line_clean
            
    if current_eng:
        pairs.append((current_eng, ""))
        
    cleaned_pairs = []
    for eng, chi in pairs:
        cleaned_pairs.append((clean_english_text(eng), clean_chinese_text(chi)))
    return cleaned_pairs

def format_alternative_expressions_part34(alt_lines):
    chunks = []
    current_chunk = []
    for line in alt_lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        if line_clean.startswith("·"):
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = [line_clean[1:].strip()]
        else:
            if current_chunk:
                current_chunk.append(line_clean)
            else:
                current_chunk = [line_clean]
    if current_chunk:
        chunks.append(current_chunk)
        
    formatted_lines = []
    for chunk in chunks:
        groups = []
        for line in chunk:
            has_eng = bool(re.search(r'[a-zA-Z]', line))
            has_chi = bool(re.search(r'[\u4e00-\u9fff]', line))
            
            if has_eng:
                line_type = "Eng"
            elif has_chi:
                line_type = "Chi"
            else:
                line_type = "Neutral"
                
            if line_type == "Neutral":
                if groups:
                    groups[-1][1].append(line)
                else:
                    groups.append(["Eng", [line]])
            else:
                if groups and groups[-1][0] == line_type:
                    groups[-1][1].append(line)
                else:
                    groups.append([line_type, [line]])
                    
        eng_templates = []
        chi_templates = []
        eng_examples = []
        chi_examples = []
        
        eng_count = 0
        chi_count = 0
        for g_type, g_lines in groups:
            if g_type == "Eng":
                eng_count += 1
                if eng_count == 1:
                    eng_templates = g_lines
                else:
                    eng_examples.extend(g_lines)
            elif g_type == "Chi":
                chi_count += 1
                if chi_count == 1:
                    chi_templates = g_lines
                else:
                    chi_examples.extend(g_lines)
                    
        template_eng = clean_english_text(" ".join(eng_templates))
        template_chi = clean_chinese_text("".join(chi_templates))
        example_eng = clean_english_text(" ".join(eng_examples))
        example_chi = clean_chinese_text("".join(chi_examples))
        
        if template_eng:
            template_eng = re.sub(r'\s*=\s*', ' = ', template_eng)
            out_str = f"- **{template_eng}**"
            if template_chi:
                out_str += f" ({template_chi})"
            formatted_lines.append(out_str)
            
        if example_eng:
            example_str = f"  - *例句：{example_eng}*"
            if example_chi:
                example_str += f" ({example_chi})"
            formatted_lines.append(example_str)
            
    return formatted_lines

# Vocabulary
def clean_english_term(parts):
    term = " ".join(parts).strip()
    term = re.sub(r'^[·\-–—…\.\s~]+', '', term)
    term = re.sub(r'[·\-–—…\.\s]+$', '', term)
    term = re.sub(r'\s+', ' ', term)
    return clean_english_text(term)

def clean_join_chinese(parts):
    text = "".join(parts).strip()
    return clean_chinese_text(text)

def parse_vocabulary_list(lines):
    pairs = []
    eng_buf = []
    chi_buf = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if "核心词汇" in line or "频率高" in line:
            continue
            
        has_eng = bool(re.search(r'[a-zA-Z]', line))
        has_chi = bool(re.search(r'[\u4e00-\u9fff]', line))
        
        if has_eng and has_chi:
            match = re.search(r'[\u4e00-\u9fff]', line)
            idx = match.start()
            eng_part = line[:idx].strip()
            chi_part = line[idx:].strip()
            
            if eng_buf and chi_buf:
                pairs.append((clean_english_term(eng_buf), clean_join_chinese(chi_buf)))
                eng_buf, chi_buf = [], []
                
            if eng_part:
                eng_buf.append(eng_part)
            if chi_part:
                chi_buf.append(chi_part)
        elif has_chi:
            chi_buf.append(line)
        elif has_eng:
            if chi_buf:
                pairs.append((clean_english_term(eng_buf), clean_join_chinese(chi_buf)))
                eng_buf, chi_buf = [], []
            eng_buf.append(line)
        else:
            if chi_buf:
                if line in ["，", ",", "；", ";"]:
                    chi_buf.append(line)
            elif eng_buf:
                if line in ["~", "...", "…"]:
                    eng_buf.append(line)
                    
    if eng_buf and chi_buf:
        pairs.append((clean_english_term(eng_buf), clean_join_chinese(chi_buf)))
        
    return pairs

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

# Fallback mapping for Part 1 photos
part1_page_fallback = {
    1: {1: 25, 2: 25, 3: 26, 4: 26, 5: 26, 6: 27},
    2: {1: 43, 2: 43, 3: 43, 4: 44, 5: 44, 6: 45},
    3: {1: 61, 2: 61, 3: 61, 4: 62, 5: 62, 6: 62},
    4: {1: 78, 2: 78, 3: 78, 4: 79, 5: 79, 6: 79},
    5: {1: 95, 2: 95, 3: 95, 4: 96, 5: 96, 6: 97},
    6: {1: 112, 2: 112, 3: 112, 4: 113, 5: 113, 6: 113},
    7: {1: 129, 2: 129, 3: 129, 4: 130, 5: 130, 6: 130},
    8: {1: 146, 2: 146, 3: 146, 4: 147, 5: 147, 6: 147},
    9: {1: 164, 2: 164, 3: 164, 4: 165, 5: 165, 6: 165},
    10: {1: 181, 2: 181, 3: 181, 4: 182, 5: 182, 6: 182}
}

def parse_answer_keys(test_lines, key_end_idx):
    answers = {}
    i = 0
    while i < key_end_idx:
        line = test_lines[i]
        if line.endswith("."):
            try:
                q = int(line[:-1])
                ans = None
                for j in range(i+1, min(i+10, key_end_idx)):
                    if test_lines[j] == "（":
                        if j + 2 < key_end_idx and test_lines[j+2].startswith("）"):
                            ans = test_lines[j+1]
                            break
                if ans:
                    answers[q] = ans
            except ValueError:
                pass
        i += 1
    return answers

output_md = []
output_md.append("# 听力 1000 题逐题解析索引（全十套完整版）\n")
output_md.append("本索引将所有听力题目按 Test 01 ~ Test 10、每套题按 Q1 ~ Q100 重新排版整理。去除了原 PDF 繁杂的页码标题，合并了题目、选项、中译、原文及解析，并对图画/图表题直接嵌入了对应的图片，以提供极佳的阅读和刷题体验。\n")

for test_idx in range(1, 11):
    print(f"Parsing Test {test_idx:02d}...")
    start_pages = [197, 256, 312, 369, 425, 481, 537, 593, 650, 706, 762]
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
                if test_lines[j].startswith("）"):
                    key_end_idx = j + 1
                    break
            if key_end_idx > 0:
                break
                
    answers = parse_answer_keys(test_lines, key_end_idx)
    explanation_lines = test_lines[key_end_idx:]
    
    current_idx = 0
    q_indices = {}
    for q in range(1, 33):
        target = str(q)
        for idx in range(current_idx, len(explanation_lines)):
            if explanation_lines[idx] == target:
                q_indices[q] = idx
                current_idx = idx + 1
                break
                
    output_md.append(f"\n# TEST {test_idx:02d}\n")
    
    # Generate Answer Key Table (20 columns fixed)
    output_md.append("## 答案速查表\n")
    output_md.append("| 题号 | 答案 | 题号 | 答案 | 题号 | 答案 | 题号 | 答案 | 题号 | 答案 | 题号 | 答案 | 题号 | 答案 | 题号 | 答案 | 题号 | 答案 | 题号 | 答案 |")
    output_md.append("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for row in range(10):
        row_str = "|"
        for col in range(5):
            q_num = row + 1 + col * 20
            ans = answers.get(q_num, "-")
            row_str += f" **{q_num}** | {ans} |"
            
            q_num_next = row + 11 + col * 20
            ans_next = answers.get(q_num_next, "-")
            row_str += f" **{q_num_next}** | {ans_next} |"
        output_md.append(row_str)
    output_md.append("\n")
    
    # PART 1
    output_md.append("## Part 1: 照片描述 (Q1 - Q6)\n")
    for q in range(1, 7):
        q_lines = explanation_lines[q_indices[q] : q_indices[q+1]]
        eng_opts, chi_opts, alt_exprs = parse_part1_options(q_lines)
        ans = answers.get(q, "")
        
        output_md.append(f"### Q{q} (正确答案：{ans})\n")
        
        p_num = q_to_page.get((test_idx, q), part1_page_fallback[test_idx][q])
        output_md.append(f"![Page {p_num}](images/listen_page_{p_num}.png)\n")
        
        output_md.append("**听力原文与选项：**")
        for let in ["A", "B", "C", "D"]:
            eng = eng_opts.get(let, "")
            chi = chi_opts.get(let, "")
            output_md.append(format_bilingual_option(let, eng, chi))
            
        if alt_exprs:
            output_md.append("\n**其他可能表达：**")
            for eng, chi in parse_alternative_expressions(alt_exprs):
                if eng and chi:
                    output_md.append(f"- {eng} ({chi})")
                elif eng:
                    output_md.append(f"- {eng}")
                else:
                    output_md.append(f"- {chi}")
        output_md.append("\n")
        
    # PART 2
    output_md.append("## Part 2: 应答测试 (Q7 - Q31)\n")
    for q in range(7, 32):
        q_lines = explanation_lines[q_indices[q] : q_indices[q+1]]
        eng_q, eng_opts, chi_q, chi_opts, script_qa = parse_part2_question(q_lines)
        ans = answers.get(q, "")
        
        output_md.append(f"### Q{q} (正确答案：{ans})\n")
        
        # Script QA
        eng_q_script, eng_a_script, chi_q_script, chi_a_script = parse_part2_script_qa(script_qa)
        if eng_q_script and eng_a_script:
            output_md.append("**听力对话文本：**")
            output_md.append(f"- **Q:** {eng_q_script} ({chi_q_script})")
            output_md.append(f"- **A:** {eng_a_script} ({chi_a_script})")
            output_md.append("")
            
        output_md.append("**听力原文与选项：**")
        eng_q_clean = clean_english_text(eng_q)
        chi_q_clean = clean_chinese_text(chi_q)
        output_md.append(f"- **问题：** {eng_q_clean} ({chi_q_clean})")
        output_md.append("- **选项：**")
        for let in ["A", "B", "C"]:
            eng = eng_opts.get(let, "")
            chi = chi_opts.get(let, "")
            output_md.append(format_bilingual_option_part2(let, eng, chi))
        output_md.append("\n")
        
    # PART 3 & PART 4
    passage_headers = []
    for idx, line in enumerate(explanation_lines):
        if re.match(r"^Questions\s+\d+\s+through\s+\d+\s+refer\s+to\s+the\s+following", line, re.IGNORECASE):
            passage_headers.append((line, idx))
            
    print(f"  Found {len(passage_headers)} passage headers.")
    
    for p_idx in range(23):
        start_line_idx = passage_headers[p_idx][1]
        end_line_idx = passage_headers[p_idx+1][1] if p_idx < 22 else len(explanation_lines)
        
        p_lines = explanation_lines[start_line_idx:end_line_idx]
        header_text = p_lines[0]
        
        match_qs = re.search(r"Questions\s+(\d+)\s+through\s+(\d+)", header_text, re.IGNORECASE)
        if not match_qs:
            continue
        q_start = int(match_qs.group(1))
        q_end = int(match_qs.group(2))
        
        if q_start == 71:
            output_md.append("## Part 4: 简短独白 (Q71 - Q100)\n")
        elif q_start == 32:
            output_md.append("## Part 3: 简短对话 (Q32 - Q70)\n")
            
        output_md.append(f"### Questions {q_start} - {q_end}\n")
        
        try:
            idx_q1 = find_real_question_index(p_lines, q_start, 0)
            idx_q2 = find_real_question_index(p_lines, q_start + 1, idx_q1 + 1)
            idx_q3 = find_real_question_index(p_lines, q_start + 2, idx_q2 + 1)
        except ValueError:
            print(f"  Warning: failed to find sub-question numbers sequentially for Q{q_start}-{q_end}")
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
        q1_lines = p_lines[idx_q1 + 1 : idx_q2]
        q2_lines = p_lines[idx_q2 + 1 : idx_q3]
        
        q3_raw_lines = p_lines[idx_q3 + 1 :]
        q3_lines = []
        alt_lines = []
        for line in q3_raw_lines:
            if line.startswith("·") or alt_lines:
                alt_lines.append(line)
            else:
                q3_lines.append(line)
                
        eng_trans, chi_trans, vocab = split_transcript_vocab(trans_vocab_lines)
        
        merged_eng = merge_english_dialogue(eng_trans)
        merged_chi = merge_chinese_dialogue(chi_trans)
        vocab_pairs = parse_vocabulary_list(vocab)
        formatted_alts = format_alternative_expressions_part34(alt_lines)
        
        q1_eng_q, q1_eng_opts, q1_chi_q, q1_chi_opts = parse_sub_question(q1_lines)
        q2_eng_q, q2_eng_opts, q2_chi_q, q2_chi_opts = parse_sub_question(q2_lines)
        q3_eng_q, q3_eng_opts, q3_chi_q, q3_chi_opts = parse_sub_question(q3_lines)
        
        is_graphic = False
        graphic_q_num = None
        for q_num, q_text in [(q_start, q1_eng_q), (q_start+1, q2_eng_q), (q_start+2, q3_eng_q)]:
            if "graphic" in q_text.lower() or "chart" in q_text.lower() or "map" in q_text.lower() or "diagram" in q_text.lower() or "schedule" in q_text.lower() or "list" in q_text.lower():
                is_graphic = True
                graphic_q_num = q_num
                break
                
        if is_graphic:
            p_num = q_to_page.get((test_idx, graphic_q_num))
            if p_num:
                output_md.append(f"![Page {p_num}](images/listen_page_{p_num}.png)\n")
            else:
                print(f"  Warning: could not find Test Book page for graphic question Q{graphic_q_num}")
                
        if merged_eng:
            output_md.append("**听力独白/对话原文：**")
            for line in merged_eng:
                output_md.append(line)
            output_md.append("")
            
        if merged_chi:
            output_md.append("**中文对照：**")
            for line in merged_chi:
                output_md.append(f"> {line}")
            output_md.append("")
            
        if vocab_pairs:
            output_md.append("**核心词汇与短语：**")
            for eng, chi in vocab_pairs:
                if eng and chi:
                    output_md.append(f"- **{eng}**：{chi}")
            output_md.append("")
            
        for q_num, eng_q, eng_opts, chi_q, chi_opts in [
            (q_start, q1_eng_q, q1_eng_opts, q1_chi_q, q1_chi_opts),
            (q_start+1, q2_eng_q, q2_eng_opts, q2_chi_q, q2_chi_opts),
            (q_start+2, q3_eng_q, q3_eng_opts, q3_chi_q, q3_chi_opts)
        ]:
            ans = answers.get(q_num, "")
            output_md.append(f"#### Q{q_num} (正确答案：{ans})")
            eng_q_clean = clean_english_text(eng_q)
            chi_q_clean = clean_chinese_text(chi_q)
            output_md.append(f"**问题：** {eng_q_clean} ({chi_q_clean})")
            for let in ["A", "B", "C", "D"]:
                eng = eng_opts.get(let, "")
                chi = chi_opts.get(let, "")
                output_md.append(format_bilingual_option(let, eng, chi))
            output_md.append("")
            
        if formatted_alts:
            output_md.append("**延伸表达与补充：**")
            for line in formatted_alts:
                output_md.append(line)
            output_md.append("")

output_file = os.path.join(base_dir, "TOEIC_精读解析包", "01_听力1000题逐题解析索引.md")
markdown_content = "\n".join(output_md)
with open(output_file, "w", encoding="utf-8") as out:
    out.write(markdown_content)
print("Successfully wrote premium index to TOEIC_精读解析包/01_听力1000题逐题解析索引.md")

brain_dir = os.path.expanduser("~/.gemini/antigravity-cli/brain/5bb036bd-1b69-42d3-9d01-2d58c651003c")
brain_output_file = os.path.join(brain_dir, "01_听力1000题逐题解析索引.md")
brain_content = markdown_content.replace("(images/", f"(file://{brain_dir}/images/")
with open(brain_output_file, "w", encoding="utf-8") as out:
    out.write(brain_content)
print("Successfully wrote premium index to brain directory.")
