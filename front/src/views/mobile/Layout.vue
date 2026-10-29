<template>
  <div class="mobile-layout">
    <div class="mobile-topbar" v-if="user" :class="{ 'barber-topbar': isBarber }">
      <div class="topbar-user">
        <span class="topbar-name">
          {{ user.name }}
          <van-tag v-if="isBarber" type="primary" size="medium" class="role-tag">理发师</van-tag>
        </span>
        <span class="topbar-id">工号 {{ user.employee_id }}</span>
      </div>
      <van-button
        size="small"
        round
        plain
        type="danger"
        icon="exchange"
        class="switch-btn"
        @click="handleSwitchUser"
      >
        切换用户
      </van-button>
    </div>

    <div class="mobile-body" :class="{ 'has-topbar': !!user }">
      <router-view />
    </div>

    <!-- 理发师底部导航 -->
    <van-tabbar v-model="active" route v-if="showTabbar && isBarber">
      <van-tabbar-item to="/m/barber" icon="service-o">工作台</van-tabbar-item>
      <van-tabbar-item to="/m/barber/schedule" icon="calendar-o">排班</van-tabbar-item>
      <van-tabbar-item to="/m/barber/orders" icon="orders-o" :badge="pendingBadge">预约单</van-tabbar-item>
      <van-tabbar-item to="/m/book" icon="add-o">预约理发</van-tabbar-item>
      <van-tabbar-item to="/m/my" icon="notes-o">我的预约</van-tabbar-item>
    </van-tabbar>

    <!-- 普通员工底部导航 -->
    <van-tabbar v-model="active" route v-else-if="showTabbar">
      <van-tabbar-item to="/m/book" icon="calendar-o">预约理发</van-tabbar-item>
      <van-tabbar-item to="/m/my" icon="orders-o">我的预约</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex'
import { Dialog } from 'vant'
import request from '@/utils/request'

export default {
  name: 'MobileLayout',
  data() {
    return {
      active: 0,
      pendingCount: 0
    }
  },
  computed: {
    ...mapState(['user']),
    ...mapGetters(['isBarber']),
    pendingBadge() {
      return this.pendingCount > 0 ? String(this.pendingCount) : ''
    },
    showTabbar() {
      return !this.$route.path.includes('/notifications')
    }
  },
  watch: {
    isBarber: {
      immediate: true,
      handler(val) {
        if (val) this.loadPendingCount()
      }
    }
  },
  mounted() {
    this.refreshProfile()
  },
  methods: {
    async refreshProfile() {
      if (!this.$store.getters.isLoggedIn) return
      try {
        const res = await request.get('/auth/profile')
        const user = res.data
        await this.$store.dispatch('login', {
          token: this.$store.state.token,
          user
        })
      } catch (e) { /* ignore */ }
    },
    async loadPendingCount() {
      try {
        const res = await request.get('/mobile/barber/appointments', { params: { status: 'pending' } })
        this.pendingCount = res.data.length
      } catch (e) { /* ignore */ }
    },
    handleSwitchUser() {
      Dialog.confirm({
        title: '切换用户',
        message: '退出当前账号，以便其他人输入工号预约',
        confirmButtonText: '切换用户',
        confirmButtonColor: '#F56C6C'
      }).then(() => {
        this.$store.dispatch('logout')
        this.$router.replace('/m/login')
      }).catch(() => {})
    }
  }
}
</script>

<style lang="scss" scoped>
.mobile-layout {
  min-height: 100vh;
  padding-bottom: 50px;
  background: #f5f7fa;
}

.mobile-topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  &.barber-topbar {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-bottom: none;
    .topbar-name, .topbar-id { color: #fff; }
    .role-tag { margin-left: 6px; vertical-align: middle; }
  }
}

.topbar-user {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.topbar-id {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.switch-btn {
  flex-shrink: 0;
  font-weight: 500;
}

.mobile-body.has-topbar {
  min-height: calc(100vh - 50px - 54px);
}
</style>
