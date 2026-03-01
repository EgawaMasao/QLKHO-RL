import json

with open(r'c:\Study\NCKH\QLKHO-RL\ablation_study.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find cell containing line 2634
for i, cell in enumerate(nb['cells']):
    start = cell.get('startLineNumber', 0)
    end = cell.get('endLineNumber', 0)
    if start <= 2634 <= end:
        print(f"Cell {i} contains line 2634 (lines {start}-{end})")
        if cell['cell_type'] == 'code':
            print("Code:")
            print(''.join(cell['source']))
        break
