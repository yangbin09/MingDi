import { test, expect } from '@playwright/test'

/**
 * 日志中心页面测试
 * 验证日志列表和筛选功能
 */
test.describe('日志中心页面测试', () => {
  test('日志中心页面正常加载', async ({ page }) => {
    await page.goto('/logs')
    await page.waitForLoadState('networkidle')

    // 验证页面标题
    await expect(page.locator('.header-left .text-sm')).toContainText('日志中心')
  })

  test('日志表格或空状态显示', async ({ page }) => {
    await page.goto('/logs')
    await page.waitForLoadState('networkidle')

    // 等待页面加载
    await page.waitForTimeout(1000)

    // 表格或空状态应该有一个可见
    const hasTable = await page.locator('.el-table').isVisible().catch(() => false)
    const hasEmpty = await page.locator('.el-empty').isVisible().catch(() => false)

    expect(hasTable || hasEmpty).toBeTruthy()
  })

  test('刷新按钮功能正常', async ({ page }) => {
    await page.goto('/logs')
    await page.waitForLoadState('networkidle')

    // 点击头部刷新按钮
    const refreshBtn = page.locator('.header-right .el-button')
    await expect(refreshBtn).toBeVisible()
    await refreshBtn.click()

    // 页面应该仍然正常
    await expect(page.locator('.app-main')).toBeVisible()
  })
})
