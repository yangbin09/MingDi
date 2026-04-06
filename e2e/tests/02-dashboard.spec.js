import { test, expect } from '@playwright/test'

/**
 * 仪表盘页面测试
 * 验证 Dashboard 页面的各项指标卡片和图表
 */
test.describe('仪表盘页面测试', () => {
  test('仪表盘页面正常加载', async ({ page }) => {
    await page.goto('/')

    // 等待页面加载
    await page.waitForLoadState('networkidle')

    // 验证页面标题
    await expect(page.locator('.header-left .text-sm')).toContainText('仪表盘概览')
  })

  test('系统指标卡片显示正常', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // 验证 CPU 使用率卡片
    const cpuCard = page.locator('.metric-card').filter({ hasText: 'CPU 使用率' })
    await expect(cpuCard).toBeVisible()

    // 验证内存使用卡片
    const memoryCard = page.locator('.metric-card').filter({ hasText: '内存使用' })
    await expect(memoryCard).toBeVisible()

    // 验证磁盘占用卡片
    const diskCard = page.locator('.metric-card').filter({ hasText: '磁盘占用' })
    await expect(diskCard).toBeVisible()
  })

  test('统计卡片显示正常', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // 验证统计卡片存在
    await expect(page.locator('.stat-card, [class*="stats"]').first()).toBeVisible({ timeout: 5000 })
  })

  test('仪表盘点击刷新按钮不崩溃', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // 点击刷新按钮
    const refreshBtn = page.locator('.header-right .el-button')
    await expect(refreshBtn).toBeVisible()
    await refreshBtn.click()

    // 页面应该仍然正常
    await expect(page.locator('.app-main')).toBeVisible()
  })
})
