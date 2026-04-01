<template>
  <div class="settings-page">
    <div class="header">
      <h1>⚙️ 系统设置</h1>
      <p class="subtitle">管理员配置面板</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-message">
      <p>❌ {{ error }}</p>
      <button @click="loadConfigs" class="retry-btn">重试</button>
    </div>

    <!-- 配置表单 -->
    <div v-else class="settings-content">
      <!-- RAG 配置 -->
      <section class="settings-section">
        <h2>📚 RAG 配置</h2>
        <div class="form-group">
          <label for="topK">
            检索条数 (top_k)
            <span class="hint">控制 RAG 检索返回的相似记录数量（1-10）</span>
          </label>
          <input
            id="topK"
            v-model.number="config.top_k"
            type="number"
            min="1"
            max="10"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="threshold">
            相似度阈值
            <span class="hint">过滤低相似度记录（0-1，建议 0.6-0.8）</span>
          </label>
          <input
            id="threshold"
            v-model.number="config.similarity_threshold"
            type="number"
            min="0"
            max="1"
            step="0.1"
            class="form-input"
          />
        </div>

        <button @click="saveRAGConfig" class="btn btn-primary">保存 RAG 配置</button>
      </section>

      <!-- 系统提示词 -->
      <section class="settings-section">
        <h2>📝 系统提示词</h2>
        <div class="form-group">
          <label for="systemPrompt">
            改写助手提示词
            <span class="hint">定义 AI 助手的角色和行为规范</span>
          </label>
          <textarea
            id="systemPrompt"
            v-model="config.system_prompt"
            rows="12"
            class="form-textarea"
            placeholder="请输入系统提示词..."
          ></textarea>
        </div>

        <button @click="saveSystemPrompt" class="btn btn-primary">保存提示词</button>
      </section>

      <!-- 功能开关 -->
      <section class="settings-section">
        <h2>🔧 功能开关</h2>
        <div class="form-group">
          <label class="checkbox-label">
            <input
              v-model="config.enable_registration"
              type="checkbox"
              class="form-checkbox"
            />
            <span>允许用户注册</span>
            <span class="hint">关闭后，新用户无法注册，只能通过登录访问</span>
          </label>
        </div>

        <button @click="saveFeatureFlags" class="btn btn-primary">保存开关设置</button>
      </section>

      <!-- 向量数据库配置 -->
      <section class="settings-section">
        <h2>🗄️ 向量数据库</h2>
        <div class="info-box">
          <p><strong>当前后端:</strong> {{ vectorBackend }}</p>
          <p class="hint">
            修改向量数据库后端需要编辑 .env 文件并重启服务<br>
            支持的后端：vikingdb, pgvector, qdrant, milvus
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'SettingsPage',
  setup() {
    const authStore = useAuthStore()
    const loading = ref(true)
    const error = ref(null)
    const vectorBackend = ref('vikingdb') // 从环境变量读取

    const config = ref({
      top_k: 3,
      similarity_threshold: 0.7,
      system_prompt: '',
      enable_registration: true
    })

    // 加载配置
    const loadConfigs = async () => {
      loading.value = true
      error.value = null

      try {
        const token = authStore.token
        const headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }

        // 获取所有配置
        const [ragRes, promptRes, flagsRes] = await Promise.all([
          fetch('/api/admin/config/rag/config', { headers }),
          fetch('/api/admin/config/prompt/system', { headers }),
          fetch('/api/admin/config/flags', { headers })
        ])

        if (!ragRes.ok || !promptRes.ok || !flagsRes.ok) {
          throw new Error('加载配置失败，请检查管理员权限')
        }

        const ragData = await ragRes.json()
        const promptData = await promptRes.json()
        const flagsData = await flagsRes.json()

        config.value = {
          top_k: ragData.top_k,
          similarity_threshold: ragData.similarity_threshold,
          system_prompt: promptData.prompt,
          enable_registration: flagsData.enable_registration
        }
      } catch (err) {
        console.error('加载配置失败:', err)
        error.value = err.message || '加载失败'
      } finally {
        loading.value = false
      }
    }

    // 保存 RAG 配置
    const saveRAGConfig = async () => {
      try {
        const token = authStore.token
        const res = await fetch('/api/admin/config/rag/config', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            top_k: config.value.top_k,
            similarity_threshold: config.value.similarity_threshold
          })
        })

        if (!res.ok) {
          const data = await res.json()
          throw new Error(data.detail || '保存失败')
        }

        alert('✅ RAG 配置已保存！')
      } catch (err) {
        alert('❌ 保存失败：' + err.message)
      }
    }

    // 保存系统提示词
    const saveSystemPrompt = async () => {
      try {
        const token = authStore.token
        const res = await fetch('/api/admin/config/prompt/system', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            prompt: config.value.system_prompt
          })
        })

        if (!res.ok) {
          const data = await res.json()
          throw new Error(data.detail || '保存失败')
        }

        alert('✅ 系统提示词已保存！')
      } catch (err) {
        alert('❌ 保存失败：' + err.message)
      }
    }

    // 保存功能开关
    const saveFeatureFlags = async () => {
      try {
        const token = authStore.token
        const res = await fetch(
          `/api/admin/config/flags/registration?enable=${config.value.enable_registration}`,
          {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        )

        if (!res.ok) {
          const data = await res.json()
          throw new Error(data.detail || '保存失败')
        }

        alert('✅ 功能开关已保存！')
      } catch (err) {
        alert('❌ 保存失败：' + err.message)
      }
    }

    onMounted(() => {
      // 检查是否是管理员
      if (!authStore.user || !authStore.user.is_admin) {
        error.value = '权限不足：需要管理员权限才能访问此页面'
        loading.value = false
        return
      }

      loadConfigs()
    })

    return {
      loading,
      error,
      config,
      vectorBackend,
      loadConfigs,
      saveRAGConfig,
      saveSystemPrompt,
      saveFeatureFlags
    }
  }
}
</script>

<style scoped>
.settings-page {
  max-width: 800px;
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

.settings-section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.settings-section h2 {
  font-size: 1.5rem;
  color: #1a1a1a;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.hint {
  display: block;
  font-size: 0.85rem;
  color: #666;
  font-weight: normal;
  margin-top: 0.25rem;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 200px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.form-checkbox {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.info-box {
  background: #f8f9fa;
  border-left: 4px solid #3498db;
  padding: 1rem;
  border-radius: 4px;
}

.info-box p {
  margin: 0.5rem 0;
}

.info-box .hint {
  color: #666;
  font-size: 0.9rem;
}
</style>
