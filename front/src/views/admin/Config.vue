<template>
  <div class="config-page">
    <div class="card">
      <h3 style="margin-bottom:20px">系统基础参数配置</h3>
      <el-form ref="form" :model="form" label-width="180px" v-loading="loading">
        <el-form-item v-for="item in configs" :key="item.config_key" :label="item.description || item.config_key">
          <el-input v-model="item.config_value" style="width:400px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存配置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'Config',
  data() {
    return {
      loading: false,
      saving: false,
      configs: [],
      form: {}
    }
  },
  created() { this.loadConfig() },
  methods: {
    async loadConfig() {
      this.loading = true
      try {
        const res = await request.get('/admin/config')
        this.configs = res.data
      } finally {
        this.loading = false
      }
    },
    async handleSave() {
      this.saving = true
      try {
        await request.put('/admin/config', { configs: this.configs })
        this.$message.success('配置已保存')
      } finally {
        this.saving = false
      }
    }
  }
}
</script>
