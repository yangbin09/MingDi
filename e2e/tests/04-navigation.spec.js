import { test, expect } from '@playwright/test'

/**
 * 导航测试
 * 验证所有页面导航功能
 */
test.describe('导航测试', () => {
  const routes = [
    { path: '/', name: '仪表盘' },
    { path: '/tasks', name: '任务管理' },
    { path: '/logs', name: '日志中心' },
    { path: '/ai', name: 'AI 助手' },
    { path: '/flows', name: '节点编排' },
    { path: '/settings', name: '系统设置' },
  ]

  test('侧边栏导航链接全部可点击', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    for (const route of routes) {
      const menuItem = page.locator(`.sidebar-menu .el-menu-item:has-text("${route.name}")`)
      await expect(menuItem).toBeVisible()
      await menuItem.click()
      await expect(page).toHaveURL(new RegExp(route.path), { timeout: 3000 })
    }
  })

  test('URL 直接访问各页面正常', async ({ page }) => {
    for (const route of routes) {
      await page.goto(route.path)
      await page.waitForLoadState('networkidle')
      await expect(page.locator('.app-main')).toBeVisible()
    }
  })

  test('快速执行代码按钮存在', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // 验证快速执行代码按钮
    const scratchpadBtn = page.locator('.scratchpad-btn, button:has-text("快速执行代码")')
    await expect(scratchpadBtn.first()).toBeVisible()
  })
})
