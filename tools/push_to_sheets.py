"""
Push lessons.json, blogs.json và kanji-data.js lên Google Sheets.
Chạy lần đầu sẽ mở browser để đăng nhập Google.

Usage:
    python tools/push_to_sheets.py            # push tất cả
    python tools/push_to_sheets.py kanji      # chỉ push kanji
    python tools/push_to_sheets.py lessons    # chỉ push lessons
    python tools/push_to_sheets.py blogs      # chỉ push blogs
"""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ── Google Sheets IDs ──────────────────────────────────────────────────────
SPREADSHEET_ID = '18L12LLSISwxwaolxC6AlJT04ei7Fib9ea90UC96qdT0'
LESSON_GID     = '1629647114'
BLOG_GID       = '764836700'
KANJI_GID      = '1657974799'

# ── Cột tương ứng ─────────────────────────────────────────────────────────
LESSON_COLS = ['title','lang','cat','thumb','bg','type','dur','xp']
BLOG_COLS   = ['title','lang','cat','flag','tagBg','tagC','tag','excerpt','date','views','bg']
KANJI_COLS  = ['kanji','hanviet','level','on','kun','meaning','meaning_en',
               'mn_vi','stroke','freq_rank','grade','radical','parts','mnemonic','words']

# ── Helpers ────────────────────────────────────────────────────────────────
def to_rows(data, cols):
    rows = [cols]
    for item in data:
        rows.append([str(item.get(c, '')) for c in cols])
    return rows

def parse_kanji_js(filepath):
    """Parse kanji-data.js (JS literal) → list of dicts."""
    content = Path(filepath).read_text(encoding='utf-8')

    # Strip JS comments and variable declaration
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    # Extract the array content between first [ and last ]
    start = content.find('[')
    end   = content.rfind(']') + 1
    js_arr = content[start:end]

    # Convert JS object literal → valid JSON
    # Unquoted keys → quoted keys
    js_arr = re.sub(r'(\b)(\w+)(\s*):', r'"\2":', js_arr)
    # Single-quoted strings → double-quoted
    js_arr = re.sub(r"'([^']*)'", r'"\1"', js_arr)
    # Trailing commas before } or ]
    js_arr = re.sub(r',\s*([}\]])', r'\1', js_arr)

    try:
        data = json.loads(js_arr)
    except json.JSONDecodeError as e:
        print(f"  ⚠️  JSON parse error: {e}")
        print("  Thử fallback regex parser...")
        data = _regex_parse_kanji(content)

    return data

def _regex_parse_kanji(content):
    """Fallback: extract entries by tracking brace depth."""
    entries = []

    # Find start of array
    arr_start = content.find('[')
    if arr_start == -1:
        return entries

    i = arr_start + 1
    n = len(content)

    while i < n:
        # Find next opening brace (start of entry)
        while i < n and content[i] != '{':
            i += 1
        if i >= n:
            break

        # Track depth to find matching closing brace
        depth = 0
        start = i
        while i < n:
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1

        block = content[start:i+1]
        i += 1

        def get_str(key, blk=block):
            m = re.search(rf'\b{key}\s*:\s*"((?:[^"\\]|\\.)*)"', blk)
            return m.group(1) if m else ''

        def get_num(key, blk=block):
            m = re.search(rf'\b{key}\s*:\s*(\d+)', blk)
            return m.group(1) if m else ''

        def get_parts(blk=block):
            m = re.search(r'\bparts\s*:\s*\[([^\]]*)\]', blk)
            if not m: return ''
            return ', '.join(re.findall(r'"([^"]+)"', m.group(1)))

        def get_words(blk=block):
            m = re.search(r'\bwords\s*:\s*\[(.+?)\](?=\s*[,}])', blk, re.DOTALL)
            if not m: return ''
            ws = re.findall(r'"w"\s*:\s*"([^"]+)"', m.group(1))
            rs = re.findall(r'"r"\s*:\s*"([^"]+)"', m.group(1))
            ms = re.findall(r'"m"\s*:\s*"([^"]+)"', m.group(1))
            parts = []
            for j in range(min(len(ws), 5)):
                r_ = rs[j] if j < len(rs) else ''
                m_ = ms[j] if j < len(ms) else ''
                parts.append(f"{ws[j]} ({r_}): {m_}")
            return ' | '.join(parts)

        if not get_str('kanji'):
            continue

        entries.append({
            'kanji':      get_str('kanji'),
            'hanviet':    get_str('hanviet'),
            'level':      get_str('level'),
            'on':         get_str('on'),
            'kun':        get_str('kun'),
            'meaning':    get_str('meaning'),
            'meaning_en': get_str('meaning_en'),
            'mn_vi':      get_str('mn_vi'),
            'stroke':     get_num('stroke'),
            'freq_rank':  get_num('freq_rank'),
            'grade':      get_num('grade'),
            'radical':    get_str('radical'),
            'parts':      get_parts(),
            'mnemonic':   get_str('mnemonic'),
            'words':      get_words(),
        })

    return entries

