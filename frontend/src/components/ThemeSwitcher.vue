<template>
  <div class="relative" ref="dropdownRef">
    <!-- Trigger Button -->
    <button
      @click="isOpen = !isOpen"
      class="flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200"
      :style="isOpen
        ? { backgroundColor: 'var(--color-primary-subtle)', color: 'var(--color-primary)' }
        : { color: 'var(--text-muted)' }"
      :class="!isOpen && 'hover:bg-hover'"
      title="切换主题"
    >
      <component :is="currentTheme.icon" class="w-5 h-5" />
      <span class="text-sm font-medium hidden sm:inline">{{ currentTheme.label }}</span>
      <ChevronDownIcon class="w-4 h-4 transition-transform" :class="{ 'rotate-180': isOpen }" />
    </button>

    <!-- Dropdown -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 scale-95 -translate-y-1"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 -translate-y-1"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 mt-2 w-72 rounded-xl overflow-hidden z-50"
        :style="{
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-soft)'
        }"
      >
        <!-- Header -->
        <div class="px-4 py-3" :style="{ borderBottom: '1px solid var(--border-subtle)' }">
          <p class="text-sm font-medium" :style="{ color: 'var(--text-main)' }">选择主题</p>
          <p class="text-xs mt-0.5" :style="{ color: 'var(--text-muted)' }">IDE 级专业配色</p>
        </div>

        <!-- Theme Options -->
        <div class="p-2 space-y-1">
          <button
            v-for="theme in themes"
            :key="theme.id"
            @click="selectTheme(theme.id)"
            class="w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200"
            :style="currentThemeId === theme.id
              ? { backgroundColor: 'var(--color-primary-subtle)' }
              : {}"
          >
            <!-- Theme Preview Palette -->
            <div class="flex flex-col gap-1 flex-shrink-0">
              <div class="flex items-center gap-1">
                <div
                  v-for="(color, i) in theme.colors.bg"
                  :key="'bg-' + i"
                  class="w-5 h-5 rounded-sm border border-black/10"
                  :style="{ backgroundColor: color }"
                ></div>
              </div>
              <div class="flex items-center gap-1">
                <div
                  v-for="(color, i) in theme.colors.accent"
                  :key="'accent-' + i"
                  class="w-5 h-5 rounded-sm border border-black/10"
                  :style="{ backgroundColor: color }"
                ></div>
              </div>
            </div>

            <!-- Theme Info -->
            <div class="flex-1 text-left">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium" :style="{ color: 'var(--text-main)' }">
                  {{ theme.label }}
                </span>
                <span
                  v-if="theme.badge"
                  class="text-[10px] px-1.5 py-0.5 rounded-full font-medium"
                  :style="{
                    backgroundColor: 'var(--color-primary-subtle)',
                    color: 'var(--color-primary)'
                  }"
                >
                  {{ theme.badge }}
                </span>
              </div>
              <p class="text-xs mt-0.5" :style="{ color: 'var(--text-muted)' }">
                {{ theme.description }}
              </p>
            </div>

            <!-- Selected Indicator -->
            <div
              v-if="currentThemeId === theme.id"
              class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0"
              :style="{ backgroundColor: 'var(--color-primary)' }"
            >
              <CheckIcon class="w-3.5 h-3.5 text-white" />
            </div>
          </button>
        </div>

        <!-- Footer hint -->
        <div
          class="px-4 py-2.5 text-xs"
          :style="{ borderTop: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }"
        >
          主题选择已自动保存 · 刷新后生效
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, markRaw } from 'vue'
import {
  ChevronDownIcon,
  CheckIcon,
  MoonIcon,
  SparklesIcon,
  SunIcon,
  CodeBracketIcon
} from '@heroicons/vue/24/outline'

const emit = defineEmits(['change'])

const isOpen = ref(false)
const dropdownRef = ref(null)
const currentThemeId = ref('darcula')

const themes = [
  {
    id: 'darcula',
    label: 'JetBrains Darcula',
    description: 'IDEA 经典暗色，长时间编码最护眼',
    badge: '推荐',
    icon: markRaw(MoonIcon),
    isDark: true,
    colors: {
      bg: ['#2B2B2B', '#3C3F41', '#4C5052'],
      accent: ['#3592C4', '#67965A', '#E43F3F']
    }
  },
  {
    id: 'onedark',
    label: 'One Dark Pro',
    description: 'VS Code 最受欢迎，深邃蓝黑',
    badge: null,
    icon: markRaw(SparklesIcon),
    isDark: true,
    colors: {
      bg: ['#282C34', '#21252B', '#2C313A'],
      accent: ['#61AFEF', '#98C379', '#E06C75']
    }
  },
  {
    id: 'gruvbox',
    label: 'Gruvbox Material',
    description: '复古琥珀暖色调，极致护眼',
    badge: null,
    icon: markRaw(SunIcon),
    isDark: true,
    colors: {
      bg: ['#282828', '#32302F', '#3C3836'],
      accent: ['#D65D0E', '#98971A', '#CC241D']
    }
  },
  {
    id: 'intellij',
    label: 'IntelliJ Light',
    description: 'IDEA 经典亮色，干净高对比',
    badge: null,
    icon: markRaw(CodeBracketIcon),
    isDark: false,
    colors: {
      bg: ['#F2F2F2', '#FFFFFF', '#E6E6E6'],
      accent: ['#3592C4', '#488B49', '#D04438']
    }
  }
]

const currentTheme = computed(() => themes.find(t => t.id === currentThemeId.value) || themes[0])

function selectTheme(themeId) {
  currentThemeId.value = themeId
  applyTheme(themeId)
  localStorage.setItem('pycron-theme', themeId)
  emit('change', themeId)
  isOpen.value = false
}

function applyTheme(themeId) {
  document.documentElement.setAttribute('data-theme', themeId)
  // Element Plus dark mode - add/remove 'dark' class based on theme
  const theme = themes.find(t => t.id === themeId)
  if (theme && theme.isDark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

// Close dropdown when clicking outside
function handleClickOutside(event) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

// Load saved theme on mount
onMounted(() => {
  const savedTheme = localStorage.getItem('pycron-theme')
  if (savedTheme && themes.some(t => t.id === savedTheme)) {
    currentThemeId.value = savedTheme
    applyTheme(savedTheme)
  } else {
    // Default to darcula
    applyTheme('darcula')
  }
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
