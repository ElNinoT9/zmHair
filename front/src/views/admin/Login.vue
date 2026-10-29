<template>
  <div class="admin-login">
    <div class="login-card">
      <div class="login-header">
        <h2>理发预约管理系统</h2>
        <p>管理后台</p>
      </div>
      <el-form ref="form" :model="form" :rules="rules" @submit.native.prevent="handleLogin">
        <el-form-item prop="employee_id">
          <el-input v-model="form.employee_id" prefix-icon="el-icon-user" placeholder="请输入工号" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" prefix-icon="el-icon-lock" type="password" placeholder="请输入密码" show-password @keyup.enter.native="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width:100%" @click="handleLogin">登 录</el-button>
        </el-form-item>
      </el-form>
      <div class="login-tip">默认管理员：admin / admin123</div>
    </div>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'AdminLogin',
  data() {
    return {
      loading: false,
      form: { employee_id: '', password: '' },
      rules: {
        employee_id: [{ required: true, message: '请输入工号', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
      }
    }
  },
  methods: {
    handleLogin() {
      this.$refs.form.validate(async valid => {
        if (!valid) return
        this.loading = true
        try {
          const res = await request.post('/auth/login', this.form)
          if (res.data.user.role !== 'admin') {
            this.$message.warning('您没有管理后台权限')
            return
          }
          await this.$store.dispatch('login', { token: res.data.token, user: res.data.user })
          this.$router.push('/admin/dashboard')
        } finally {
          this.loading = false
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.admin-login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
  h2 { font-size: 22px; color: #303133; margin-bottom: 8px; }
  p { color: #909399; font-size: 14px; }
}

.login-tip {
  text-align: center;
  color: #C0C4CC;
  font-size: 12px;
  margin-top: 16px;
}
</style>
