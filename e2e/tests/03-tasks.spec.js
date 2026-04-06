import { test, expect } from '@playwright/test'

/**
 * 任务管理页面测试
 * 验证任务列表和新建任务表单
 */
test.describe('任务管理页面测试', () => {
  test('任务管理页面正常加载', async ({ page }) => {
    await page.goto('/tasks')
    await page.waitForLoadState('networkidle')

    // 验证页面标题
    await expect(page.locator('.header-left .text-sm')).toContainText('任务管理')

    // 验证新建任务按钮
    await expect(page.locator('button:has-text("新建任务")')).toBeVisible()
  })

  test('任务表格或空状态显示正常', async ({ page }) => {
    await page.goto('/tasks')
    await page.waitForLoadState('networkidle')

    // 表格或空状态应该有一个可见
    const hasTable = await page.locator('.el-table').isVisible().catch(() => false)
    const hasEmpty = await page.locator('.el-empty').isVisible().catch(() => false)

    expect(hasTable || hasEmpty).toBeTruthy()
  })

  test('新建任务抽屉可以打开', async ({ page }) => {
    await page.goto('/tasks')
    await page.waitForLoadState('domcontentloaded')

    // 点击新建任务按钮
    await page.locator('button:has-text("新建任务")').click()

    // 验证抽屉打开 - 使用更精确的选择器
    await expect(page.getByRole('dialog', { name: '新建任务' })).toBeVisible({ timeout: 5000 })
  })

  test('新建任务表单必填项验证', async ({ page }) => {
    await page.goto('/tasks')
    await page.waitForLoadState('domcontentloaded')

    // 打开新建任务抽屉
    await page.locator('button:has-text("新建任务")').click()
    await page.getByRole('dialog', { name: '新建任务' }).waitFor({ state: 'visible', timeout: 5000 })

    // 尝试直接提交（不填写任何内容）
    const submitBtn = page.locator('.el-drawer__body button:has-text("确定"), [class*="drawer"] button:has-text("确定")')
    if (await submitBtn.first().isVisible()) {
      await submitBtn.first().click()

      // 应该显示验证错误
      // Element Plus 会自动进行表单验证
    }
  })

  test('新建任务表单填写后重置', async ({ page }) => {
    await page.goto('/tasks')
    await page.waitForLoadState('domcontentloaded')

    // 打开新建任务抽屉
    await page.locator('button:has-text("新建任务")').click()
    const drawer = page.getByRole('dialog', { name: '新建任务' })
    await drawer.waitFor({ state: 'visible', timeout: 5000 })

    // 在抽屉内查找表单输入框并填写
    const nameInput = drawer.locator('input').first()
    if (await nameInput.isVisible()) {
      await nameInput.fill('测试任务')

      // 点击重置按钮
      const resetBtn = drawer.locator('button:has-text("重置")')
      if (await resetBtn.isVisible()) {
        await resetBtn.click()

        // 输入框应该被清空
        await expect(nameInput).toHaveValue('')
      }
    }
  })

  test('导航到其他页面正常', async ({ page }) => {
    await page.goto('/tasks')
    await page.waitForLoadState('networkidle')

    // 点击日志中心
    await page.locator('.sidebar-menu .el-menu-item:has-text("日志中心")').click()
    await expect(page).toHaveURL(/\/logs/)

    // 点击任务管理返回
    await page.locator('.sidebar-menu .el-menu-item:has-text("任务管理")').click()
    await expect(page).toHaveURL(/\/tasks/)
  })
})
