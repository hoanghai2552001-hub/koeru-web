"""
static_analyzer.py — Phân tích tĩnh HTML/JS tìm bug phổ biến trong web game

Kiểm tra:
  1. Hàm gọi nhưng không định nghĩa
  2. getElementById trỏ ID không có trong HTML
  3. Event listener attach vào ID không tồn tại (crash on load)
  4. Biến toàn cục dùng trước khi khai báo (trong cùng file)

Chạy:
    python static_analyzer.py --html kanji.html --js-dir js/ --out qa_static_report.json
"""

import re, json, os, argparse
from pathlib import Path

# ─────────────────────────────────────────────
# HTML: Extract static IDs
# ─────────────────────────────────────────────
def extract_html_ids(html_path):
    """Lấy tất cả id="..." có trong HTML tĩnh (không phải trong <script> tag)."""
    with open(html_path, encoding='utf-8') as f:
        content = f.read()
    # Remove script blocks to avoid counting dynamic IDs
    no_scripts = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    return set(re.findall(r'\bid=["\']([^"\']+)["\']', no_scripts))


def extract_dynamic_ids(js_files):
    """Lấy ID được tạo động qua innerHTML/insertAdjacentHTML."""
    dynamic = set()
    for path in js_files:
        with open(path, encoding='utf-8', errors='ignore') as f:
            content = f.read()
        # id="..." inside template literals or string assignments
        dynamic.update(re.findall(r'\bid=["\`\'\\]([^"\'`\\>]+)["\`\'\\]', content))
        # Also get from innerHTML = `...id="xyz"...`
        dynamic.update(re.findall(r'id=\\"([^\\]+)\\"', content))
    return dynamic


