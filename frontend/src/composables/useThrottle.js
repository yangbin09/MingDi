import { ref } from 'vue'

export function useThrottle(fn, delay = 100) {
  let lastTime = 0
  let timerId = null

  function throttled(...args) {
    const now = Date.now()
    if (now - lastTime >= delay) {
      lastTime = now
      fn(...args)
    } else {
      // Schedule for later if not already scheduled
      if (!timerId) {
        timerId = setTimeout(() => {
          lastTime = Date.now()
          timerId = null
          fn(...args)
        }, delay - (now - lastTime))
      }
    }
  }

  function cancel() {
    if (timerId) {
      clearTimeout(timerId)
      timerId = null
    }
  }

  return {
    throttled,
    cancel
  }
}
