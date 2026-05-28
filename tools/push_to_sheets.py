"""
Push lessons.json và blogs.json lên Google Sheets.
Chạy lần đầu sẽ mở browser để đăng nhập Google.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ── Google Sheets IDs ──────────────────────────────────────────────────────
SPREADSHEET_ID = '18L12LLSISwxwaolxC6AlJT04ei7Fib9ea90UC96qdT0'
LESSON_GID     = '1629647114'
BLOG_GID       = '764836700'

# ── Cột tương ứng ─────────────────────────────────────────────────────────
LESSON_COLS = ['title','lang','cat','thumb','bg','type','dur','xp']
BLOG_COLS   = ['title','lang','cat','flag','tagBg','tagC','tag','excerpt','date','views','bg']

def to_rows(data, cols):
    rows = [cols]
    for item in data:
        rows.append([str(item.get(c,'')) for c in cols])
    return rows

def main():
    try:
        import gspread
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    except ImportError:
        print("Cài thêm: pip install gspread google-auth-oauthlib")
        sys.exit(1)

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    cred_file = ROOT / 'tools' / 'oauth_credentials.json'
    token_file = ROOT / 'tools' / 'token.json'

    if not cred_file.exists():
        print(f"\n❌ Thiếu file credentials: {cred_file}")
        print("Hướng dẫn:")
        print("  1. Vào https://console.cloud.google.com/")
        print("  2. Tạo project → Enable Google Sheets API")
        print("  3. Credentials → OAuth 2.0 → Desktop App → Download JSON")
        print(f"  4. Đổi tên thành oauth_credentials.json → để vào {cred_file.parent}")
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

    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)

    # ── Lessons ────────────────────────────────────────────────────────────
    lessons = json.loads((ROOT / 'lessons.json').read_text(encoding='utf-8'))
    ws_l = sh.get_worksheet_by_id(int(LESSON_GID))
    ws_l.clear()
    ws_l.update(to_rows(lessons, LESSON_COLS), value_input_option='USER_ENTERED')
    print(f"✅ Đã push {len(lessons)} bài học lên sheet")

    # ── Blogs ──────────────────────────────────────────────────────────────
    blogs = json.loads((ROOT / 'blogs.json').read_text(encoding='utf-8'))
    ws_b = sh.get_worksheet_by_id(int(BLOG_GID))
    ws_b.clear()
    ws_b.update(to_rows(blogs, BLOG_COLS), value_input_option='USER_ENTERED')
    print(f"✅ Đã push {len(blogs)} blog lên sheet")

if __name__ == '__main__':
    main()
