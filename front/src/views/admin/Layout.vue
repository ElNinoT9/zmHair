<template>
  <el-container class="admin-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <i class="el-icon-scissors"></i>
        <span>理发预约系统</span>
      </div>
      <el-menu :default-active="$route.path" router background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF">
        <el-menu-item index="/admin/dashboard"><i class="el-icon-s-home"></i><span>工作台</span></el-menu-item>
        <el-menu-item index="/admin/users"><i class="el-icon-user"></i><span>用户管理</span></el-menu-item>
        <el-menu-item index="/admin/appointments"><i class="el-icon-document"></i><span>预约台账</span></el-menu-item>
        <el-menu-item index="/admin/config"><i class="el-icon-setting"></i><span>系统配置</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span class="page-title">{{ $route.meta.title }}</span>
        <div class="header-right">
          <span class="user-name">{{ user.name }}（{{ user.employee_id }}）</span>
          <el-button type="text" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'AdminLayout',
  computed: {
    ...mapState(['user'])
  },
  methods: {
    handleLogout() {
      this.$confirm('确定退出登录？', '提示').then(() => {
        this.$store.dispatch('logout')
        this.$router.push('/admin/login')
      }).catch(() => {})
    }
  }
}
</script>

<style lang="scss" scoped>
.admin-layout { height: 100vh; }

.sidebar {
  background: #304156;
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 16px;
    font-weight: 600;
    i { margin-right: 8px; font-size: 20px; }
  }
}

.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  .page-title { font-size: 18px; font-weight: 500; }
  .user-name { margin-right: 16px; color: #606266; font-size: 14px; }
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
}
</style>
