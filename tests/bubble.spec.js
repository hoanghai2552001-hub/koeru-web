// ══════════════════════════════════════════
// E2E Tests — Kanji Dungeon (nút "Bubble" cũ, game đã thay bằng Dungeon RPG)
// Chọn âm On/Kun đúng cho kanji của quái. Markup: dng-* (js/kanji-bubble.js)
// Luồng game:
//   - Đúng  → popup từ ghép thay ngay #dng-options (highlight biến mất tức thì),
//             tự tiếp tục sau ~2.2s → quái tiếp theo (2/10)
//   - Sai   → nút đúng được highlight .dng-opt-correct trong 1.6s,
//             hero -1 HP, render lại CÙNG quái để thử lại
// ══════════════════════════════════════════
const { test, expect } = require('@playwright/test');

// Sau khi click 1 lựa chọn, chờ 1 trong 2 kết cục:
// 'wrong'    → .dng-opt-correct hiện (đã chọn sai)
// 'advanced' → enemy counter sang 2/ (đã chọn đúng, game tự chuyển tiếp)
async function clickAndWaitOutcome(page) {
  await page.locator('.dng-opt-btn').first().click();
  const revealed = page.locator('.dng-opt-correct').first();
  const advanced = page.locator('.dng-enemy-count').filter({ hasText: '2/' }).first();
  await expect(revealed.or(advanced)).toBeVisible({ timeout: 8000 });
  return (await revealed.isVisible().catch(() => false)) ? 'wrong' : 'advanced';
}

// Click đúng nút có text khớp CHÍNH XÁC (tránh substring: "い" nằm trong "せい")
async function clickExactOption(page, text) {
  const btns = page.locator('.dng-opt-btn');
  const texts = await btns.allTextContents();
  const idx = texts.findIndex(t => t.trim() === text);
  expect(idx).toBeGreaterThanOrEqual(0);
  await btns.nth(idx).click();
}

test.describe('Kanji Dungeon E2E', () => {

  test.beforeEach(async ({ page }) => {
    // Bỏ qua onboarding overlay (chỉ hiện lần đầu, chặn mọi click)
    await page.addInitScript(() => localStorage.setItem('kanji_visited', '1'));
    await page.goto('/kanji.html');
    await page.click('#go-bubble');
    await expect(page.locator('#bubble-screen')).toHaveClass(/active/);
  });

  // ──────────────────────────────────────────────────────
  test('hiện quái với kanji + 4 lựa chọn âm đọc', async ({ page }) => {
    await expect(page.locator('#dng-enemy-kanji')).not.toBeEmpty();
    await expect(page.locator('.dng-opt-btn')).toHaveCount(4);
    // Timer bar của câu hỏi phải tồn tại
    await expect(page.locator('#dng-timer-bar')).toBeAttached();
  });

  // ──────────────────────────────────────────────────────
  test('trả lời sai → hiện đáp án đúng, render lại cùng quái để thử lại', async ({ page }) => {
    const outcome = await clickAndWaitOutcome(page);

    if (outcome === 'advanced') {
      // Lỡ chọn trúng ngay từ nút đầu — game đã chuyển tiếp hợp lệ, không còn
      // gì để kiểm cho nhánh sai. Xác nhận game vẫn chạy rồi kết thúc.
      await expect(page.locator('.dng-opt-btn')).toHaveCount(4);
      return;
    }

    // Nhánh sai: streak về 0, vẫn là quái 1/10
    await expect(page.locator('#dng-streak-val')).toHaveText('0');
    await expect(page.locator('.dng-enemy-count')).toContainText('1/');

    const correctReading = (await page.locator('.dng-opt-correct').first().textContent()).trim();

    // Sau 1.6s cùng quái render lại: highlight biến mất, vẫn có nút đáp án đúng cũ
    await expect(page.locator('.dng-opt-correct')).toHaveCount(0, { timeout: 5000 });
    const texts = await page.locator('.dng-opt-btn').allTextContents();
    expect(texts.map(t => t.trim())).toContain(correctReading);
  });

  // ──────────────────────────────────────────────────────
  test('trả lời đúng → streak tăng, chuyển sang quái tiếp theo (2/10)', async ({ page }) => {
    const outcome = await clickAndWaitOutcome(page);

    if (outcome === 'wrong') {
      // Ghi lại đáp án đúng, chờ quái render lại, trả lời đúng lần 2
      const correctReading = (await page.locator('.dng-opt-correct').first().textContent()).trim();
      await expect(page.locator('.dng-opt-correct')).toHaveCount(0, { timeout: 5000 });
      await clickExactOption(page, correctReading);
    }

    // Đã trả lời đúng → game chuyển sang quái 2/10 (popup từ ghép tự tiếp tục)
    await expect(page.locator('.dng-enemy-count')).toContainText('2/', { timeout: 10000 });

    // Streak ≥ 1
    const streakVal = await page.locator('#dng-streak-val').textContent();
    expect(parseInt(streakVal)).toBeGreaterThan(0);
  });

});
