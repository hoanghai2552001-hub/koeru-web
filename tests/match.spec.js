// ══════════════════════════════════════════
// E2E Tests — Kanji Match Game (Nối từ)
// Markup hiện tại: .match-item.kanji-item / .match-item.meaning-item
// (trong #left-col / #right-col), data-id = kanji, timer là thanh
// #match-timer-bar (scaleX giảm dần), 3 mạng ❤️.
// ══════════════════════════════════════════
const { test, expect } = require('@playwright/test');

// Đọc scaleX hiện tại của thanh timer
async function timerScale(page) {
  return page.$eval('#match-timer-bar', el => {
    const m = /scaleX\(([\d.]+)\)/.exec(el.style.transform || '');
    return m ? parseFloat(m[1]) : 1;
  });
}

test.describe('Match Game (Nối từ)', () => {

  test.beforeEach(async ({ page }) => {
    // Bỏ qua onboarding overlay (chỉ hiện lần đầu, chặn mọi click)
    await page.addInitScript(() => localStorage.setItem('kanji_visited', '1'));
    await page.goto('/kanji.html');
    await page.click('#go-match');
    await expect(page.locator('#match-screen')).toHaveClass(/active/);
  });

  // ──────────────────────────────────────────────────────
  test('hiển thị đúng số cặp kanji và nghĩa', async ({ page }) => {
    // Mặc định vòng 1 có 4 cặp → 4 item kanji + 4 item nghĩa
    const kanjiItems   = page.locator('#left-col .match-item.kanji-item');
    const meaningItems = page.locator('#right-col .match-item.meaning-item');

    await expect(kanjiItems).toHaveCount(4);
    await expect(meaningItems).toHaveCount(4);

    // Round text hiển thị "Vòng 1 · 4 cặp"
    await expect(page.locator('#match-round-text')).toContainText('Vòng 1');
  });

  // ──────────────────────────────────────────────────────
  test('timer đang đếm ngược', async ({ page }) => {
    await expect(page.locator('#match-timer-bar')).toBeAttached();

    await page.waitForTimeout(500); // để timer khởi động
    const t1 = await timerScale(page);
    await page.waitForTimeout(2000);
    const t2 = await timerScale(page);

    expect(t2).toBeLessThan(t1);
  });

  // ──────────────────────────────────────────────────────
  test('click kanji item → item được highlight', async ({ page }) => {
    const firstKanji = page.locator('#left-col .match-item').first();
    await firstKanji.click();
    await expect(firstKanji).toHaveClass(/selected/);
  });

  // ──────────────────────────────────────────────────────
  test('ghép cặp đúng → cả 2 item matched rồi biến mất', async ({ page }) => {
    // data-id của item bên trái = kanji; item bên phải cùng data-id là cặp đúng
    const firstLeft = page.locator('#left-col .match-item').first();
    const id = await firstLeft.getAttribute('data-id');

    await firstLeft.click();
    await page.locator(`#right-col .match-item[data-id="${id}"]`).click();

    // Sau khi ghép đúng: 2 item bị remove khỏi DOM (sau animation ~650ms)
    await expect(page.locator(`#left-col .match-item[data-id="${id}"]`))
      .toHaveCount(0, { timeout: 3000 });
    await expect(page.locator('#match-pairs-left')).toContainText('Còn 3 cặp');
  });

  // ──────────────────────────────────────────────────────
  test('ghép cặp sai → mất 1 mạng, bỏ chọn cả 2', async ({ page }) => {
    const leftItems = page.locator('#left-col .match-item');
    const firstLeft = leftItems.first();
    const id = await firstLeft.getAttribute('data-id');

    await firstLeft.click();
    // Chọn item bên phải KHÁC data-id → chắc chắn sai
    await page.locator(`#right-col .match-item:not([data-id="${id}"])`).first().click();

    // Mất 1 mạng: hiện 🖤
    await expect(page.locator('#match-lives')).toContainText('🖤');

    // Sau animation 400ms: cả 2 bỏ chọn, game vẫn chạy
    await page.waitForTimeout(600);
    await expect(page.locator('.match-item.selected')).toHaveCount(0);
    await expect(page.locator('#match-screen')).toHaveClass(/active/);
  });

  // ──────────────────────────────────────────────────────
  test('hoàn thành vòng → chuyển sang vòng tiếp theo', async ({ page }) => {
    // Ghép hết 4 cặp theo data-id
    for (let i = 0; i < 4; i++) {
      const left = page.locator('#left-col .match-item').first();
      const id = await left.getAttribute('data-id');
      await left.click();
      await page.locator(`#right-col .match-item[data-id="${id}"]`).click();
      // chờ cặp bị remove (animation ~650ms) trước khi ghép tiếp
      await expect(page.locator(`#left-col .match-item[data-id="${id}"]`))
        .toHaveCount(0, { timeout: 3000 });
    }

    // Vòng 2 phải load (4 item mới, round text đổi)
    await expect(page.locator('#match-round-text')).toContainText('Vòng 2', { timeout: 5000 });
    await expect(page.locator('#left-col .match-item')).toHaveCount(4);
  });

  // ──────────────────────────────────────────────────────
  test('lọc level N5 → game vẫn start, item thuộc N5', async ({ page }) => {
    // Về Home chọn N5 trước khi vào Match
    await page.click('#match-back');
    await page.click('.home-lvl-btn[data-lvl="N5"]');
    await page.click('#go-match');

    await expect(page.locator('#match-screen')).toHaveClass(/active/);
    const leftItems = page.locator('#left-col .match-item');
    await expect(leftItems.first()).toBeVisible();

    // Mọi kanji hiển thị phải thuộc level N5 (đối chiếu window.KANJI_DATA)
    const ids = await leftItems.evaluateAll(els => els.map(e => e.dataset.id));
    const levels = await page.evaluate(ids =>
      ids.map(id => (window.KANJI_DATA.find(k => k.kanji === id) || {}).level),
      ids);
    for (const lv of levels) expect(lv).toBe('N5');
  });

});
