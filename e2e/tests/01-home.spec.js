import { test, expect } from '@playwright/test'

/**
 * 首页访问测试
 * 验证应用首页是否正常加载
 */
test.describe('首页访问测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(500) // 等待 Vue 初始化
  })

  test('页面标题和侧边栏加载正常', async ({ page }) => {
    // 验证侧边栏 Logo
    await expect(page.locator('.sidebar-logo h1')).toBeVisible({ timeout: 10000 })

    // 验证侧边栏菜单位置
    await expect(page.locator('.sidebar-menu')).toBeVisible()

    // 验证主要导航项存在
    await expect(page.locator('.sidebar-menu')).toContainText('仪表盘')
    await expect(page.locator('.sidebar-menu')).toContainText('任务管理')
    await expect(page.locator('.sidebar-menu')).toContainText('日志中心')
    await expect(page.locator('.sidebar-menu')).toContainText('AI 助手')
    await expect(page.locator('.sidebar-menu')).toContainText('节点编排')
    await expect(page.locator('.sidebar-menu')).toContainText('系统设置')
  })

  test('Header 区域正常显示', async ({ page }) => {
    // 验证头部区域可见
    await expect(page.locator('.app-header')).toBeVisible({ timeout: 10000 })

    // 验证头部右侧按钮存在
    await expect(page.locator('.header-right .el-button')).toBeVisible()
  })

  test('主内容区域正常渲染', async ({ page }) => {
    // 验证主内容区域可见
    await expect(page.locator('.app-main')).toBeVisible()
  })
})