def kanji_to_rows(data):
    """Convert parsed kanji list → sheet rows."""
    rows = [KANJI_COLS]
    for k in data:
        # words: [{"w":"安心","r":"あんしん","m":"an tâm"}, ...] → "安心 (あんしん): an tâm"
        words = k.get('words', [])
        if isinstance(words, list):
            words_str = ' | '.join(
                f"{w.get('w','')} ({w.get('r','')}): {w.get('m','')}"
                for w in words[:5]  # giới hạn 5 từ để không quá dài
            )
        else:
            words_str = str(words)

        # parts: list → comma separated
        parts = k.get('parts', [])
        parts_str = ', '.join(parts) if isinstance(parts, list) else str(parts)

        rows.append([
            k.get('kanji',''),
            k.get('hanviet',''),
            k.get('level',''),
            k.get('on',''),
            k.get('kun',''),
            k.get('meaning',''),
            k.get('meaning_en',''),
            k.get('mn_vi',''),
            str(k.get('stroke','')),
            str(k.get('freq_rank','')),
            str(k.get('grade','')),
            k.get('radical',''),
            parts_str,
            k.get('mnemonic',''),
            words_str,
        ])
    return rows

# ── Auth ───────────────────────────────────────────────────────────────────
def get_credentials():
    try:
        import gspread
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    except ImportError:
        print("Cài thêm: pip install gspread google-auth-oauthlib")
        sys.exit(1)

    SCOPES    = ['https://www.googleapis.com/auth/spreadsheets']
    cred_file = ROOT / 'tools' / 'oauth_credentials.json'
    token_file= ROOT / 'tools' / 'token.json'

    if not cred_file.exists():
        print(f"\n❌ Thiếu file credentials: {cred_file}")
        sys.exit(1)

    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(cred_file), SCOPES)
            creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json())

    return gspread.authorize(creds)

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else 'all'

    gc = get_credentials()
    sh = gc.open_by_key(SPREADSHEET_ID)

    if mode in ('all', 'lessons'):
        lessons = json.loads((ROOT / 'lessons.json').read_text(encoding='utf-8'))
        ws = sh.get_worksheet_by_id(int(LESSON_GID))
        ws.clear()
        ws.update(to_rows(lessons, LESSON_COLS), value_input_option='USER_ENTERED')
        print(f"✅ Đã push {len(lessons)} bài học lên sheet Lessons")

    if mode in ('all', 'blogs'):
        blogs = json.loads((ROOT / 'blogs.json').read_text(encoding='utf-8'))
        ws = sh.get_worksheet_by_id(int(BLOG_GID))
        ws.clear()
        ws.update(to_rows(blogs, BLOG_COLS), value_input_option='USER_ENTERED')
        print(f"✅ Đã push {len(blogs)} blog lên sheet Blogs")

    if mode in ('all', 'kanji'):
        print("📖 Đang parse kanji-data.js (1481 kanji)...")
        kanji = parse_kanji_js(ROOT / 'js' / 'kanji-data.js')
        print(f"   Parsed: {len(kanji)} kanji")
        rows = kanji_to_rows(kanji)
        ws = sh.get_worksheet_by_id(int(KANJI_GID))
        ws.clear()
        # Push theo batch 500 rows để tránh timeout
        BATCH = 500
        for i in range(0, len(rows), BATCH):
            batch = rows[i:i+BATCH]
            ws.append_rows(batch, value_input_option='USER_ENTERED')
            print(f"   Pushed rows {i}–{i+len(batch)-1}")
        print(f"✅ Đã push {len(kanji)} kanji lên sheet Kanji")

if __name__ == '__main__':
    main()
