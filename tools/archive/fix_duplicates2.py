import re
from collections import defaultdict

with open('js/kanji-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Split into header + array body
# Each kanji entry is exactly one line (confirmed earlier)
lines = content.split('\n')

header = []
entry_lines = []
footer = []
in_array = False

for line in lines:
    stripped = line.strip()
    if stripped.startswith('{kanji:'):
        in_array = True
        entry_lines.append(line)
    elif in_array and stripped in ('];', ']'):
        footer.append(line)
        in_array = False
    elif not in_array and not entry_lines:
        header.append(line)
    elif not in_array:
        footer.append(line)
    else:
        # lines between entries (shouldn't be any but just in case)
        entry_lines.append(line)

print(f'Header lines: {len(header)}')
print(f'Entry lines: {len(entry_lines)}')
print(f'Footer lines: {len(footer)}')

# Level priority: N5=0, N4=1, N3=2, N2=3, N1=4
level_order = {'N5': 0, 'N4': 1, 'N3': 2, 'N2': 3, 'N1': 4}

# Parse each entry line to get kanji and level
kanji_re = re.compile(r'kanji:"([^"]+)"')
level_re = re.compile(r'level:"([^"]+)"')

# Group by kanji
kanji_groups = defaultdict(list)  # kanji -> [(priority, line)]
for line in entry_lines:
    km = kanji_re.search(line)
    lm = level_re.search(line)
    if km and lm:
        k = km.group(1)
        lv = lm.group(1)
        pri = level_order.get(lv, 99)
        kanji_groups[k].append((pri, lv, line))

# Deduplicate: keep the lowest level (best JLPT)
kept_lines = []
removed = 0
for k, items in kanji_groups.items():
    items.sort(key=lambda x: x[0])
    kept_lines.append(items[0][2])
    if len(items) > 1:
        removed += len(items) - 1
        for item in items[1:]:
            pass  # silently remove

print(f'Original: {len(entry_lines)}, Kept: {len(kept_lines)}, Removed: {removed}')

# Rebuild file
# Entries need trailing comma except last
new_entries = []
for i, line in enumerate(kept_lines):
    # Normalize: ensure line ends with }],
    stripped = line.rstrip()
    if stripped.endswith(']},'):
        new_entries.append(stripped)
    elif stripped.endswith(']}'):
        new_entries.append(stripped + ',')
    else:
        new_entries.append(stripped)

new_content = '\n'.join(header) + '\n' + '\n'.join(new_entries) + '\n' + '\n'.join(footer)

with open('js/kanji-data.js', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Done! Verifying...')

# Verify
with open('js/kanji-data.js', 'r', encoding='utf-8') as f:
    verify = f.read()
open_b = verify.count('[')
close_b = verify.count(']')
print(f'Brackets balanced: [ {open_b} == ] {close_b}: {open_b == close_b}')
entry_count = len(re.findall(r'\{kanji:"', verify))
print(f'Entry count: {entry_count}')
