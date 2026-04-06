import { test, expect } from '@playwright/test'

/**
 * AI 助手页面测试
 * 验证 AI 助手功能
 */
test.describe('AI 助手页面测试', () => {
  test('AI 助手页面正常加载', async ({ page }) => {
    await page.goto('/ai')
    await page.waitForLoadState('networkidle')

    // 验证页面标题
    await expect(page.locator('.header-left .text-sm')).toContainText('AI 助手')
  })

  test('AI 对话区域或输入框存在', async ({ page }) => {
    await page.goto('/ai')
    await page.waitForLoadState('networkidle')

    // 等待页面加载
    await page.waitForTimeout(500)

    // 查找输入框或对话区域
    const hasInput = await page.locator('textarea, input[type="text"], .el-input').first().isVisible().catch(() => false)
    const hasChatArea = await page.locator('[class*="chat"], [class*="message"], [class*="dialog"]').first().isVisible().catch(() => false)

    expect(hasInput || hasChatArea).toBeTruthy()
  })
})

/**
 * 节点编排页面测试
 * 验证流程编排功能
 */
test.describe('节点编排页面测试', () => {
  test('节点编排页面正常加载', async ({ page }) => {
    await page.goto('/flows')
    await page.waitForLoadState('networkidle')

    // 验证页面标题
    await expect(page.locator('.header-left .text-sm')).toContainText('节点编排')
  })

  test('流程画布或节点区域存在', async ({ page }) => {
    await page.goto('/flows')
    await page.waitForLoadState('networkidle')

    // 等待页面加载
    await page.waitForTimeout(500)

    // 查找画布区域
    const hasCanvas = await page.locator('[class*="canvas"], [class*="flow"], [class*="node"]').first().isVisible().catch(() => false)

    // 或者为空状态
    const hasEmpty = await page.locator('.el-empty').isVisible().catch(() => false)

    expect(hasCanvas || hasEmpty).toBeTruthy()
  })
})
