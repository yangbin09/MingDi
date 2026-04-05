<template>
  <el-card shadow="never" class="stats-card">
    <div class="stats-content">
      <div class="stats-icon" :style="{ backgroundColor: iconBgColor }">
        <el-icon :size="24" :color="iconColor">
          <component :is="icon" />
        </el-icon>
      </div>
      <div class="stats-info">
        <div class="stats-label">{{ label }}</div>
        <div class="stats-value" :style="{ color: valueColor }">{{ value }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  value: [String, Number],
  icon: Object,
  iconBgColor: {
    type: String,
    default: 'var(--color-primary-subtle)'
  },
  iconColor: {
    type: String,
    default: 'var(--color-primary)'
  },
  valueColor: {
    type: String,
    default: 'var(--text-main)'
  }
})
</script>

<style scoped>
.stats-card {
  height: 100%;
}

.stats-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stats-info {
  flex: 1;
  min-width: 0;
}

.stats-label {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.stats-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}
</style>
