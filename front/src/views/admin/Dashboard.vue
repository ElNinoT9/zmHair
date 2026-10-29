<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6" v-for="item in statCards" :key="item.key">
        <div class="stat-card" :style="{ borderTop: `3px solid ${item.color}` }">
          <div class="stat-value">{{ stats[item.key] || 0 }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </div>
      </el-col>
    </el-row>
    <div class="card welcome-card">
      <h3>欢迎使用企业内部理发预约管理系统</h3>
      <p>您可以在此管理员工账号、查看预约台账、导出报表及配置系统参数。</p>
      <el-row :gutter="16" style="margin-top:20px">
        <el-col :span="8"><el-button type="primary" plain icon="el-icon-user" @click="$router.push('/admin/users')">用户管理</el-button></el-col>
        <el-col :span="8"><el-button type="success" plain icon="el-icon-document" @click="$router.push('/admin/appointments')">预约台账</el-button></el-col>
        <el-col :span="8"><el-button type="warning" plain icon="el-icon-setting" @click="$router.push('/admin/config')">系统配置</el-button></el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {},
      statCards: [
        { key: 'total_users', label: '在职员工', color: '#409EFF' },
        { key: 'total_barbers', label: '理发师', color: '#67C23A' },
        { key: 'total_appointments', label: '预约总数', color: '#E6A23C' },
        { key: 'today_appointments', label: '今日预约', color: '#F56C6C' }
      ]
    }
  },
  created() {
    this.loadStats()
  },
  methods: {
    async loadStats() {
      const res = await request.get('/admin/dashboard')
      this.stats = res.data
    }
  }
}
</script>

<style lang="scss" scoped>
.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  margin-bottom: 20px;
  .stat-value { font-size: 32px; font-weight: 600; color: #303133; }
  .stat-label { color: #909399; margin-top: 8px; font-size: 14px; }
}

.welcome-card {
  h3 { margin-bottom: 12px; color: #303133; }
  p { color: #606266; line-height: 1.6; }
}
</style>
