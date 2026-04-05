/**
 * Shared utility functions for PyCron-Master
 * Centralizes formatting and helper functions to avoid duplication
 */

/**
 * Format timestamp to localized Chinese string
 * @param {string|Date} timeStr - ISO date string or Date object
 * @returns {string} Formatted date string
 */
export function formatTime(timeStr) {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Format full timestamp with seconds
 * @param {string|Date} timeStr
 * @returns {string}
 */
export function formatTimeFull(timeStr) {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN')
}

/**
 * Get Chinese status text
 * @param {string} status - Status value
 * @returns {string} Chinese status text
 */
export function statusText(status) {
  const texts = {
    idle: '闲置',
    running: '运行中',
    success: '成功',
    failed: '失败',
    timeout: '超时'
  }
  return texts[status] || status
}

/**
 * Get status color for UI
 * @param {string} status
 * @returns {string} CSS variable value
 */
export function getStatusColor(status) {
  const colors = {
    running: 'var(--color-primary)',
    success: 'var(--color-success)',
    failed: 'var(--color-danger)',
    timeout: 'var(--color-warning)',
    idle: 'var(--text-muted)'
  }
  return colors[status] || 'var(--text-muted)'
}

/**
 * Parse cron expression to human-readable Chinese text
 * @param {string} expr - Cron expression
 * @returns {string} Human readable text
 */
export function cronHumanText(expr) {
  if (!expr) return ''
  try {
    const parts = expr.split(' ')
    if (parts.length !== 5) return ''
    const [min, hour, day, month, week] = parts

    if (expr === '* * * * *') return '每分钟执行一次'
    if (expr === '0 * * * *') return '每小时整点执行'
    if (day === '*' && month === '*' && week === '*')
      return `每天 ${hour}:${min.padStart(2, '0')} 执行`
    if (week !== '*' && day === '*') {
      const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      const dayIndex = parseInt(week)
      if (!isNaN(dayIndex) && weekDays[dayIndex]) {
        return `每周${weekDays[dayIndex]} ${hour}:${min.padStart(2, '0')} 执行`
      }
      return `每周${week} ${hour}:${min.padStart(2, '0')} 执行`
    }
    return `将在 ${expr} 执行`
  } catch {
    return ''
  }
}

/**
 * Highlight search keyword in text (for log viewer)
 * @param {string} text - Original text
 * @param {string} keyword - Search keyword
 * @returns {string} HTML with marked keywords
 */
export function highlightKeyword(text, keyword) {
  if (!keyword) return escapeHtml(text)
  const escapedKw = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const escaped = escapeHtml(text)
  return escaped.replace(
    new RegExp(`(${escapedKw})`, 'gi'),
    '<mark style="background-color: var(--color-warning-subtle); color: var(--color-warning); padding: 0 2px; border-radius: 2px;">$1</mark>'
  )
}

/**
 * Escape HTML special characters
 * @param {string} text
 * @returns {string}
 */
function escapeHtml(text) {
  if (!text) return ''
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

/**
 * Truncate text with ellipsis
 * @param {string} text
 * @param {number} maxLength
 * @returns {string}
 */
export function truncate(text, maxLength = 50) {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

/**
 * Format bytes to human readable size
 * @param {number} bytes
 * @returns {string}
 */
export function formatBytes(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * Format duration in seconds to human readable
 * @param {number} seconds
 * @returns {string}
 */
export function formatDuration(seconds) {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds.toFixed(1)}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${(seconds % 60).toFixed(0)}s`
  return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
}

/**
 * Debounce function for search inputs
 * @param {Function} func
 * @param {number} wait
 * @returns {Function}
 */
export function debounce(func, wait = 300) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Deep clone object (JSON safe)
 * @param {any} obj
 * @returns {any}
 */
export function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj))
}

/**
 * Check if object is empty
 * @param {object} obj
 * @returns {boolean}
 */
export function isEmpty(obj) {
  if (!obj) return true
  return Object.keys(obj).length === 0
}

// Cron presets for UI
export const CRON_PRESETS = [
  { label: '每分钟', value: '* * * * *' },
  { label: '每小时', value: '0 * * * *' },
  { label: '每天凌晨', value: '0 2 * * *' },
  { label: '每周一', value: '0 9 * * 1' }
]

// Default export with all utilities
export default {
  formatTime,
  formatTimeFull,
  statusText,
  getStatusColor,
  cronHumanText,
  highlightKeyword,
  truncate,
  formatBytes,
  formatDuration,
  debounce,
  deepClone,
  isEmpty,
  CRON_PRESETS
}
