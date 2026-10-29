<template>
  <div class="schedule-page">
    <van-nav-bar title="排班设置" />

    <div class="schedule-tip">
      <van-notice-bar left-icon="info-o" :text="`请选择未来 ${minDays}~${maxDays} 天内可服务的日期`" />
    </div>

    <div class="calendar-area">
      <van-calendar
        :poppable="false"
        :show-confirm="false"
        :min-date="minDate"
        :max-date="maxDate"
        type="multiple"
        :default-date="selectedDates"
        @select="onSelect"
        color="#409EFF"
      />
    </div>

    <div class="selected-info" v-if="selectedDates.length">
      已选 {{ selectedDates.length }} 天
    </div>

    <div class="submit-area">
      <van-button round block type="info" :loading="saving" @click="handleSave">保存排班</van-button>
    </div>
  </div>
</template>

<script>
import request from '@/utils/request'
import { Toast } from 'vant'

export default {
  name: 'BarberSchedule',
  data() {
    return {
      minDays: 7,
      maxDays: 14,
      minDate: new Date(),
      maxDate: new Date(),
      selectedDates: [],
      saving: false
    }
  },
  async created() {
    await this.loadConfig()
    await this.loadSchedules()
  },
  methods: {
    async loadConfig() {
      const res = await request.get('/mobile/config/public')
      this.minDays = parseInt(res.data.schedule_min_days || 7)
      this.maxDays = parseInt(res.data.schedule_max_days || 14)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      this.minDate = new Date(today.getTime() + 86400000)
      this.maxDate = new Date(today.getTime() + this.maxDays * 86400000)
    },
    async loadSchedules() {
      const res = await request.get('/mobile/barber/schedules')
      this.selectedDates = res.data.map(s => new Date(s.service_date))
    },
    onSelect(dates) {
      this.selectedDates = dates
    },
    async handleSave() {
      this.saving = true
      try {
        const dates = this.selectedDates.map(d => {
          const y = d.getFullYear()
          const m = String(d.getMonth() + 1).padStart(2, '0')
          const day = String(d.getDate()).padStart(2, '0')
          return `${y}-${m}-${day}`
        })
        await request.post('/mobile/barber/schedules', { dates })
        Toast.success('排班已保存')
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.schedule-tip { margin: 12px 16px 0; }
.calendar-area {
  margin: 12px 16px;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.selected-info {
  text-align: center;
  color: #409EFF;
  font-size: 14px;
  margin: 12px 0;
}
.submit-area { padding: 16px 24px; }
</style>
