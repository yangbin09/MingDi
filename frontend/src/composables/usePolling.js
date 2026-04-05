import { ref, onUnmounted } from 'vue'

export function usePolling(callback, interval = 5000) {
  const isPolling = ref(false)
  let timerId = null

  function start() {
    if (isPolling.value) return
    isPolling.value = true
    // Execute immediately
    callback()
    // Then start interval
    timerId = setInterval(() => {
      callback()
    }, interval)
  }

  function stop() {
    if (timerId) {
      clearInterval(timerId)
      timerId = null
    }
    isPolling.value = false
  }

  function restart(newInterval) {
    stop()
    if (newInterval) {
      interval = newInterval
    }
    start()
  }

  onUnmounted(() => {
    stop()
  })

  return {
    isPolling,
    start,
    stop,
    restart
  }
}
