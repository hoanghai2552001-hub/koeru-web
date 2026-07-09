// ══════════════════════════════════════════
// E2E Tests — Kanji Flashcard Game
// ══════════════════════════════════════════
const { test, expect } = require('@playwright/test');

// Trả lời 1 thẻ và chờ chuyển sang thẻ tiếp theo.
// Game có cooldown 500ms sau khi render thẻ + animation 600ms sau khi trả lời,
// nên phải chờ progress text đổi thật sự thay vì dùng timeout cố định.
async function answerCard(page, selector) {
  const progress = page.locator('#progress-text');
  const before = await progress.textContent();
  await page.waitForTimeout(650); // hết cooldown 500ms sau render
  await page.click(selector);
  await expect(progress).not.toHaveText(before, { timeout: 5000 });
}

test.describe('Flashcard Game', () => {

  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      // Bỏ qua onboarding overlay (chỉ hiện lần đầu, chặn mọi click)
      localStorage.setItem('kanji_visited', '1');
      // Game Easy hiện nghĩa ngẫu nhiên đúng/sai (Math.random() > .45).
      // Stub để nghĩa hiển thị LUÔN ĐÚNG → nút "Đúng" = trả lời đúng,
      // nút "Sai" = trả lời sai — test được deterministic.
      Math.random = () => 0.9;
    });
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
    const progress = page.locator('#progress-text');

    await answerCard(page, '#btn-correct');

    // Progress phải tăng lên "2 / N"
    await expect(progress).toHaveText(/^2 \/ \d+/);
  });

  // ──────────────────────────────────────────────────────
  test('nhấn Sai → chuyển sang card tiếp theo, streak về 0', async ({ page }) => {
    const progress = page.locator('#progress-text');

    await answerCard(page, '#btn-incorrect');

    await expect(progress).toHaveText(/^2 \/ \d+/);

    // Nghĩa hiển thị luôn đúng (Math.random stub) → nhấn Sai = trả lời sai
    const sIncorrect = page.locator('#s-incorrect');
    await expect(sIncorrect).toHaveText('1');
  });

  // ──────────────────────────────────────────────────────
  test('phím ArrowLeft = Đúng, ArrowRight = Sai', async ({ page }) => {
    const progress = page.locator('#progress-text');

    let before = await progress.textContent();
    await page.waitForTimeout(650);
    await page.keyboard.press('ArrowLeft');
    await expect(progress).not.toHaveText(before);
    const sCorrect = page.locator('#s-correct');
    await expect(sCorrect).toHaveText('1');

    before = await progress.textContent();
    await page.waitForTimeout(650);
    await page.keyboard.press('ArrowRight');
    await expect(progress).not.toHaveText(before);
    const sIncorrect = page.locator('#s-incorrect');
    await expect(sIncorrect).toHaveText('1');
  });

  // ──────────────────────────────────────────────────────
  test('nút Shuffle reset progress về 1', async ({ page }) => {
    const progress = page.locator('#progress-text');

    // Trả lời 2 câu
    await answerCard(page, '#btn-correct');
    await answerCard(page, '#btn-correct');
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

    // Nghĩa hiển thị luôn đúng (Math.random stub) → 3 lần Đúng = streak 3
    for (let i = 0; i < 3; i++) {
      await answerCard(page, '#btn-correct');
    }

    await expect(streakBadge).toBeVisible();
    await expect(streakBadge).toContainText('🔥');
  });

  // ──────────────────────────────────────────────────────
  test('lọc theo level N5 → deck không rỗng', async ({ page }) => {
    // Về Home, chọn N5
    await page.click('#flash-back');
    await page.click('.home-lvl-btn[data-lvl="N5"]');
    await page.click('#go-flash');

    const progress = page.locator('#progress-text');
    await expect(progress).toHaveText(/^1 \/ [1-9]\d*/);
  });

});
