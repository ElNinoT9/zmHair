<template>
  <div class="mobile-layout">
    <div class="mobile-topbar" v-if="user" :class="{ 'barber-topbar': isBarber }">
      <div class="topbar-identity">
        <span class="topbar-name">{{ user.name }}</span>
        <span class="topbar-dot">·</span>
        <span class="topbar-id">{{ user.employee_id }}</span>
      </div>
      <div class="topbar-actions">
        <div v-if="isBarberCapable" class="role-switch">
          <button
            type="button"
            class="role-pill"
            :class="{ active: !isBarber }"
            @click="switchViewMode('employee')"
          >
            员工
          </button>
          <button
            type="button"
            class="role-pill"
            :class="{ active: isBarber }"
            @click="switchViewMode('barber')"
          >
            理发师
          </button>
        </div>
        <button type="button" class="switch-user-btn" @click="handleSwitchUser">换人</button>
      </div>
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
    ...mapGetters(['isBarber', 'isBarberCapable', 'defaultMobileRoute']),
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
        const wasBarberMode = this.isBarber
        await this.$store.dispatch('login', {
          token: this.$store.state.token,
          user
        })
        if (wasBarberMode && !this.isBarberCapable) {
          this.$router.replace('/m/book')
        }
      } catch (e) { /* ignore */ }
    },
    async loadPendingCount() {
      try {
        const res = await request.get('/mobile/barber/appointments', { params: { status: 'pending' } })
        this.pendingCount = res.data.length
      } catch (e) { /* ignore */ }
    },
    switchViewMode(mode) {
      if (mode === 'barber' && !this.isBarberCapable) return
      const goingBarber = mode === 'barber'
      if (goingBarber === this.isBarber) return
      this.$store.dispatch('setMobileViewMode', mode)
      const target = goingBarber ? '/m/barber' : '/m/book'
      if (this.$route.path !== target) {
        this.$router.replace(target)
      }
      if (goingBarber) this.loadPendingCount()
    },
    handleSwitchUser() {
      Dialog.confirm({
        title: '换人登录',
        message: '退出当前账号，以便其他人输入工号',
        confirmButtonText: '换人',
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
  gap: 10px;
  padding: 8px 12px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  &.barber-topbar {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-bottom: none;
    .topbar-name,
    .topbar-id,
    .topbar-dot { color: #fff; }
    .topbar-id { opacity: 0.88; }
    .topbar-dot { opacity: 0.7; }
    .role-switch {
      background: rgba(0, 0, 0, 0.22);
    }
    .role-pill {
      color: rgba(255, 255, 255, 0.95);
      font-weight: 500;
      &.active {
        background: #fff;
        color: #5b6fd8;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
      }
    }
    .switch-user-btn {
      color: #fff;
      border-color: rgba(255, 255, 255, 0.55);
      background: rgba(255, 255, 255, 0.12);
    }
  }
}

.topbar-identity {
  display: flex;
  align-items: baseline;
  gap: 4px;
  min-width: 0;
  flex: 1;
}

.topbar-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.topbar-dot {
  font-size: 12px;
  color: #c0c4cc;
  flex-shrink: 0;
}

.topbar-id {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  flex-shrink: 0;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.role-switch {
  display: inline-flex;
  padding: 2px;
  background: #f0f2f5;
  border-radius: 14px;
  gap: 2px;
}

.role-pill {
  border: none;
  padding: 3px 12px;
  font-size: 12px;
  line-height: 18px;
  border-radius: 12px;
  color: #606266;
  background: transparent;
  cursor: pointer;
  transition: all 0.15s;
  &.active {
    background: #fff;
    color: #409eff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }
}

.switch-user-btn {
  border: 1px solid #f56c6c;
  color: #f56c6c;
  background: #fff;
  font-size: 12px;
  line-height: 1;
  padding: 5px 10px;
  border-radius: 14px;
  cursor: pointer;
  white-space: nowrap;
}

.mobile-body.has-topbar {
  min-height: calc(100vh - 50px - 44px);
}
</style>
