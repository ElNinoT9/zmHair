<template>
  <div class="mobile-login">
    <div class="login-bg"></div>
    <div class="login-content">
      <div v-if="autoChecking" class="auto-login-box">
        <van-loading size="28px" color="#409EFF" />
        <p>正在自动登录...</p>
      </div>
      <template v-else>
        <div class="login-logo">
          <van-icon name="smile-o" size="48" color="#409EFF" />
          <h2>理发预约</h2>
          <p>输入工号即可使用，无需密码</p>
        </div>
        <van-form @submit="handleLogin">
          <van-field
            v-model="employeeId"
            type="digit"
            label="工号"
            placeholder="请输入纯数字工号"
            maxlength="10"
            clearable
            autofocus
            :rules="[{ required: true, message: '请输入工号' }]"
            @input="handleInput"
          />
          <div v-if="matchedName" class="name-preview">
            <van-icon name="contact" color="#67C23A" />
            <span>{{ matchedName }}</span>
          </div>
          <div style="margin:24px 16px">
            <van-button round block type="info" native-type="submit" :loading="loading">
              进入系统
            </van-button>
          </div>
        </van-form>
        <div class="login-tip">首次输入工号后会记住，下次打开自动登录</div>
      </template>
    </div>
  </div>
</template>

<script>
import request from '@/utils/request'
import { lookupEmployee } from '@/utils/auth'
import { Toast } from 'vant'

let lookupTimer = null

export default {
  name: 'MobileLogin',
  data() {
    return {
      loading: false,
      autoChecking: true,
      employeeId: '',
      matchedName: ''
    }
  },
    async created() {
    const ok = await this.$store.dispatch('autoLogin')
    if (ok) {
      this.$router.replace(this.$store.getters.isBarber ? '/m/barber' : '/m/book')
      return
    }
    this.autoChecking = false
    const saved = this.$store.getters.savedEmployeeId
    if (saved) {
      this.employeeId = saved
      this.lookupName(saved)
    }
  },
  methods: {
    handleInput() {
      this.matchedName = ''
      clearTimeout(lookupTimer)
      if (!this.employeeId || this.employeeId.length < 4) return
      lookupTimer = setTimeout(() => this.lookupName(this.employeeId), 300)
    },
    async lookupName(id) {
      try {
        const res = await lookupEmployee(id)
        if (res.data.code === 0 && res.data.data) {
          this.matchedName = res.data.data.name
        } else {
          this.matchedName = ''
        }
      } catch (e) {
        this.matchedName = ''
      }
    },
    async handleLogin() {
      this.loading = true
      try {
        const res = await request.post('/auth/quick-login', { employee_id: this.employeeId })
        if (res.data.user.role === 'admin') {
          Toast('管理员请使用 PC 后台登录')
          return
        }
        await this.$store.dispatch('login', { token: res.data.token, user: res.data.user })
        const target = res.data.user.is_barber ? '/m/barber' : '/m/book'
        this.$router.replace(target)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.mobile-login {
  min-height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(160deg, #e8f4fd 0%, #f0f2f5 50%, #e8f4fd 100%);
}

.login-content {
  position: relative;
  width: 90%;
  max-width: 400px;
  background: #fff;
  border-radius: 16px;
  padding: 32px 16px 24px;
  box-shadow: 0 8px 32px rgba(64, 158, 255, 0.12);
}

.auto-login-box {
  text-align: center;
  padding: 40px 0;
  p { margin-top: 16px; color: #909399; font-size: 14px; }
}

.login-logo {
  text-align: center;
  margin-bottom: 24px;
  h2 { font-size: 22px; margin: 12px 0 4px; color: #303133; }
  p { color: #909399; font-size: 13px; }
}

.name-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin: 8px 16px 0;
  padding: 10px;
  background: #f0f9eb;
  border-radius: 8px;
  color: #67C23A;
  font-size: 15px;
  font-weight: 500;
}

.login-tip {
  text-align: center;
  color: #C0C4CC;
  font-size: 12px;
  margin-top: 8px;
  line-height: 1.6;
}
</style>
