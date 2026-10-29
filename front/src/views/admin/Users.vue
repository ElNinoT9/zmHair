<template>
  <div class="users-page">
    <div class="card toolbar">
      <el-form inline @submit.native.prevent="loadData">
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="搜索工号/姓名" clearable style="width:200px" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="query.role" placeholder="角色" clearable style="width:120px">
            <el-option label="管理员" value="admin" />
            <el-option label="员工" value="employee" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="loadData">查询</el-button>
          <el-button type="success" icon="el-icon-plus" @click="openDialog()">新增用户</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="card">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="employee_id" label="工号" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="role" label="角色" width="100">
          <template slot-scope="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
              {{ row.role === 'admin' ? '管理员' : '员工' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_barber" label="理发师" width="80">
          <template slot-scope="{ row }">
            <el-tag :type="row.is_barber ? 'success' : 'info'" size="small">{{ row.is_barber ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template slot-scope="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '正常' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="160" fixed="right">
          <template slot-scope="{ row }">
            <el-button type="text" @click="openDialog(row)">编辑</el-button>
            <el-button type="text" style="color:#F56C6C" @click="handleDelete(row)" v-if="row.role !== 'admin'">停用</el-button>
          </template>
        </el-table-column>
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

    <el-dialog :title="editForm.id ? '编辑用户' : '新增用户'" :visible.sync="dialogVisible" width="480px">
      <el-form ref="editForm" :model="editForm" :rules="editRules" label-width="80px">
        <el-form-item label="工号" prop="employee_id">
          <el-input v-model="editForm.employee_id" :disabled="!!editForm.id" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="editForm.role" style="width:100%">
            <el-option label="员工" value="employee" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="理发师">
          <el-switch v-model="editForm.is_barber" />
        </el-form-item>
        <el-form-item label="密码" v-if="!editForm.id">
          <el-input v-model="editForm.password" placeholder="默认为工号" />
        </el-form-item>
        <el-form-item label="重置密码" v-if="editForm.id">
          <el-input v-model="editForm.password" placeholder="留空则不修改" />
        </el-form-item>
        <el-form-item label="状态" v-if="editForm.id">
          <el-switch v-model="editForm.is_active" active-text="正常" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'Users',
  data() {
    return {
      loading: false,
      saving: false,
      list: [],
      total: 0,
      query: { keyword: '', role: '', page: 1, page_size: 20 },
      dialogVisible: false,
      editForm: {},
      editRules: {
        employee_id: [{ required: true, message: '请输入工号', trigger: 'blur' }],
        name: [{ required: true, message: '请输入姓名', trigger: 'blur' }]
      }
    }
  },
  created() { this.loadData() },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const res = await request.get('/admin/users', { params: this.query })
        this.list = res.data.list
        this.total = res.data.total
      } finally {
        this.loading = false
      }
    },
    openDialog(row) {
      this.editForm = row
        ? { ...row, password: '' }
        : { employee_id: '', name: '', role: 'employee', is_barber: false, password: '', is_active: true }
      this.dialogVisible = true
    },
    handleSave() {
      this.$refs.editForm.validate(async valid => {
        if (!valid) return
        this.saving = true
        try {
          if (this.editForm.id) {
            await request.put(`/admin/users/${this.editForm.id}`, this.editForm)
          } else {
            await request.post('/admin/users', this.editForm)
          }
          this.$message.success('保存成功')
          this.dialogVisible = false
          this.loadData()
        } finally {
          this.saving = false
        }
      })
    },
    handleDelete(row) {
      this.$confirm(`确定停用用户 ${row.name}？`, '提示').then(async () => {
        await request.delete(`/admin/users/${row.id}`)
        this.$message.success('已停用')
        this.loadData()
      }).catch(() => {})
    }
  }
}
</script>

<style scoped>
.toolbar { margin-bottom: 16px; }
</style>
