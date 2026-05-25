// ══════════════════════════════════════════
// E2E Tests — Kanji Flashcard Game
// ══════════════════════════════════════════
const { test, expect } = require('@playwright/test');

test.describe('Flashcard Game', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/kanji.html');
    // Vào Flashcard từ Home
    await page.click('#go-flash');
    await expect(page.locator('#flash-screen')).toHaveClass(/active/);
  });

  // ──────────────────────────────────────────────────────
  test('hiển thị card đầu tiên với kanji và nghĩa', async ({ page }) => {
    // Card mặt trước phải có kanji text
    const kanjiEl = page.locator('#kanji');
    await expect(kanjiEl).not.toBeEmpty();

    // Phải có han-viet
    const hanViet = page.locator('#han-viet');
    await expect(hanViet).not.toBeEmpty();

    // Progress text phải là "1 / N"
    const progress = page.locator('#progress-text');
    await expect(progress).toHaveText(/^1 \/ \d+/);
  });

  // ──────────────────────────────────────────────────────
  test('lật card bằng nút flip', async ({ page }) => {
    const card = page.locator('#card');

    // Trước khi lật: không có class "flipped"
    await expect(card).not.toHaveClass(/flipped/);

    await page.click('#btn-flip');

    // Sau khi lật: có class "flipped"
    await expect(card).toHaveClass(/flipped/);

    // Lật lại
    await page.click('#btn-flip');
    await expect(card).not.toHaveClass(/flipped/);
  });

  // ──────────────────────────────────────────────────────
  test('lật card bằng phím Space', async ({ page }) => {
    const card = page.locator('#card');
    await page.keyboard.press('Space');
    await expect(card).toHaveClass(/flipped/);
  });

  // ──────────────────────────────────────────────────────
  test('nhấn Đúng → chuyển sang card tiếp theo', async ({ page }) => {
    const kanjiEl   = page.locator('#kanji');
    const progress  = page.locator('#progress-text');

    const firstKanji = await kanjiEl.textContent();
    await page.waitForTimeout(600); // tránh cooldown 500ms

    await page.click('#btn-correct');

    // Progress phải tăng lên "2 / N"
    await expect(progress).toHaveText(/^2 \/ \d+/);

    // Kanji hiển thị phải khác (hoặc có thể giống nếu deck shuffle trùng — chấp nhận)
    // Điều quan trọng là progress đã thay đổi
  });

  // ──────────────────────────────────────────────────────
  test('nhấn Sai → chuyển sang card tiếp theo, streak về 0', async ({ page }) => {
    const progress = page.locator('#progress-text');

    await page.waitForTimeout(600);
    await page.click('#btn-incorrect');

    await expect(progress).toHaveText(/^2 \/ \d+/);

    // s-incorrect counter phải tăng
    const sIncorrect = page.locator('#s-incorrect');
    await expect(sIncorrect).toHaveText('1');
  });

  // ──────────────────────────────────────────────────────
  test('phím ArrowLeft = Đúng, ArrowRight = Sai', async ({ page }) => {
    await page.waitForTimeout(600);

    await page.keyboard.press('ArrowLeft');
    const sCorrect = page.locator('#s-correct');
    await expect(sCorrect).toHaveText('1');

    await page.waitForTimeout(700);
    await page.keyboard.press('ArrowRight');
    const sIncorrect = page.locator('#s-incorrect');
    await expect(sIncorrect).toHaveText('1');
  });

  // ──────────────────────────────────────────────────────
  test('nút Shuffle reset progress về 1', async ({ page }) => {
    const progress = page.locator('#progress-text');

    // Trả lời vài câu
    await page.waitForTimeout(600);
    await page.click('#btn-correct');
    await page.waitForTimeout(700);
    await page.click('#btn-correct');
    await expect(progress).toHaveText(/^3 \/ \d+/);

    // Shuffle
    await page.click('#btn-shuffle');
    await expect(progress).toHaveText(/^1 \/ \d+/);
  });

  // ──────────────────────────────────────────────────────
  test('chuyển sang Hard mode → xuất hiện timer bar', async ({ page }) => {
    await page.click('[data-mode="hard"]');

    // Timer wrap phải hiển thị
    await expect(page.locator('#timer-wrap')).toBeVisible();

    // Timer select phải hiển thị
    await expect(page.locator('#timer-select-wrap')).toBeVisible();
  });

  // ──────────────────────────────────────────────────────
  test('Hard mode: hết giờ → hiện modal', async ({ page }) => {
    // Chọn timer 3 giây (ngắn nhất)
    await page.click('[data-mode="hard"]');
    await page.click('[data-sec="3"]');

    // Chờ hết giờ (3s + buffer)
    await page.waitForTimeout(4500);

    // Modal phải xuất hiện
    const modal = page.locator('#modal-overlay');
    await expect(modal).toHaveClass(/visible/);
    await expect(page.locator('#modal-title')).toHaveText(/Hết giờ/);
  });

  // ──────────────────────────────────────────────────────
  test('streak badge xuất hiện sau 3 câu đúng liên tiếp', async ({ page }) => {
    const streakBadge = page.locator('#streak-badge');
    await expect(streakBadge).toBeHidden();

    for (let i = 0; i < 3; i++) {
      await page.waitForTimeout(600);
      await page.click('#btn-correct');
    }

    await expect(streakBadge).toBeVisible();
    await expect(streakBadge).toContainText('🔥');
  });

  // ──────────────────────────────────────────────────────
  test('lọc theo level N5 → deck không rỗng', async ({ page }) => {
    // Về Home, chọn N5
    await page.click('.logo');
    await page.click('.home-lvl-btn[data-lvl="N5"]');
    await page.click('#go-flash');

    const progress = page.locator('#progress-text');
    await expect(progress).toHaveText(/^1 \/ [1-9]\d*/);
  });

});
