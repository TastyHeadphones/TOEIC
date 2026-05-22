import os
import re

filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch/page_details.txt"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# We look for lines containing: Page \d+ (len=\d+): Tests: ['Test \d+'], ...
# e.g., Page 197 (len= 1238): Tests: ['Test 01'], Parts: [], Qs: Q1-Q100
matches = re.findall(r"Page\s+(\d+)\s+\(len=\s*\d+\):\s*Tests:\s*\[['\"](Test \d+)['\"]\]", text)
for page, test in matches:
    print(f"{test} starts on PDF page {page}")
