import os

files = [
    'routes/presentation_rewriter.py',
    'routes/question_generator.py',
    'phase_two.py',
    'phase_four.py',
    'auth.py',
    'phase_live.py'
]

results = []

for filepath in files:
    results.append(f"\n=======================================================\nFILE: {filepath}\n=======================================================")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'return jsonify(' in line or '_error(' in line:
            # Capture the full block until status code or semicolon/paren match
            block_lines = []
            j = i
            open_parens = 0
            while j < len(lines):
                cur = lines[j]
                block_lines.append(cur)
                open_parens += cur.count('(') - cur.count(')')
                if open_parens <= 0 and j > i:
                    break
                if j - i > 25:
                    break
                j += 1
            block = "".join(block_lines)
            
            # Check if this is an error response (has 4xx, 5xx, or error keywords)
            is_error = False
            for code in [', 400', ', 401', ', 403', ', 404', ', 413', ', 422', ', 500', ', 502']:
                if code in block:
                    is_error = True
                    break
            if 'error' in block.lower() and ('fail' in block.lower() or 'invalid' in block.lower() or 'missing' in block.lower() or 'denied' in block.lower() or 'unauthorized' in block.lower()):
                is_error = True
            if '_error(' in line and 'def _error' not in line:
                is_error = True
                
            if is_error and not ('"status": "success"' in block or "'status': 'success'" in block or '"success": True' in block or "'success': True" in block):
                results.append(f"Line {i+1}:")
                results.append(block.strip())
                results.append("-------------------------------------------------------")
            i = j
        i += 1

with open('tools/error_catalog.txt', 'w', encoding='utf-8') as out:
    out.write("\n".join(results))

print(f"Scanned {len(files)} files. Catalog written to tools/error_catalog.txt.")
