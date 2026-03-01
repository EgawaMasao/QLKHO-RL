import json

with open(r'c:\Study\NCKH\QLKHO-RL\ablation_study.ipynb', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')
    
# Extract lines 2633-2660 (0-indexed: 2632-2659)
print("=" * 80)
print("EXTRACTED JSON LINES (2633-2660):")
print("=" * 80)
for i in range(2632, min(2661, len(lines))):
    # Print full line without truncation
    line = lines[i]
    print(line)
