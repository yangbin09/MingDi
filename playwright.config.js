const { defineConfig, devices } = require('@playwright/test')
const path = require('path')

const testOutputDir = path.join(__dirname, 'test-output-local')

module.exports = defineConfig({
  testDir: './e2e/tests',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 1,
  workers: 1,
  reporter: [
    ['html', { outputFolder: path.join(testOutputDir, 'html-report') }],
    ['json', { outputFile: path.join(testOutputDir, 'raw-results', 'results.json') }]
  ],
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
        executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        headless: true,
      },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
    timeout: 120000,
    cwd: './frontend',
  },
  outputDir: testOutputDir,
})
