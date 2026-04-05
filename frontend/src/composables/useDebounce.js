import { ref } from 'vue'

export function useDebounce(fn, delay = 300) {
  let timerId = null

  function debounced(...args) {
    if (timerId) {
      clearTimeout(timerId)
    }
    timerId = setTimeout(() => {
      fn(...args)
      timerId = null
    }, delay)
  }

  function cancel() {
    if (timerId) {
      clearTimeout(timerId)
      timerId = null
    }
  }

  return {
    debounced,
    cancel
  }
}
