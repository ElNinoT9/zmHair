<template>
  <div class="mobile-home">
    <div class="home-header">
      <div class="greeting">欢迎使用理发预约</div>
      <div class="sub">选择理发师和日期即可预约</div>
    </div>

    <div class="quick-actions">
      <div class="action-item" @click="$router.push('/m/book')">
        <van-icon name="calendar-o" size="28" color="#409EFF" />
        <span>预约理发</span>
      </div>
      <div class="action-item" @click="$router.push('/m/my')">
        <van-icon name="orders-o" size="28" color="#67C23A" />
        <span>我的预约</span>
      </div>
      <div class="action-item" @click="$router.push('/m/notifications')" v-if="unreadCount > 0">
        <van-badge :content="unreadCount">
          <van-icon name="bell" size="28" color="#E6A23C" />
        </van-badge>
        <span>消息</span>
      </div>
      <div class="action-item" @click="$router.push('/m/barber')" v-if="isBarber">
        <van-icon name="service-o" size="28" color="#F56C6C" />
        <span>理发师</span>
      </div>
    </div>

    <div class="section card-block">
      <div class="section-title">理发师列表</div>
      <van-empty v-if="!barbers.length" description="暂无理发师" />
      <div v-for="b in barbers" :key="b.id" class="barber-item" @click="goBook(b)">
        <div class="barber-avatar">{{ b.name.charAt(0) }}</div>
        <div class="barber-info">
          <div class="barber-name">{{ b.name }}</div>
          <div class="barber-id">工号：{{ b.employee_id }}</div>
        </div>
        <van-icon name="arrow" color="#C0C4CC" />
      </div>
    </div>

    <div class="tip-block">
      <van-notice-bar left-icon="info-o" text="预约仅登记日期，具体理发时间由理发师线下沟通确认" />
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import request from '@/utils/request'

export default {
  name: 'MobileHome',
  data() {
    return {
      barbers: [],
      unreadCount: 0
    }
  },
  computed: {
    ...mapState(['user']),
    ...mapGetters(['isBarber'])
  },
  created() {
    if (this.$store.getters.isLoggedIn) {
      this.loadBarbers()
      this.loadNotifications()
    }
  },
  methods: {
    async loadBarbers() {
      try {
        const res = await request.get('/mobile/barbers')
        this.barbers = res.data
      } catch (e) {
        if (!e.silent) throw e
      }
    },
    async loadNotifications() {
      try {
        const res = await request.get('/mobile/notifications')
        this.unreadCount = res.data.unread_count
      } catch (e) { /* ignore */ }
    },
    goBook(barber) {
      this.$router.push({ path: '/m/book', query: { barber_id: barber.id } })
    }
  }
}
</script>

<style lang="scss" scoped>
.home-header {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  padding: 32px 20px 48px;
  color: #fff;
  .greeting { font-size: 22px; font-weight: 600; }
  .sub { margin-top: 6px; opacity: 0.85; font-size: 13px; }
}

.quick-actions {
  display: flex;
  justify-content: space-around;
  margin: -28px 16px 16px;
  background: #fff;
  border-radius: 12px;
  padding: 20px 0;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  .action-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #606266;
    cursor: pointer;
  }
}

.section { margin: 0 16px; }
.card-block {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
}

.barber-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  &:last-child { border-bottom: none; }
}
.barber-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #ecf5ff;
  color: #409EFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  margin-right: 12px;
}
.barber-name { font-size: 15px; font-weight: 500; }
.barber-id { font-size: 12px; color: #909399; margin-top: 2px; }

.tip-block { margin: 16px; }
</style>