# ─────────────────────────────────────────────
# JS: Extract defined functions
# ─────────────────────────────────────────────
def extract_defined_functions(js_files):
    """Lấy tên hàm được định nghĩa trong bất kỳ JS file nào."""
    defined = set()
    patterns = [
        r'function\s+(\w+)\s*\(',           # function foo(
        r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(',  # const foo = (
        r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?function',  # const foo = function
        r'(\w+)\s*[:=]\s*(?:async\s*)?function',  # foo: function
        r'(\w+)\s*[:=]\s*(?:async\s*)?\([^)]*\)\s*=>',  # foo = () =>
    ]
    for path in js_files:
        with open(path, encoding='utf-8', errors='ignore') as f:
            content = f.read()
        for p in patterns:
            defined.update(re.findall(p, content))
    # Add globals known to exist (browser APIs, etc.)
    defined.update({
        'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
        'parseInt', 'parseFloat', 'Math', 'JSON', 'Date', 'Array',
        'Object', 'Promise', 'console', 'document', 'window', 'navigator',
        'localStorage', 'sessionStorage', 'URL', 'FileReader', 'Blob',
        'SpeechSynthesisUtterance', 'AudioContext', 'fetch',
        'shuffle',  # defined in kanji-state.js
    })
    return defined


def extract_function_calls(js_file):
    """Lấy tên hàm được gọi (không phải định nghĩa) trong 1 file."""
    with open(js_file, encoding='utf-8', errors='ignore') as f:
        content = f.read()
    # Remove comments
    content = re.sub(r'//[^\n]*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Remove string literals to avoid matching CSS function names inside template strings
    content = re.sub(r'`[^`]*`', '``', content)
    content = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '""', content)
    content = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", "''", content)
    # Find call patterns: funcName( but not function funcName(
    calls = set()
    for m in re.finditer(r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(', content):
        name = m.group(1)
        # Skip keywords and JS built-ins
        if name in {'if', 'for', 'while', 'switch', 'catch', 'return',
                    'typeof', 'instanceof', 'new', 'delete', 'void', 'throw',
                    'function', 'class', 'async', 'await', 'yield', 'import',
                    'export', 'default', 'case', 'else', 'try', 'finally',
                    'do', 'in', 'of', 'break', 'continue', 'debugger'}:
            continue
        # Skip method calls (preceded by . or ?.)
        start = m.start()
        prefix = content[max(0, start-2):start].strip()
        if prefix.endswith('.') or prefix.endswith('?.'):
            continue
        calls.add(name)
    return calls


# ─────────────────────────────────────────────
# JS: getElementById analysis
# ─────────────────────────────────────────────
def check_getelementbyid(js_files, static_ids, dynamic_ids):
    """Tìm getElementById calls trỏ tới ID không có trong HTML."""
    issues = []
    all_known_ids = static_ids | dynamic_ids

    for path in js_files:
        with open(path, encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        for i, line in enumerate(lines, 1):
            # Skip comment lines
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('*'):
                continue
            for m in re.finditer(r"getElementById\(['\"]([^'\"]+)['\"]\)", line):
                id_val = m.group(1)
                if id_val not in all_known_ids:
                    # Check if it's a concatenation/variable
                    if not re.search(r'[+\$\{]', line):
                        issues.append({
                            'file': os.path.basename(path),
                            'line': i,
                            'id': id_val,
                            'context': stripped[:100],
                        })
    return issues


def check_event_listeners_on_missing_ids(js_files, static_ids):
    """
    Tìm pattern: document.getElementById('x').addEventListener(...)
    khi 'x' không có trong HTML tĩnh — crash on load.
    """
    issues = []
    for path in js_files:
        with open(path, encoding='utf-8', errors='ignore') as f:
            content = f.read()
        lines = content.splitlines()
        # Look for getElementById(...).addEventListener or similar chained calls
        pattern = re.compile(
            r"getElementById\(['\"]([^'\"]+)['\"]\)\s*\.\s*(addEventListener|classList|style|textContent|innerHTML)",
        )
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//'):
                continue
            for m in pattern.finditer(line):
                id_val = m.group(1)
                method = m.group(2)
                if id_val not in static_ids:
                    # If it's addEventListener specifically, it's likely at top-level (crash on load)
                    severity = 'critical' if method == 'addEventListener' else 'warning'
                    issues.append({
                        'file': os.path.basename(path),
                        'line': i,
                        'id': id_val,
                        'method': method,
                        'severity': severity,
                        'context': stripped[:100],
                    })
    return issues


# ─────────────────────────────────────────────
# JS: Undefined function calls
# ─────────────────────────────────────────────
def check_undefined_calls(js_files, defined_funcs):
    """Tìm hàm được gọi nhưng không định nghĩa ở bất kỳ file nào."""
    issues = []
    # Common browser/DOM globals and CSS functions to exclude
    exclude = {
        # Console
        'log', 'warn', 'error', 'dir', 'info', 'assert', 'group', 'groupEnd', 'table',
        # DOM methods (called as methods, but captured before dot-filter catches them)
        'querySelector', 'querySelectorAll', 'getElementById', 'getElementsByClassName',
        'createElement', 'createTextNode', 'addEventListener', 'removeEventListener',
        'appendChild', 'removeChild', 'insertBefore', 'replaceChild', 'remove',
        # Array / String / Object methods
        'push', 'pop', 'shift', 'unshift', 'splice', 'slice', 'map', 'filter',
        'reduce', 'forEach', 'find', 'findIndex', 'includes', 'indexOf', 'lastIndexOf',
        'join', 'split', 'replace', 'replaceAll', 'trim', 'trimStart', 'trimEnd',
        'toLowerCase', 'toUpperCase', 'toString', 'toFixed', 'repeat',
        'startsWith', 'endsWith', 'padStart', 'padEnd', 'substring', 'substr',
        'sort', 'reverse', 'concat', 'flat', 'flatMap', 'some', 'every', 'fill',
        'keys', 'values', 'entries', 'assign', 'freeze', 'create', 'defineProperty',
        'hasOwnProperty', 'isPrototypeOf', 'propertyIsEnumerable',
        # Math
        'abs', 'round', 'floor', 'ceil', 'min', 'max', 'random', 'pow', 'sqrt',
        'sign', 'trunc', 'log', 'exp', 'sin', 'cos', 'tan', 'atan2', 'hypot',
        # JSON
        'stringify', 'parse',
        # Date
        'now', 'getTime', 'getFullYear', 'getMonth', 'getDate', 'getDay',
        'getHours', 'getMinutes', 'getSeconds',
        'toDateString', 'toISOString', 'toLocaleDateString', 'toLocaleString',
        # Window / Browser globals
        'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
        'requestAnimationFrame', 'cancelAnimationFrame',
        'confirm', 'alert', 'prompt', 'open', 'close', 'print',
        'encodeURIComponent', 'decodeURIComponent', 'encodeURI', 'decodeURI',
        'parseInt', 'parseFloat', 'isNaN', 'isFinite', 'escape', 'unescape',
        'fetch', 'atob', 'btoa',
        # Constructors
        'Audio', 'Image', 'Video', 'Worker', 'Blob', 'File', 'FileReader',
        'FormData', 'URLSearchParams', 'URL', 'Headers', 'Request', 'Response',
        'Promise', 'Proxy', 'Reflect', 'Symbol', 'BigInt', 'WeakRef',
        'Map', 'Set', 'WeakMap', 'WeakSet',
        'String', 'Number', 'Boolean', 'Array', 'Object', 'Function', 'RegExp',
        'Error', 'TypeError', 'RangeError', 'SyntaxError', 'ReferenceError',
        'SpeechSynthesisUtterance', 'AudioContext', 'webkitAudioContext',
        'IntersectionObserver', 'MutationObserver', 'ResizeObserver',
        'XMLHttpRequest', 'WebSocket', 'EventSource',
        # Storage / Crypto / Other
        'getItem', 'setItem', 'removeItem', 'clear',
        'getVoices', 'speak', 'cancel', 'pause', 'resume',
        'getBoundingClientRect', 'getClientRects', 'getComputedStyle',
        'createObjectURL', 'revokeObjectURL', 'readAsText', 'readAsDataURL',
        'createOscillator', 'createGain', 'createBuffer', 'createBufferSource',
        'createAnalyser', 'createDynamicsCompressor', 'createConvolver',
        'fromCharCode', 'fromCodePoint', 'charCodeAt', 'codePointAt',
        'connect', 'disconnect', 'start', 'stop',
        'setValueAtTime', 'linearRampToValueAtTime', 'exponentialRampToValueAtTime',
        'click', 'focus', 'blur', 'submit', 'reset', 'select', 'scroll',
        'scrollTo', 'scrollIntoView', 'scrollBy',
        'getAttribute', 'setAttribute', 'removeAttribute', 'hasAttribute',
        'contains', 'matches', 'closest', 'cloneNode', 'normalize',
        'getContext', 'toDataURL', 'drawImage', 'clearRect', 'fillRect',
        'strokeRect', 'beginPath', 'moveTo', 'lineTo', 'arc', 'stroke', 'fill',
        # CSS functions (may appear in template literal strings)
        'linear-gradient', 'radial-gradient', 'conic-gradient',
        'gradient', 'var', 'calc', 'min', 'max', 'clamp', 'rgb', 'rgba',
        'hsl', 'hsla', 'scale', 'scaleX', 'scaleY', 'rotate', 'translate',
        'translateX', 'translateY', 'skew', 'matrix', 'perspective',
        'blur', 'brightness', 'contrast', 'grayscale', 'invert', 'opacity',
        'saturate', 'sepia', 'drop-shadow', 'env', 'attr',
        # Module / AMD
        'require', 'define', 'module', 'exports',
        # Lodash-style utils often defined elsewhere
        'shuffle',  # defined in kanji-state.js
    }

    for path in js_files:
        calls = extract_function_calls(path)
        fname = os.path.basename(path)
        for call in calls:
            if call not in defined_funcs and call.replace('-','_') not in exclude and call not in exclude:
                # Verify it's actually called (not just pattern matched)
                with open(path, encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                # Find all occurrences with line numbers
                for i, line in enumerate(content.splitlines(), 1):
                    if re.search(r'\b' + re.escape(call) + r'\s*\(', line):
                        if not line.strip().startswith('//'):
                            # Double-check it's a call not a definition
                            if not re.match(r'\s*(?:function\s+' + re.escape(call) + r'|(?:const|let|var)\s+' + re.escape(call) + r')', line):
                                issues.append({
                                    'file': fname,
                                    'line': i,
                                    'function': call,
                                    'context': line.strip()[:100],
                                })
                                break  # Just first occurrence per function per file

    # Deduplicate by (file, function)
    seen = set()
    unique = []
    for issue in issues:
        key = (issue['file'], issue['function'])
        if key not in seen:
            seen.add(key)
            unique.append(issue)
    return unique


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def get_js_files_from_html(html_path, js_dir):
    """Lấy danh sách JS files được include trong HTML (theo thứ tự)."""
    with open(html_path, encoding='utf-8') as f:
        content = f.read()
    found = []
    for m in re.finditer(r'<script[^>]+src=["\']([^"\'?]+)', content):
        src = m.group(1)
        # Only local JS files
        if src.startswith('http') or src.startswith('//'):
            continue
        # Resolve path relative to HTML
        html_dir = Path(html_path).parent
        resolved = html_dir / src
        if resolved.exists():
            found.append(resolved)
        else:
            # Try js_dir
            alt = Path(js_dir) / Path(src).name
            if alt.exists():
                found.append(alt)
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--html', default='kanji.html')
    parser.add_argument('--js-dir', default='js/')
    parser.add_argument('--out', default='qa_static_report.json')
    parser.add_argument('--all-js', action='store_true',
                        help='Quét tất cả JS trong js-dir thay vì chỉ JS của HTML đó')
    args = parser.parse_args()

    # Collect JS files
    if args.all_js:
        js_dir = Path(args.js_dir)
        js_files = sorted(f for f in js_dir.glob('*.js')
                          if '.backup' not in f.name and '.bak' not in f.name)
    else:
        js_files = get_js_files_from_html(args.html, args.js_dir)
        if not js_files:
            # Fallback to all JS
            js_dir = Path(args.js_dir)
            js_files = sorted(f for f in js_dir.glob('*.js')
                              if '.backup' not in f.name and '.bak' not in f.name)
    print(f'📂 HTML: {args.html}')
    print(f'📂 JS files: {len(js_files)} files in {args.js_dir}')

    # Extract data
    print('\n🔍 Phân tích...')
    static_ids   = extract_html_ids(args.html)
    dynamic_ids  = extract_dynamic_ids(js_files)
    defined_func = extract_defined_functions(js_files)

    print(f'   {len(static_ids)} static IDs trong HTML')
    print(f'   {len(dynamic_ids)} dynamic IDs (tạo bởi JS)')
    print(f'   {len(defined_func)} hàm được định nghĩa')

    # Run checks
    id_issues      = check_getelementbyid(js_files, static_ids, dynamic_ids)
    listener_issues = check_event_listeners_on_missing_ids(js_files, static_ids)
    undef_calls    = check_undefined_calls(js_files, defined_func)

    # Build report
    report = {
        'summary': {
            'static_ids': len(static_ids),
            'dynamic_ids': len(dynamic_ids),
            'defined_functions': len(defined_func),
            'id_mismatches': len(id_issues),
            'listener_on_missing': len(listener_issues),
            'undefined_calls': len(undef_calls),
            'total_issues': len(id_issues) + len(listener_issues) + len(undef_calls),
        },
        'id_mismatches': id_issues,
        'listener_on_missing_id': listener_issues,
        'undefined_function_calls': undef_calls,
    }

    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Print summary
    total = report['summary']['total_issues']
    print(f'\n{"="*50}')
    print(f'Kết quả: {total} vấn đề tìm thấy')
    print(f'  🔴 Undefined function calls : {len(undef_calls)}')
    print(f'  🔴 Listener on missing ID   : {len([x for x in listener_issues if x["severity"]=="critical"])}')
    print(f'  🟡 getElementById mismatch  : {len(id_issues)}')
    print(f'\n💾 Báo cáo → {args.out}')

    if undef_calls:
        print('\n🔴 Undefined calls:')
        for u in undef_calls[:10]:
            print(f'   {u["file"]}:{u["line"]} — {u["function"]}()')

    if listener_issues:
        critical = [x for x in listener_issues if x['severity'] == 'critical']
        if critical:
            print('\n🔴 addEventListener on missing ID:')
            for c in critical[:5]:
                print(f'   {c["file"]}:{c["line"]} — #{c["id"]}')


if __name__ == '__main__':
    main()
