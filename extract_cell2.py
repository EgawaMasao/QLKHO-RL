import json

with open(r'c:\Study\NCKH\QLKHO-RL\ablation_study.ipynb', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')
    
# Check line 2634 directly
if len(lines) > 2634:
    print(f"Line 2634 content: {lines[2633]}")  # 0-indexed
    print(f"\nShowing lines 2633-2660:")
    for i in range(2632, min(2660, len(lines))):
        print(f"{i+1}: {lines[i]}")
