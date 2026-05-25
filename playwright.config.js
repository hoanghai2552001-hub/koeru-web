const { devices } = require('@playwright/test');

/** @type {import('@playwright/test').PlaywrightTestConfig} */
module.exports = {
  // Timeout mỗi test (ms)
  timeout: 60000,

  // Retry khi fail (CI: 2, local: 0)
  retries: process.env.CI ? 2 : 0,

  // Chạy song song
  workers: process.env.CI ? 2 : 1,

  // Report
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
  ],

  use: {
    headless: true,
    viewport: { width: 1280, height: 800 },
    ignoreHTTPSErrors: true,
    actionTimeout: 10000,
    baseURL: 'http://localhost:8000',
    // Chụp ảnh khi test fail
    screenshot: 'only-on-failure',
    // Lưu trace khi retry
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  // Tự khởi động server trước khi test
  webServer: {
    command: 'python3 -m http.server 8000',
    url: 'http://localhost:8000',
    reuseExistingServer: !process.env.CI,
    timeout: 10000,
  },
};
