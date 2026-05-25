const { test, expect } = require('@playwright/test');

test.describe('Bubble E2E', () => {
  test('plays one bubble round: tap bubble, select correct reading', async ({ page }) => {
    await page.goto('/kanji.html');

    // Open Bubble game
    await page.click('#go-bubble');
    await expect(page.locator('#bub-arena')).toBeVisible();

    // Wait for bubbles to spawn
    await page.waitForSelector('#bub-arena .bub-kanji', { timeout: 5000 });

    // Pick first bubble and read its dataset
    const first = page.locator('#bub-arena .bub-kanji').first();
    const idx = await first.getAttribute('data-idx');

    // Click bubble -> options should appear
    await first.click();
    await expect(page.locator('#bub-meanings')).toBeVisible();

    // Grab correct reading from bCurrentPairs via DOM question label
    const correctReading = await page.evaluate(() => {
      const q = document.querySelector('#bub-meanings');
      if (!q) return null;
      const pair = window.bCurrentPairs && window.bCurrentPairs[0];
      return pair ? pair.correctReading : null;
    });

    expect(correctReading).not.toBeNull();

    // Click the button that matches the correct reading
    const btn = page.locator('#bub-options-grid .bub-meaning-btn').filter({ hasText: correctReading }).first();
    await btn.click();

    // Expect bubble removed and HUD updated
    await expect(first).toBeHidden({ timeout: 2000 });
    await expect(page.locator('#bub-correct')).not.toHaveText('0');
  });
});
