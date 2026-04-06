import { test, expect } from '@playwright/test'

/**
 * 系统设置页面测试
 * 验证设置表单功能
 */
test.describe('系统设置页面测试', () => {
  test('设置页面正常加载', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForLoadState('networkidle')

    // 验证页面标题
    await expect(page.locator('.header-left .text-sm')).toContainText('系统设置')
  })

  test('设置表单元素存在', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForLoadState('domcontentloaded')

    // 等待页面加载
    await page.waitForTimeout(1000)

    // 验证有设置相关的元素存在（卡片、表单、或输入框）
    const hasSettingElements = await page.locator('.el-card, .el-input, .el-switch, [class*="setting"]').first().isVisible().catch(() => false)
    expect(hasSettingElements).toBeTruthy()
  })

  test('主题切换器存在', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForLoadState('networkidle')

    // 验证主题切换相关元素
    const themeSwitcher = page.locator('.theme-switcher, [class*="theme"], .el-switch')
    await expect(themeSwitcher.first()).toBeVisible({ timeout: 3000 })
  })
})
