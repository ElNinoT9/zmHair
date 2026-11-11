<template>
  <div class="users-page">
    <div class="card toolbar">
      <el-form inline @submit.native.prevent="handleSearch">
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="搜索工号/姓名" clearable style="width:200px" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="query.role" placeholder="角色" clearable style="width:120px">
            <el-option label="员工" value="employee" />
            <el-option label="外协" value="waixie" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-select v-model="query.is_admin" placeholder="管理员" clearable style="width:110px">
            <el-option label="是" value="true" />
            <el-option label="否" value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleSearch">查询</el-button>
          <el-button type="success" icon="el-icon-plus" @click="openDialog()">新增用户</el-button>
          <el-button icon="el-icon-download" @click="handleExport">导出当前数据</el-button>
          <el-button icon="el-icon-document" @click="handleDownloadTemplate">下载模板</el-button>
          <el-button type="warning" icon="el-icon-upload2" @click="openImportDialog">批量导入</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="card">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="employee_id" label="工号" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="role" label="角色" width="90">
          <template slot-scope="{ row }">
            <el-tag :type="businessRoleTagType(row)" size="small">
              {{ businessRoleLabel(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="管理员" width="80">
          <template slot-scope="{ row }">
            <el-tag :type="isAdminUser(row) ? 'danger' : 'info'" size="small">
              {{ isAdminUser(row) ? '是' : '否' }}
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
        <el-table-column label="操作" width="200" fixed="right">
          <template slot-scope="{ row }">
            <el-button type="text" @click="openDialog(row)">编辑</el-button>
            <template v-if="row.role !== 'admin'">
              <el-button
                v-if="row.is_active"
                type="text"
                style="color:#E6A23C"
                @click="handleDeactivate(row)"
              >
                停用
              </el-button>
              <el-button type="text" style="color:#F56C6C" @click="handlePurge(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        style="margin-top:16px;text-align:right"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        :current-page="query.page"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="query.page_size"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
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
          <el-select
            v-model="editForm.business_role"
            style="width:100%"
            :disabled="editForm.is_admin"
            @change="onRoleChange"
          >
            <el-option label="员工" value="employee" />
            <el-option label="外协" value="waixie" />
          </el-select>
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="editForm.is_admin" @change="onAdminChange" />
        </el-form-item>
        <el-form-item label="理发师">
          <el-switch
            v-model="editForm.is_barber"
            :disabled="editForm.is_admin || editForm.business_role === 'waixie'"
          />
          <span v-if="editForm.business_role === 'waixie'" class="field-tip">外协账号固定为理发师</span>
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

    <el-dialog title="批量导入用户" :visible.sync="importVisible" width="520px" @closed="resetImport">
      <el-alert
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom:16px"
      >
        <div slot="title">
          <p><strong>更新（默认）</strong>：相同工号仅更新姓名，保留角色、理发师、状态等原有设置。</p>
          <p style="margin-top:8px"><strong>覆盖</strong>：相同工号按 Excel 中的角色、理发师、状态等字段全部覆盖。</p>
        </div>
      </el-alert>
      <el-form label-width="100px">
        <el-form-item label="导入模式">
          <el-radio-group v-model="importMode">
            <el-radio label="update">更新</el-radio>
            <el-radio label="overwrite">覆盖</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Excel 文件">
          <el-upload
            ref="importUpload"
            action=""
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xlsm"
            :on-change="onImportFileChange"
            :on-remove="onImportFileRemove"
          >
            <el-button size="small" type="primary" plain>选择文件</el-button>
            <div slot="tip" class="el-upload__tip">仅支持 .xlsx，请先下载模板填写</div>
          </el-upload>
        </el-form-item>
      </el-form>
      <div v-if="importResult" class="import-result">
        <p>新增 {{ importResult.created }} 条，更新 {{ importResult.updated }} 条，跳过 {{ importResult.skipped }} 条</p>
        <ul v-if="importResult.errors && importResult.errors.length">
          <li v-for="(msg, i) in importResult.errors.slice(0, 10)" :key="i">{{ msg }}</li>
          <li v-if="importResult.errors.length > 10">…共 {{ importResult.errors.length }} 条提示</li>
        </ul>
      </div>
      <div slot="footer">
        <template v-if="importResult">
          <el-button type="primary" @click="importVisible = false">确认</el-button>
        </template>
        <template v-else>
          <el-button @click="importVisible = false">取消</el-button>
          <el-button type="primary" :loading="importing" :disabled="!importFile" @click="handleImport">开始导入</el-button>
        </template>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'
import {
  roleLabel,
  roleTagType,
  isAdminUser,
  businessRoleLabel,
  businessRoleTagType
} from '@/constants/userRole'

export default {
  name: 'Users',
  data() {
    return {
      loading: false,
      saving: false,
      list: [],
      total: 0,
      query: { keyword: '', role: '', is_admin: '', page: 1, page_size: 20 },
      dialogVisible: false,
      editForm: {},
      editRules: {
        employee_id: [{ required: true, message: '请输入工号', trigger: 'blur' }],
        name: [{ required: true, message: '请输入姓名', trigger: 'blur' }]
      },
      importVisible: false,
      importMode: 'update',
      importFile: null,
      importing: false,
      importResult: null
    }
  },
  created() { this.loadData() },
  methods: {
    roleLabel,
    roleTagType,
    isAdminUser,
    businessRoleLabel,
    businessRoleTagType,
    onRoleChange(role) {
      if (role === 'waixie') this.editForm.is_barber = true
    },
    onAdminChange(isAdmin) {
      if (isAdmin) {
        this.editForm.is_barber = false
      } else if (this.editForm.business_role === 'waixie') {
        this.editForm.is_barber = true
      }
    },
    handleSearch() {
      this.query.page = 1
      this.loadData()
    },
    handlePageChange(page) {
      this.query.page = page
      this.loadData()
    },
    handleSizeChange(size) {
      this.query.page_size = size
      this.query.page = 1
      this.loadData()
    },
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
      if (row) {
        const isAdmin = row.role === 'admin'
        this.editForm = {
          ...row,
          password: '',
          is_admin: isAdmin,
          business_role: isAdmin ? 'employee' : row.role
        }
      } else {
        this.editForm = {
          employee_id: '',
          name: '',
          business_role: 'employee',
          is_admin: false,
          is_barber: false,
          password: '',
          is_active: true
        }
      }
      this.dialogVisible = true
    },
    buildSavePayload() {
      const { business_role, is_admin, ...rest } = this.editForm
      const payload = { ...rest }
      delete payload.business_role
      delete payload.is_admin
      if (is_admin) {
        payload.role = 'admin'
        payload.is_barber = false
      } else {
        payload.role = business_role
      }
      return payload
    },
    handleSave() {
      this.$refs.editForm.validate(async valid => {
        if (!valid) return
        this.saving = true
        try {
          const payload = this.buildSavePayload()
          if (this.editForm.id) {
            await request.put(`/admin/users/${this.editForm.id}`, payload)
          } else {
            await request.post('/admin/users', payload)
          }
          this.$message.success('保存成功')
          this.dialogVisible = false
          this.loadData()
        } finally {
          this.saving = false
        }
      })
    },
    handleDeactivate(row) {
      this.$confirm(`确定停用用户「${row.name}」（工号 ${row.employee_id}）？停用后无法登录。`, '停用用户', {
        type: 'warning'
      }).then(async () => {
        await request.delete(`/admin/users/${row.id}`)
        this.$message.success('已停用')
        this.loadData()
      }).catch(() => {})
    },
    handlePurge(row) {
      this.$confirm(
        `永久删除用户「${row.name}」（工号 ${row.employee_id}）？删除后无法恢复；若存在预约记录将无法删除。`,
        '永久删除',
        {
          type: 'warning',
          confirmButtonText: '永久删除',
          confirmButtonClass: 'el-button--danger'
        }
      ).then(async () => {
        await request.post(`/admin/users/${row.id}/purge`)
        this.$message.success('已删除')
        this.loadData()
      }).catch(() => {})
    },
    async downloadBlob(path, filename, params = {}) {
      const res = await request.get(path, { params, responseType: 'blob' })
      const blob = res.data
      const ct = (res.headers['content-type'] || '').toLowerCase()
      if (ct.includes('json') || (blob.type && blob.type.includes('json'))) {
        const text = await blob.text()
        let msg = '下载失败'
        try {
          const j = JSON.parse(text)
          msg = j.message || j.detail || msg
        } catch (_) { /* ignore */ }
        this.$message.error(msg)
        throw new Error(msg)
      }
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.click()
      window.URL.revokeObjectURL(url)
    },
    async handleExport() {
      const params = {
        keyword: this.query.keyword,
        role: this.query.role,
        is_admin: this.query.is_admin
      }
      const name = `用户列表_${new Date().toISOString().slice(0, 10)}.xlsx`
      await this.downloadBlob('/admin/users/export', name, params)
      this.$message.success('导出成功')
    },
    async handleDownloadTemplate() {
      await this.downloadBlob('/admin/users/import-template', '用户导入模板.xlsx')
      this.$message.success('模板已下载')
    },
    openImportDialog() {
      this.importVisible = true
    },
    resetImport() {
      this.importMode = 'update'
      this.importFile = null
      this.importResult = null
      this.importing = false
      if (this.$refs.importUpload) {
        this.$refs.importUpload.clearFiles()
      }
    },
    onImportFileChange(file) {
      this.importFile = file.raw
      this.importResult = null
    },
    onImportFileRemove() {
      this.importFile = null
    },
    async handleImport() {
      if (!this.importFile) return
      this.importing = true
      try {
        const form = new FormData()
        form.append('file', this.importFile)
        const res = await request.post(`/admin/users/import?mode=${this.importMode}`, form, {
          timeout: 120000
        })
        this.importResult = res.data
        const d = res.data
        this.$message.success(`导入完成：新增 ${d.created}，更新 ${d.updated}`)
        this.loadData()
      } catch (e) {
        if (!e.silent) {
          // 错误文案由 request 拦截器弹出
        }
      } finally {
        this.importing = false
      }
    }
  }
}
</script>

<style scoped>
.toolbar { margin-bottom: 16px; }
.import-result { font-size: 13px; color: #606266; }
.import-result ul { margin: 8px 0 0; padding-left: 20px; color: #E6A23C; }
.field-tip { margin-left: 8px; font-size: 12px; color: #909399; }
</style>
