<template>
  <div class="my-page">
    <van-nav-bar title="我的预约" />

    <van-pull-refresh v-model="refreshing" @refresh="loadData">
      <van-empty v-if="!list.length && !loading" description="暂无预约记录" />
      <div v-for="item in list" :key="item.id" class="apt-card">
        <div class="apt-header">
          <span class="apt-barber">{{ item.barber_name }}</span>
          <van-tag :type="statusTagType(item.status)" size="medium">{{ item.status_text }}</van-tag>
        </div>
        <div class="apt-body">
          <div class="apt-row"><van-icon name="calendar-o" /> 预约日期：{{ item.appointment_date }}</div>
          <div class="apt-row" v-if="item.time_period_text">
            <van-icon name="clock-o" /> 安排时段：{{ item.time_period_text }}
          </div>
          <div class="apt-row" v-else-if="item.status === 'pending'">
            <van-icon name="clock-o" /> 时段：待理发师确认
          </div>
          <div class="apt-row" v-if="item.remark"><van-icon name="comment-o" /> 备注：{{ item.remark }}</div>
          <div class="apt-row"><van-icon name="clock-o" /> 提交时间：{{ item.created_at }}</div>
        </div>
        <div class="apt-footer" v-if="item.status === 'pending' || item.status === 'confirmed'">
          <van-button size="small" plain type="danger" @click="handleCancel(item)">取消预约</van-button>
        </div>
      </div>
    </van-pull-refresh>
  </div>
</template>

<script>
import request from '@/utils/request'
import { Dialog, Toast } from 'vant'

export default {
  name: 'MyAppointments',
  data() {
    return {
      list: [],
      loading: false,
      refreshing: false
    }
  },
  created() { this.loadData() },
  methods: {
    statusTagType(s) {
      return { pending: 'warning', confirmed: 'primary', completed: 'success', cancelled: 'default' }[s] || 'default'
    },
    async loadData() {
      this.loading = true
      try {
        const res = await request.get('/mobile/my-appointments')
        this.list = res.data
      } finally {
        this.loading = false
        this.refreshing = false
      }
    },
    handleCancel(item) {
      Dialog.confirm({ title: '取消预约', message: `确定取消 ${item.appointment_date} 的预约？` }).then(async () => {
        await request.post(`/mobile/my-appointments/${item.id}/cancel`)
        Toast.success('已取消')
        this.loadData()
      }).catch(() => {})
    }
  }
}
</script>

<style lang="scss" scoped>
.my-page { padding-bottom: 16px; }

.apt-card {
  margin: 12px 16px;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.apt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  .apt-barber { font-size: 16px; font-weight: 600; }
}

.apt-body {
  .apt-row {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #606266;
    margin-bottom: 6px;
  }
}

.apt-footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  text-align: right;
}
</style>
