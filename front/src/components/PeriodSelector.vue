<template>
  <div class="period-select">
    <span class="period-label">{{ label }}</span>
    <div class="period-chips">
      <div
        v-for="p in options"
        :key="p.value"
        class="period-chip"
        :class="{ active: value === p.value }"
        @click="$emit('input', p.value)"
      >
        {{ p.label }}
      </div>
    </div>
  </div>
</template>

<script>
import { PERIOD_OPTIONS } from '@/utils/timePeriod'

export default {
  name: 'PeriodSelector',
  props: {
    value: { type: String, default: 'morning' },
    label: { type: String, default: '安排时段' }
  },
  data() {
    return { options: PERIOD_OPTIONS }
  }
}
</script>

<style lang="scss" scoped>
.period-select {
  margin-top: 10px;
}

.period-label {
  display: block;
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.period-chips {
  display: flex;
  gap: 8px;
}

.period-chip {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s;

  &.active {
    background: #409eff;
    border-color: #409eff;
    color: #fff;
    font-weight: 500;
  }
}
</style>
