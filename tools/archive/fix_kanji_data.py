"""
Fix kanji-data.js: each data line has trailing garbage like:
  {kanji:"安",...,words:[w1,w2]}, {w:extra1}, {w:extra2}]}, ...
We keep only the first balanced JS object per data line.
"""
import re

INPUT  = r'js/kanji-data.js'
OUTPUT = r'js/kanji-data.js'

def extract_first_object(line):
    """Extract the first balanced { } object from a JS data line."""
    line = line.rstrip()
    if not line.startswith('{'):
        return line  # comment / header line — keep as-is

    depth = 0
    in_str = False
    str_char = None
    i = 0
    end = -1
    while i < len(line):
        c = line[i]
        if in_str:
            if c == chr(92):   # backslash escape
                i += 2
                continue
            if c == str_char:
                in_str = False
        else:
            if c in ('"', "'", '`'):
                in_str = True
                str_char = c
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    end = i
                    break
        i += 1

    if end == -1:
        # No balanced object found — return original (will be caught as error later)
        return line

    obj = line[:end + 1]  # the clean object
    return obj + ','       # trailing comma for array syntax


with open(INPUT, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
fixed_count  = 0
header_done  = False

for raw in lines:
    stripped = raw.strip()

    # Keep blank lines / comments / array opener / closer unchanged
    if (not stripped
            or stripped.startswith('//')
            or stripped == 'const ALL_KANJI = ['
            or stripped == '];'):
        output_lines.append(raw.rstrip('\n') + '\n')
        continue

    # Data line
    if stripped.startswith('{kanji:'):
        fixed = extract_first_object(stripped)
        if fixed.rstrip(',') != stripped.rstrip(','):
            fixed_count += 1
        output_lines.append(fixed + '\n')
    else:
        # Non-kanji line inside array (comment, level header, etc.)
        output_lines.append(raw.rstrip('\n') + '\n')

with open(OUTPUT, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(output_lines)

print(f'Done! Fixed {fixed_count} malformed lines out of {len(lines)} total lines.')
print(f'Wrote {len(output_lines)} lines to {OUTPUT}')

# Quick verify
import subprocess
import sys
result = subprocess.run([sys.executable, 'check_syntax.py'], capture_output=True, text=True)
print(result.stdout or result.stderr)
