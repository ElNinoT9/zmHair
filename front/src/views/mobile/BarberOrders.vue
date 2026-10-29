<template>
  <div class="orders-page">
    <van-nav-bar title="预约订单" />

    <van-tabs v-model="activeTab" @change="loadData" sticky>
      <van-tab title="待确认" name="pending" />
      <van-tab title="已确认" name="confirmed" />
      <van-tab title="全部" name="" />
    </van-tabs>

    <van-pull-refresh v-model="refreshing" @refresh="loadData">
      <van-empty v-if="!list.length && !loading" description="暂无预约订单" />
      <div v-for="item in list" :key="item.id" class="order-card">
        <div class="order-header">
          <span class="employee-name">{{ item.employee_name }}</span>
          <van-tag :type="statusTagType(item.status)" size="medium">{{ item.status_text }}</van-tag>
        </div>
        <div class="order-body">
          <div class="order-row">工号：{{ item.employee_no }}</div>
          <div class="order-row">预约日期：{{ item.appointment_date }}</div>
          <div class="order-row" v-if="item.time_period_text">安排时段：{{ item.time_period_text }}</div>
          <div class="order-row" v-if="item.remark">备注：{{ item.remark }}</div>
          <div class="order-row">提交时间：{{ item.created_at }}</div>
        </div>
        <period-selector
          v-if="item.status === 'pending'"
          v-model="periodMap[item.id]"
          label="确认时段"
        />
        <div class="order-actions" v-if="item.status === 'pending'">
          <van-button size="small" type="info" @click="confirmOrder(item)">确认</van-button>
          <van-button size="small" plain type="danger" @click="updateStatus(item, 'cancelled')">拒绝</van-button>
        </div>
        <div class="order-actions" v-if="item.status === 'confirmed'">
          <van-button size="small" type="primary" @click="updateStatus(item, 'completed')">标记完成</van-button>
        </div>
      </div>
    </van-pull-refresh>
  </div>
</template>

<script>
import request from '@/utils/request'
import { Toast } from 'vant'
import PeriodSelector from '@/components/PeriodSelector.vue'
import { DEFAULT_PERIOD } from '@/utils/timePeriod'

export default {
  name: 'BarberOrders',
  components: { PeriodSelector },
  data() {
    return {
      activeTab: 'pending',
      list: [],
      loading: false,
      refreshing: false,
      defaultPeriod: DEFAULT_PERIOD,
      periodMap: {}
    }
  },
  created() {
    this.loadDefaultPeriod().then(() => this.loadData())
  },
  methods: {
    statusTagType(s) {
      return { pending: 'warning', confirmed: 'primary', completed: 'success', cancelled: 'default' }[s] || 'default'
    },
    async loadDefaultPeriod() {
      try {
        const res = await request.get('/mobile/barber/last-period')
        this.defaultPeriod = res.data.time_period || DEFAULT_PERIOD
      } catch (e) { /* ignore */ }
    },
    initPeriodMap() {
      const map = { ...this.periodMap }
      this.list.forEach(item => {
        if (item.status === 'pending' && !map[item.id]) {
          map[item.id] = this.defaultPeriod
        }
      })
      this.periodMap = map
    },
    async loadData() {
      this.loading = true
      try {
        const params = {}
        if (this.activeTab) params.status = this.activeTab
        const res = await request.get('/mobile/barber/appointments', { params })
        this.list = res.data
        this.initPeriodMap()
      } finally {
        this.loading = false
        this.refreshing = false
      }
    },
    async confirmOrder(item) {
      const period = this.periodMap[item.id] || this.defaultPeriod
      await request.put(`/mobile/barber/appointments/${item.id}/status`, {
        status: 'confirmed',
        time_period: period
      })
      this.defaultPeriod = period
      Toast.success('已确认预约')
      this.loadData()
    },
    async updateStatus(item, status) {
      await request.put(`/mobile/barber/appointments/${item.id}/status`, { status })
      Toast.success('状态已更新')
      this.loadData()
    }
  }
}
</script>

<style lang="scss" scoped>
.order-card {
  margin: 12px 16px;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  .employee-name { font-size: 16px; font-weight: 600; }
}

.order-body {
  .order-row { font-size: 13px; color: #606266; margin-bottom: 4px; }
}

.order-actions {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
