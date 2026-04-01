<template>
  <div class="admin-page">
    <div class="header">
      <h1>👥 用户管理</h1>
      <p class="subtitle">管理员控制面板</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-message">
      <p>❌ {{ error }}</p>
      <button @click="loadUsers" class="retry-btn">重试</button>
    </div>

    <!-- 用户列表 -->
    <div v-else class="admin-content">
      <!-- 用户表格 -->
      <section class="admin-section">
        <h2>📋 用户列表</h2>
        <div class="toolbar">
          <el-input
            v-model="searchText"
            placeholder="搜索用户名..."
            style="width: 200px"
            @input="loadUsers"
          />
          <el-button type="primary" @click="showCreateUserDialog = true">
            ➕ 创建用户
          </el-button>
        </div>

        <el-table :data="users" style="width: 100%" border>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column label="管理员" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_admin ? 'success' : 'info'">
                {{ row.is_admin ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="250">
            <template #default="{ row }">
              <el-button size="small" @click="editUser(row)">编辑</el-button>
              <el-button
                size="small"
                type="danger"
                @click="deleteUser(row.id)"
                :disabled="row.id === currentUserId"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </section>

      <!-- 历史记录管理 -->
      <section class="admin-section">
        <h2>📜 历史记录管理</h2>
        <div class="toolbar">
          <el-input
            v-model="historySearch"
            placeholder="搜索历史记录..."
            style="width: 300px"
            @input="loadAllHistory"
          />
        </div>

        <el-table :data="allHistory" style="width: 100%" border>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户" width="150" />
          <el-table-column prop="source_text" label="原文" show-overflow-tooltip />
          <el-table-column prop="result_text" label="改写" show-overflow-tooltip />
          <el-table-column label="收藏" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_favorite ? 'success' : 'info'">
                {{ row.is_favorite ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button
                size="small"
                type="danger"
                @click="deleteHistory(row.id)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </section>
    </div>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog v-model="showCreateUserDialog" title="创建用户" width="400px">
      <el-form :model="newUser" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="newUser.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="newUser.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="newUser.is_admin" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateUserDialog = false">取消</el-button>
        <el-button type="primary" @click="createUser">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import http from '../api/http'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(true)
const error = ref(null)
const users = ref([])
const allHistory = ref([])
const searchText = ref('')
const historySearch = ref('')
const showCreateUserDialog = ref(false)
const currentUserId = ref(null)

const newUser = reactive({
  username: '',
  password: '',
  is_admin: false
})

// 获取当前用户 ID
const getCurrentUser = async () => {
  try {
    const response = await http.get('/auth/me')
    currentUserId.value = response.data.id
  } catch (error) {
    console.error('获取当前用户失败:', error)
  }
}

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  error.value = null
  
  try {
    const token = localStorage.getItem('rewrite_token')
    const response = await fetch('/api/admin/users', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      throw new Error('加载用户失败，请检查管理员权限')
    }
    
    const data = await response.json()
    users.value = data.users || []
  } catch (err) {
    error.value = err.message || '加载失败'
  } finally {
    loading.value = false
  }
}

// 加载所有历史记录
const loadAllHistory = async () => {
  try {
    const token = localStorage.getItem('rewrite_token')
    const response = await fetch('/api/admin/history/all', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      allHistory.value = data.records || []
    }
  } catch (err) {
    console.error('加载历史记录失败:', err)
  }
}

// 创建用户
const createUser = async () => {
  if (!newUser.username || !newUser.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  
  try {
    const token = localStorage.getItem('rewrite_token')
    const response = await fetch('/api/admin/users', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newUser)
    })
    
    if (response.ok) {
      ElMessage.success('用户创建成功')
      showCreateUserDialog.value = false
      newUser.username = ''
      newUser.password = ''
      newUser.is_admin = false
      loadUsers()
    } else {
      const data = await response.json()
      ElMessage.error(data.detail || '创建失败')
    }
  } catch (err) {
    ElMessage.error('创建失败')
  }
}

// 编辑用户
const editUser = (user) => {
  ElMessageBox.prompt('设置管理员权限', `用户：${user.username}`, {
    confirmButtonText: '保存',
    cancelButtonText: '取消',
    inputType: 'checkbox',
    inputValue: user.is_admin,
    inputPlaceholder: '是否设为管理员'
  }).then(async ({ value }) => {
    try {
      const token = localStorage.getItem('rewrite_token')
      const response = await fetch(`/api/admin/users/${user.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_admin: value })
      })
      
      if (response.ok) {
        ElMessage.success('更新成功')
        loadUsers()
      } else {
        ElMessage.error('更新失败')
      }
    } catch (err) {
      ElMessage.error('更新失败')
    }
  })
}

// 删除用户
const deleteUser = async (userId) => {
  if (userId === currentUserId.value) {
    ElMessage.warning('不能删除自己')
    return
  }
  
  ElMessageBox.confirm('确定要删除该用户吗？', '警告', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const token = localStorage.getItem('rewrite_token')
      const response = await fetch(`/api/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        ElMessage.success('删除成功')
        loadUsers()
      } else {
        ElMessage.error('删除失败')
      }
    } catch (err) {
      ElMessage.error('删除失败')
    }
  })
}

// 删除历史记录
const deleteHistory = async (recordId) => {
  ElMessageBox.confirm('确定要删除该历史记录吗？', '警告', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const token = localStorage.getItem('rewrite_token')
      const response = await fetch(`/api/admin/history/${recordId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        ElMessage.success('删除成功')
        loadAllHistory()
      } else {
        ElMessage.error('删除失败')
      }
    } catch (err) {
      ElMessage.error('删除失败')
    }
  })
}

onMounted(() => {
  getCurrentUser()
  loadUsers()
  loadAllHistory()
})
</script>

<style scoped>
.admin-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2rem;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 1rem;
}

.loading,
.error-message {
  text-align: center;
  padding: 3rem;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.admin-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.admin-section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.admin-section h2 {
  font-size: 1.5rem;
  color: #1a1a1a;
  margin-bottom: 1.5rem;
}

.toolbar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  justify-content: space-between;
}
</style>
