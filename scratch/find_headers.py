import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TOEIC_精读解析包/01_听力1000题逐题解析索引.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Find all lines matching Questions \d+ through \d+
matches = re.findall(r"Questions \d+ through \d+[^\n]+", content)
print(f"Total question headers found: {len(matches)}")
# Print first 20 headers and their frequencies or unique forms
unique_headers = set(matches)
print(f"Unique header count: {len(unique_headers)}")
for h in sorted(list(unique_headers))[:20]:
    print(f"  {h}")
