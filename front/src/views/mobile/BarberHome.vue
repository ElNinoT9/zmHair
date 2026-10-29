<template>
  <div class="barber-home">
    <div class="barber-hero">
      <div class="hero-title">理发师工作台</div>
      <div class="hero-sub">管理可服务日期，处理员工预约</div>
      <div class="hero-stats">
        <div class="stat-item" @click="$router.push('/m/barber/orders')">
          <div class="stat-num">{{ pendingCount }}</div>
          <div class="stat-label">待确认</div>
        </div>
        <div class="stat-divider" />
        <div class="stat-item" @click="$router.push('/m/barber/schedule')">
          <div class="stat-num">{{ scheduleCount }}</div>
          <div class="stat-label">已开放日期</div>
        </div>
        <div class="stat-divider" />
        <div class="stat-item" @click="$router.push('/m/notifications')">
          <div class="stat-num">{{ unreadCount }}</div>
          <div class="stat-label">未读消息</div>
        </div>
      </div>
    </div>

    <div class="section card-block">
      <div class="section-header">
        <span class="section-title">我的排班</span>
        <span class="section-link" @click="$router.push('/m/barber/schedule')">调整排班 ></span>
      </div>
      <van-empty v-if="!schedules.length" description="暂未设置可服务日期" />
      <div v-else class="date-tags">
        <van-tag v-for="s in schedules" :key="s.id" type="primary" plain size="medium">
          {{ formatDate(s.service_date) }}
        </van-tag>
      </div>
    </div>

    <div class="section card-block">
      <div class="section-header">
        <span class="section-title">当前预约单</span>
        <span class="section-link" @click="$router.push('/m/barber/orders')">查看全部 ></span>
      </div>
      <van-empty v-if="!recentOrders.length" description="暂无预约订单" />
      <div v-for="item in recentOrders" :key="item.id" class="order-preview">
        <div class="order-row">
          <span class="employee-name">{{ item.employee_name }}</span>
          <van-tag :type="statusTagType(item.status)" size="medium">{{ item.status_text }}</van-tag>
        </div>
        <div class="order-meta">预约日期：{{ item.appointment_date }}</div>
        <div class="order-meta" v-if="item.time_period_text">安排时段：{{ item.time_period_text }}</div>
        <div class="order-meta" v-if="item.remark">备注：{{ item.remark }}</div>
        <period-selector
          v-if="item.status === 'pending'"
          v-model="periodMap[item.id]"
          label="确认时段"
        />
        <div class="order-actions" v-if="item.status === 'pending'">
          <van-button size="mini" type="info" @click="confirmOrder(item)">确认</van-button>
          <van-button size="mini" plain type="danger" @click="updateStatus(item, 'cancelled')">拒绝</van-button>
        </div>
      </div>
    </div>

    <div class="tip-block">
      <van-notice-bar left-icon="info-o" text="确认预约请选择上午/下午/晚上，员工可在预约单中查看" />
    </div>
  </div>
</template>

<script>
import request from '@/utils/request'
import { Toast } from 'vant'
import PeriodSelector from '@/components/PeriodSelector.vue'
import { DEFAULT_PERIOD } from '@/utils/timePeriod'

export default {
  name: 'BarberHome',
  components: { PeriodSelector },
  data() {
    return {
      pendingCount: 0,
      unreadCount: 0,
      scheduleCount: 0,
      schedules: [],
      recentOrders: [],
      defaultPeriod: DEFAULT_PERIOD,
      periodMap: {}
    }
  },
  created() {
    this.loadDefaultPeriod().then(() => this.loadData())
  },
  activated() {
    this.loadData()
  },
  methods: {
    statusTagType(s) {
      return { pending: 'warning', confirmed: 'primary', completed: 'success', cancelled: 'default' }[s] || 'default'
    },
    formatDate(dateStr) {
      const d = new Date(dateStr)
      return `${d.getMonth() + 1}/${d.getDate()}`
    },
    async loadDefaultPeriod() {
      try {
        const res = await request.get('/mobile/barber/last-period')
        this.defaultPeriod = res.data.time_period || DEFAULT_PERIOD
      } catch (e) { /* ignore */ }
    },
    initPeriodMap() {
      const map = { ...this.periodMap }
      this.recentOrders.forEach(item => {
        if (item.status === 'pending' && !map[item.id]) {
          map[item.id] = this.defaultPeriod
        }
      })
      this.periodMap = map
    },
    async loadData() {
      const [schedulesRes, ordersRes, notifRes] = await Promise.all([
        request.get('/mobile/barber/schedules'),
        request.get('/mobile/barber/appointments'),
        request.get('/mobile/notifications')
      ])
      this.schedules = schedulesRes.data.slice(0, 8)
      this.scheduleCount = schedulesRes.data.length
      this.recentOrders = ordersRes.data.slice(0, 5)
      this.pendingCount = ordersRes.data.filter(o => o.status === 'pending').length
      this.unreadCount = notifRes.data.unread_count
      this.initPeriodMap()
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
.barber-hero {
  padding: 24px 20px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.hero-title {
  font-size: 22px;
  font-weight: 600;
}

.hero-sub {
  margin-top: 6px;
  font-size: 13px;
  opacity: 0.9;
}

.hero-stats {
  display: flex;
  align-items: center;
  justify-content: space-around;
  margin-top: 20px;
  padding: 16px 0;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
}

.stat-item {
  text-align: center;
  cursor: pointer;
  flex: 1;
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
}

.stat-label {
  font-size: 12px;
  margin-top: 4px;
  opacity: 0.9;
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: rgba(255, 255, 255, 0.3);
}

.section {
  margin: 12px 16px 0;
}

.card-block {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.section-link {
  font-size: 13px;
  color: #667eea;
  cursor: pointer;
}

.date-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.order-preview {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  &:last-child { border-bottom: none; }
}

.order-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.employee-name {
  font-size: 15px;
  font-weight: 600;
}

.order-meta {
  font-size: 13px;
  color: #606266;
  margin-bottom: 4px;
}

.order-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.tip-block {
  margin: 16px;
}
</style>
