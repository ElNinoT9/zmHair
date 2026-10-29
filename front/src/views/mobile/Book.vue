<template>
  <div class="book-page">
    <van-nav-bar title="预约理发" />

    <div class="book-content">
      <div class="card-block">
        <div class="label">选择理发师</div>
        <div class="barber-select">
          <div
            v-for="b in barbers"
            :key="b.id"
            class="barber-chip"
            :class="{ active: selectedBarber === b.id }"
            @click="selectBarber(b.id)"
          >
            {{ b.name }}
          </div>
        </div>
      </div>

      <div class="card-block" v-if="selectedBarber">
        <div class="label">选择预约日期</div>
        <van-empty v-if="!availableDates.length" description="该理发师暂无可预约日期" />
        <div class="date-grid">
          <div
            v-for="d in availableDates"
            :key="d.service_date"
            class="date-chip"
            :class="{ active: selectedDate === d.service_date }"
            @click="selectedDate = d.service_date"
          >
            <div class="date-day">{{ formatDay(d.service_date) }}</div>
            <div class="date-text">{{ formatDate(d.service_date) }}</div>
          </div>
        </div>
      </div>

      <div class="card-block">
        <van-field v-model="remark" label="备注" placeholder="选填，如有特殊需求请备注" />
      </div>

      <div class="submit-area">
        <van-button round block type="info" :loading="submitting" :disabled="!selectedBarber || !selectedDate" @click="handleSubmit">
          提交预约
        </van-button>
        <p class="submit-tip">提交后请等待理发师确认，具体时间线下沟通</p>
      </div>
    </div>
  </div>
</template>

<script>
import request from '@/utils/request'
import { Toast, Dialog } from 'vant'

export default {
  name: 'MobileBook',
  data() {
    return {
      barbers: [],
      availableDates: [],
      selectedBarber: null,
      selectedDate: '',
      remark: '',
      submitting: false
    }
  },
  created() {
    this.loadBarbers()
    if (this.$route.query.barber_id) {
      this.selectBarber(Number(this.$route.query.barber_id))
    }
  },
  methods: {
    async loadBarbers() {
      const res = await request.get('/mobile/barbers')
      this.barbers = res.data
    },
    async selectBarber(id) {
      this.selectedBarber = id
      this.selectedDate = ''
      const res = await request.get(`/mobile/barbers/${id}/dates`)
      this.availableDates = res.data
    },
    formatDay(dateStr) {
      const days = ['日', '一', '二', '三', '四', '五', '六']
      return '周' + days[new Date(dateStr).getDay()]
    },
    formatDate(dateStr) {
      const d = new Date(dateStr)
      return `${d.getMonth() + 1}月${d.getDate()}日`
    },
    handleSubmit() {
      Dialog.confirm({ title: '确认预约', message: `预约日期：${this.selectedDate}\n具体理发时间由理发师线下通知` }).then(async () => {
        this.submitting = true
        try {
          await request.post('/mobile/appointments', {
            barber_id: this.selectedBarber,
            appointment_date: this.selectedDate,
            remark: this.remark
          })
          Toast.success('预约成功')
          this.$router.push('/m/my')
        } finally {
          this.submitting = false
        }
      }).catch(() => {})
    }
  }
}
</script>

<style lang="scss" scoped>
.book-content { padding: 16px; }
.card-block {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.label { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: #303133; }

.barber-select, .date-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.barber-chip, .date-chip {
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid #DCDFE6;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  &.active {
    background: #409EFF;
    color: #fff;
    border-color: #409EFF;
  }
}

.date-chip {
  text-align: center;
  min-width: 72px;
  padding: 10px 12px;
  border-radius: 8px;
  .date-day { font-size: 12px; opacity: 0.8; }
  .date-text { font-size: 14px; font-weight: 500; margin-top: 2px; }
}

.submit-area {
  margin-top: 24px;
  padding: 0 8px;
  .submit-tip { text-align: center; color: #909399; font-size: 12px; margin-top: 12px; }
}
</style>
