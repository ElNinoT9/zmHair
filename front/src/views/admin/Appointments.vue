<template>
  <div class="appointments-page">
    <div class="card toolbar">
      <el-form inline @submit.native.prevent="loadData">
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="搜索预约人" clearable style="width:160px" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="query.status" placeholder="状态" clearable style="width:120px">
            <el-option label="待确认" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="yyyy-MM-dd" style="width:260px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="loadData">查询</el-button>
          <el-button type="success" icon="el-icon-download" @click="handleExport">导出 Excel</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="card">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="employee_no" label="预约人工号" width="120" />
        <el-table-column prop="employee_name" label="预约人" width="100" />
        <el-table-column prop="barber_name" label="理发师" width="100" />
        <el-table-column prop="appointment_date" label="预约日期" width="120" />
        <el-table-column prop="time_period_text" label="安排时段" width="90" />
        <el-table-column prop="status_text" label="状态" width="90">
          <template slot-scope="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="170" />
      </el-table>
      <el-pagination
        style="margin-top:16px;text-align:right"
        @current-change="p => { query.page = p; loadData() }"
        :current-page="query.page"
        :page-size="query.page_size"
        :total="total"
        layout="total, prev, pager, next"
      />
    </div>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'Appointments',
  data() {
    return {
      loading: false,
      list: [],
      total: 0,
      dateRange: null,
      query: { keyword: '', status: '', page: 1, page_size: 20 }
    }
  },
  created() { this.loadData() },
  methods: {
    statusType(s) {
      return { pending: 'warning', confirmed: '', completed: 'success', cancelled: 'info' }[s] || 'info'
    },
    async loadData() {
      this.loading = true
      const params = { ...this.query }
      if (this.dateRange) {
        params.start_date = this.dateRange[0]
        params.end_date = this.dateRange[1]
      }
      try {
        const res = await request.get('/admin/appointments', { params })
        this.list = res.data.list
        this.total = res.data.total
      } finally {
        this.loading = false
      }
    },
    async handleExport() {
      const params = { status: this.query.status }
      if (this.dateRange) {
        params.start_date = this.dateRange[0]
        params.end_date = this.dateRange[1]
      }
      const res = await request.get('/admin/appointments/export', { params, responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.download = `预约台账_${new Date().toISOString().slice(0,10)}.xlsx`
      link.click()
      window.URL.revokeObjectURL(url)
      this.$message.success('导出成功')
    }
  }
}
</script>

<style scoped>
.toolbar { margin-bottom: 16px; }
</style>
