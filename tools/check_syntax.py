with open(r'js/kanji-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

depth = 0
errors = []
in_string = False
string_char = None
i = 0
line = 1
while i < len(content):
    c = content[i]
    if c == '\n':
        line += 1
    if in_string:
        if c == chr(92):  # backslash
            i += 2
            continue
        if c == string_char:
            in_string = False
    else:
        if c in ('"', "'", '`'):
            in_string = True
            string_char = c
        elif c in ('[', '{', '('):
            depth += 1
        elif c in (']', '}', ')'):
            depth -= 1
            if depth < 0:
                errors.append('Line %d: unexpected %s' % (line, repr(c)))
                depth = 0
                if len(errors) >= 3:
                    break
    i += 1

if errors:
    for e in errors:
        print('SYNTAX ERROR:', e)
    print('')
    print('=> kanji-data.js has SyntaxError - ALL_KANJI will NOT load in browser!')
else:
    print('Brackets OK. Final depth: %d' % depth)
    print('File appears syntactically valid')
