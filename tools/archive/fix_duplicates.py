import re

with open('js/kanji-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the JS array content
arr_match = re.search(r'(const ALL_KANJI\s*=\s*\[)([\s\S]+?)(\];)', content)
prefix = arr_match.group(1)
arr_body = arr_match.group(2)
suffix = arr_match.group(3)

# Parse individual entries - each entry is {...}
entry_re = re.compile(r'\{kanji:"[^"]+",[\s\S]*?\}(?=\s*,|\s*\])')
entries = entry_re.findall(arr_body)
print(f'Parsed entries: {len(entries)}')

level_order = {'N5': 0, 'N4': 1, 'N3': 2, 'N2': 3, 'N1': 4}

from collections import defaultdict
kanji_entries = defaultdict(list)
for e in entries:
    k_m = re.search(r'kanji:"([^"]+)"', e)
    l_m = re.search(r'level:"([^"]+)"', e)
    if k_m and l_m:
        kanji_entries[k_m.group(1)].append((level_order.get(l_m.group(1), 99), l_m.group(1), e))

kept = []
removed = 0
for k, items in kanji_entries.items():
    if len(items) == 1:
        kept.append(items[0][2])
    else:
        # Sort by level (keep lowest = best JLPT level)
        items.sort(key=lambda x: x[0])
        kept.append(items[0][2])
        removed += len(items) - 1
        # Show what's removed
        for item in items[1:]:
            print(f'  REMOVE {k} ({item[1]}), KEEP {items[0][1]}')

print(f'\nKept: {len(kept)}, Removed: {removed}')

# Rebuild the JS file
new_arr = ',\n  '.join(kept)
new_content = content[:arr_match.start()] + prefix + '\n  ' + new_arr + '\n' + suffix + content[arr_match.end():]

with open('js/kanji-data.js', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Done!')
