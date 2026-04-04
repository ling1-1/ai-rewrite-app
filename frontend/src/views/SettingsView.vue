<template>
  <div class="settings-page">
    <div class="header">
      <div>
        <h1>⚙️ 系统设置</h1>
        <p class="subtitle">管理员配置面板</p>
      </div>
      <button @click="goBack" class="back-btn">返回工作台</button>
    </div>

    <div v-if="pageLoading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="pageError" class="error-message">
      <p>❌ {{ pageError }}</p>
      <button @click="initializePage" class="retry-btn">重试</button>
    </div>

    <div v-else class="settings-content">
      <el-tabs v-model="activeTab" class="settings-tabs">
        <el-tab-pane label="基础配置" name="config">
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

          <section class="settings-section">
            <h2>📝 降重提示词</h2>
            <div class="form-group">
              <label for="rewritePromptZh">
                中文降重提示词
                <span class="hint">用于中文论文降重模式，建议保持学术表达和语义不变。</span>
              </label>
              <textarea
                id="rewritePromptZh"
                v-model="config.rewrite_prompt_zh"
                rows="12"
                class="form-textarea"
                placeholder="请输入中文降重提示词..."
              ></textarea>
            </div>

            <div class="form-group">
              <label for="rewritePromptEn">
                英文降重提示词
                <span class="hint">用于英文论文降重模式，建议保持英文论文的正式和清晰表达。</span>
              </label>
              <textarea
                id="rewritePromptEn"
                v-model="config.rewrite_prompt_en"
                rows="12"
                class="form-textarea"
                placeholder="请输入英文降重提示词..."
              ></textarea>
            </div>

            <button @click="saveRewritePrompt" class="btn btn-primary">保存降重提示词</button>
          </section>

          <section class="settings-section">
            <h2>🎤 答辩辅助提示词</h2>
            <div class="form-group">
              <label for="defenseSystemPrompt">
                答辩辅助系统提示词
                <span class="hint">控制答辩辅助整体口吻、身份和输出边界。</span>
              </label>
              <textarea
                id="defenseSystemPrompt"
                v-model="config.defense_system_prompt"
                rows="8"
                class="form-textarea"
                placeholder="请输入答辩辅助系统提示词..."
              ></textarea>
            </div>

            <div class="form-group">
              <label for="defensePptPrompt">
                答辩 PPT 提示词
                <span class="hint">用于生成答辩 PPT 文字内容。建议保留变量：{thesis_text}、{ppt_page_count}、{ppt_outline}、{language_style}、{persona_style}、{content_density}、{include_personal_view_text}、{include_acknowledgement_text}。</span>
              </label>
              <textarea
                id="defensePptPrompt"
                v-model="config.defense_ppt_prompt"
                rows="12"
                class="form-textarea"
                placeholder="请输入答辩PPT提示词..."
              ></textarea>
            </div>

            <div class="form-group">
              <label for="defenseSpeechPrompt">
                答辩稿提示词
                <span class="hint">用于生成答辩稿。建议保留变量：{thesis_text}、{ppt_content}、{speech_duration_minutes}、{ppt_outline}、{language_style}、{persona_style}、{content_density}、{include_personal_view_text}、{include_acknowledgement_text}。</span>
              </label>
              <textarea
                id="defenseSpeechPrompt"
                v-model="config.defense_speech_prompt"
                rows="12"
                class="form-textarea"
                placeholder="请输入答辩稿提示词..."
              ></textarea>
            </div>

            <button @click="saveDefensePrompt" class="btn btn-primary">保存答辩提示词</button>
          </section>

          <section class="settings-section">
            <h2>🤖 模型配置</h2>
            <div class="info-box">
              <p><strong>填写建议：</strong>优先使用正式 API，不建议把仅面向编程工具的专用套餐直接接到你的网站后端。</p>
              <p class="hint">
                Base URL 可直接填写到服务商给出的 <code>/v1</code> 或 <code>/api/v3</code> 这一层，系统会自动补全 <code>chat/completions</code>。<br />
                例如 Claude 可填 <code>https://api.anthropic.com</code>，火山可填 <code>https://ark.cn-beijing.volces.com/api/v3</code>。<br />
                如果你用阿里云 OpenAI 兼容地址，通常应直接填到 <code>.../v1</code>，并确认 API Key 与该产品线匹配。
              </p>
            </div>
            <div class="model-config-grid">
              <div class="model-config-card">
                <h3>降重模型</h3>
                <div class="form-group">
                  <label for="rewriteApiKey">
                    API Key
                    <span class="hint">用于论文降重、改写和 RAG 主流程。要和下面的 Base URL 属于同一家服务。</span>
                  </label>
                  <el-input
                    id="rewriteApiKey"
                    v-model="config.rewrite_api_key"
                    type="password"
                    show-password
                    placeholder="请输入降重模型 API Key"
                  />
                </div>

                <div class="form-group">
                  <label for="rewriteModel">
                    模型名称
                    <span class="hint">建议使用更强一点的模型。</span>
                  </label>
                  <input
                    id="rewriteModel"
                    v-model="config.rewrite_model"
                    type="text"
                    class="form-input"
                    placeholder="例如：claude-sonnet-4-20250514"
                  />
                </div>

                <div class="form-group">
                  <label for="rewriteBaseUrl">
                    Base URL
                    <span class="hint">支持直接填写到 <code>/v1</code> 或 <code>/api/v3</code>，系统会自动补全接口路径。</span>
                  </label>
                  <input
                    id="rewriteBaseUrl"
                    v-model="config.rewrite_base_url"
                    type="text"
                    class="form-input"
                    placeholder="例如：https://api.anthropic.com"
                  />
                </div>

                <div class="model-grid">
                  <div class="form-group">
                    <label for="rewriteMaxTokens">最大输出长度</label>
                    <input
                      id="rewriteMaxTokens"
                      v-model.number="config.rewrite_max_tokens"
                      type="number"
                      min="256"
                      max="16384"
                      class="form-input"
                    />
                  </div>

                  <div class="form-group">
                    <label for="rewriteTemperature">温度</label>
                    <input
                      id="rewriteTemperature"
                      v-model.number="config.rewrite_temperature"
                      type="number"
                      min="0"
                      max="2"
                      step="0.1"
                      class="form-input"
                    />
                  </div>
                </div>
              </div>

              <div class="model-config-card">
                <h3>答辩辅助模型</h3>
                <div class="form-group">
                  <label for="defenseApiKey">
                    API Key
                    <span class="hint">答辩辅助建议单独用更稳定、成本更低的正式 API。</span>
                  </label>
                  <el-input
                    id="defenseApiKey"
                    v-model="config.defense_api_key"
                    type="password"
                    show-password
                    placeholder="请输入答辩模型 API Key"
                  />
                </div>

                <div class="form-group">
                  <label for="defenseModel">
                    模型名称
                    <span class="hint">用于生成答辩PPT文字和答辩稿。</span>
                  </label>
                  <input
                    id="defenseModel"
                    v-model="config.defense_model"
                    type="text"
                    class="form-input"
                    placeholder="例如：doubao-lite-4k-241215"
                  />
                </div>

                <div class="form-group">
                  <label for="defenseBaseUrl">
                    Base URL
                    <span class="hint">如果使用 OpenAI 兼容接口，建议直接填到 <code>.../v1</code> 这一层，不要手动拼 <code>/chat/completions</code>。</span>
                  </label>
                  <input
                    id="defenseBaseUrl"
                    v-model="config.defense_base_url"
                    type="text"
                    class="form-input"
                    placeholder="例如：https://ark.cn-beijing.volces.com/api/v3"
                  />
                </div>

                <div class="model-grid">
                  <div class="form-group">
                    <label for="defenseMaxTokens">最大输出长度</label>
                    <input
                      id="defenseMaxTokens"
                      v-model.number="config.defense_max_tokens"
                      type="number"
                      min="256"
                      max="8192"
                      class="form-input"
                    />
                  </div>

                  <div class="form-group">
                    <label for="defenseTemperature">温度</label>
                    <input
                      id="defenseTemperature"
                      v-model.number="config.defense_temperature"
                      type="number"
                      min="0"
                      max="2"
                      step="0.1"
                      class="form-input"
                    />
                  </div>
                </div>
              </div>
            </div>

            <button @click="saveModelConfig" class="btn btn-primary">保存模型配置</button>
          </section>

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
                <span class="hint">关闭后，新用户无法通过注册页面创建账号</span>
              </label>
            </div>

            <button @click="saveFeatureFlags" class="btn btn-primary">保存开关设置</button>
          </section>

          <section class="settings-section">
            <h2>🗄️ 向量数据库</h2>
            <div class="model-config-grid">
              <div class="model-config-card">
                <h3>向量模型</h3>
                <div class="form-group">
                  <label for="embeddingProvider">Provider</label>
                  <input
                    id="embeddingProvider"
                    v-model="config.embedding_provider"
                    type="text"
                    class="form-input"
                    placeholder="例如：voyage"
                  />
                </div>

                <div class="form-group">
                  <label for="embeddingApiKey">API Key</label>
                  <el-input
                    id="embeddingApiKey"
                    v-model="config.embedding_api_key"
                    type="password"
                    show-password
                    placeholder="请输入向量模型 API Key"
                  />
                </div>

                <div class="form-group">
                  <label for="embeddingModel">模型名称</label>
                  <input
                    id="embeddingModel"
                    v-model="config.embedding_model"
                    type="text"
                    class="form-input"
                    placeholder="例如：voyage-4-lite"
                  />
                </div>

                <div class="form-group">
                  <label for="embeddingBaseUrl">Base URL</label>
                  <input
                    id="embeddingBaseUrl"
                    v-model="config.embedding_base_url"
                    type="text"
                    class="form-input"
                    placeholder="例如：https://api.voyageai.com/v1"
                  />
                </div>

                <div class="form-group">
                  <label for="embeddingDimension">向量维度</label>
                  <input
                    id="embeddingDimension"
                    v-model.number="config.embedding_dimension"
                    type="number"
                    min="1"
                    class="form-input"
                  />
                </div>
              </div>

              <div class="model-config-card">
                <h3>向量数据库</h3>
                <div class="form-group">
                  <label for="vectorDbBackend">
                    后端类型
                    <span class="hint">当前生效后端：{{ vectorBackend }}</span>
                  </label>
                  <input
                    id="vectorDbBackend"
                    v-model="config.vector_db_backend"
                    type="text"
                    class="form-input"
                    placeholder="例如：qdrant"
                  />
                </div>

                <div class="form-group">
                  <label for="qdrantUrl">Qdrant URL</label>
                  <input
                    id="qdrantUrl"
                    v-model="config.qdrant_url"
                    type="text"
                    class="form-input"
                    placeholder="例如：https://xxx.aws.cloud.qdrant.io:6333"
                  />
                </div>

                <div class="form-group">
                  <label for="qdrantApiKey">Qdrant API Key</label>
                  <el-input
                    id="qdrantApiKey"
                    v-model="config.qdrant_api_key"
                    type="password"
                    show-password
                    placeholder="请输入 Qdrant API Key"
                  />
                </div>

                <div class="form-group">
                  <label for="qdrantCollection">Collection 名称</label>
                  <input
                    id="qdrantCollection"
                    v-model="config.qdrant_collection"
                    type="text"
                    class="form-input"
                    placeholder="例如：ai_rewrite_records_voyage"
                  />
                </div>
              </div>
            </div>

            <button @click="saveVectorConfig" class="btn btn-primary">保存向量配置</button>
          </section>
        </el-tab-pane>

        <el-tab-pane label="用户管理" name="users">
          <section class="settings-section">
            <div class="section-head">
              <div>
                <h2>👥 用户管理</h2>
                <p class="hint">支持管理员创建、编辑、删除用户，并设置管理员权限。</p>
              </div>
              <el-button type="primary" @click="openCreateUserDialog">创建用户</el-button>
            </div>

            <div class="toolbar">
              <el-input
                v-model="userSearch"
                placeholder="搜索用户名"
                clearable
                @input="loadUsers"
              />
              <el-button @click="loadUsers">刷新</el-button>
            </div>

            <el-table :data="users" border style="width: 100%">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="username" label="用户名" min-width="180" />
              <el-table-column label="管理员" width="120">
                <template #default="{ row }">
                  <el-tag :type="row.is_admin ? 'warning' : 'info'">
                    {{ row.is_admin ? "管理员" : "普通用户" }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" min-width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="220" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" @click="openEditUserDialog(row)">编辑</el-button>
                  <el-button
                    size="small"
                    type="danger"
                    :disabled="row.id === currentUserId"
                    @click="deleteUser(row)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </section>
        </el-tab-pane>

        <el-tab-pane label="历史记录管理" name="history">
          <section class="settings-section">
            <div class="section-head">
              <div>
                <h2>📜 全部历史记录</h2>
                <p class="hint">支持查看所有用户历史记录，并进行编辑、删除和搜索。</p>
              </div>
            </div>

            <div class="toolbar toolbar-history">
              <el-input
                v-model="historySearch"
                placeholder="搜索名称、原文或结果"
                clearable
                @input="loadAllHistory"
              />
              <el-input
                v-model.number="historyUserIdFilter"
                placeholder="按用户 ID 过滤"
                clearable
                @input="loadAllHistory"
              />
              <el-button @click="loadAllHistory">刷新</el-button>
            </div>

            <el-table :data="allHistory" border style="width: 100%">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="username" label="用户" width="140" />
              <el-table-column label="名称" min-width="160">
                <template #default="{ row }">
                  <div class="history-name-cell">
                    <span>{{ row.name || "未命名记录" }}</span>
                    <el-tag v-if="row.is_favorite" type="warning" size="small">收藏</el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="source_text" label="原文" min-width="220" show-overflow-tooltip />
              <el-table-column prop="result_text" label="结果" min-width="220" show-overflow-tooltip />
              <el-table-column prop="created_at" label="创建时间" min-width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="220" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" @click="openEditHistoryDialog(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteHistory(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </section>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog
      v-model="userDialogVisible"
      :title="editingUserId ? '编辑用户' : '创建用户'"
      width="460px"
    >
      <el-form :model="userForm" label-width="90px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item :label="editingUserId ? '新密码' : '密码'">
          <el-input
            v-model="userForm.password"
            type="password"
            show-password
            :placeholder="editingUserId ? '留空则不修改密码' : '请输入密码'"
          />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="userForm.is_admin" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUserForm">
          {{ editingUserId ? "保存" : "创建" }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="historyDialogVisible"
      title="编辑历史记录"
      width="760px"
    >
      <el-form :model="historyForm" label-width="90px">
        <el-form-item label="名称">
          <el-input v-model="historyForm.name" placeholder="请输入记录名称" />
        </el-form-item>
        <el-form-item label="原文">
          <el-input v-model="historyForm.source_text" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="结果">
          <el-input v-model="historyForm.result_text" type="textarea" :rows="6" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="historyForm.notes" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="收藏">
          <el-switch v-model="historyForm.is_favorite" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="historyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitHistoryForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { useAuthStore } from "../stores/auth";
import http from "../api/http";
import { setCachedRegistrationFlag } from "../api/publicFlags";
import { getErrorMessage } from "../utils/error";

const router = useRouter();
const authStore = useAuthStore();

const activeTab = ref("config");
const pageLoading = ref(true);
const pageError = ref(null);
const vectorBackend = ref("vikingdb");
const currentUserId = ref(null);

const config = ref({
  top_k: 3,
  similarity_threshold: 0.7,
  rewrite_prompt_zh: "",
  rewrite_prompt_en: "",
  defense_system_prompt: "",
  defense_ppt_prompt: "",
  defense_speech_prompt: "",
  rewrite_api_key: "",
  rewrite_model: "",
  rewrite_base_url: "",
  rewrite_max_tokens: 4096,
  rewrite_temperature: 0.7,
  defense_api_key: "",
  defense_model: "",
  defense_base_url: "",
  defense_max_tokens: 2048,
  defense_temperature: 0.5,
  embedding_provider: "voyage",
  embedding_api_key: "",
  embedding_model: "",
  embedding_base_url: "",
  embedding_dimension: 1024,
  vector_db_backend: "qdrant",
  qdrant_url: "",
  qdrant_api_key: "",
  qdrant_collection: "",
  enable_registration: true,
});

const users = ref([]);
const userSearch = ref("");
const userDialogVisible = ref(false);
const editingUserId = ref(null);
const userForm = reactive({
  username: "",
  password: "",
  is_admin: false,
});

const allHistory = ref([]);
const historySearch = ref("");
const historyUserIdFilter = ref(null);
const historyDialogVisible = ref(false);
const editingHistoryId = ref(null);
const historyForm = reactive({
  name: "",
  source_text: "",
  result_text: "",
  notes: "",
  is_favorite: false,
});

function goBack() {
  router.push("/");
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString("zh-CN") : "-";
}

function getFallbackBaseUrls() {
  if (typeof window === "undefined") {
    return [];
  }

  const baseUrls = [];
  const hostname = window.location.hostname;

  if (hostname === "localhost" || hostname === "127.0.0.1") {
    baseUrls.push("http://127.0.0.1:8002", "http://localhost:8002");
  }

  return [...new Set(baseUrls)];
}

async function requestApi(method, path, payload) {
  try {
    const response = await http.request({
      method,
      url: path,
      data: payload,
    });

    return response.data;
  } catch (err) {
    if (err.response) {
      throw err;
    }

    let lastError = err;
    const headers = {
      Authorization: `Bearer ${authStore.token}`,
    };

    if (payload !== undefined) {
      headers["Content-Type"] = "application/json";
    }

    for (const baseUrl of getFallbackBaseUrls()) {
      try {
        const response = await fetch(`${baseUrl}${path}`, {
          method,
          headers,
          body: payload !== undefined ? JSON.stringify(payload) : undefined,
        });

        let data = null;
        const contentType = response.headers.get("content-type") || "";
        if (contentType.includes("application/json")) {
          data = await response.json();
        }

        if (!response.ok) {
          throw new Error(data?.detail || `请求失败（${response.status}）`);
        }

        return data;
      } catch (fallbackError) {
        lastError = fallbackError;
      }
    }

    throw lastError;
  }
}

async function loadConfigs() {
  const [ragData, rewritePromptData, defensePromptData, modelData, vectorData, flagsData] = await Promise.all([
    requestApi("GET", "/admin/config/rag/config"),
    requestApi("GET", "/admin/config/prompt/rewrite"),
    requestApi("GET", "/admin/config/prompt/defense"),
    requestApi("GET", "/admin/config/model/config"),
    requestApi("GET", "/admin/config/vector/config"),
    requestApi("GET", "/admin/config/flags"),
  ]);

  config.value = {
    top_k: ragData.top_k,
    similarity_threshold: ragData.similarity_threshold,
    rewrite_prompt_zh: rewritePromptData.zh_prompt,
    rewrite_prompt_en: rewritePromptData.en_prompt,
    defense_system_prompt: defensePromptData.system_prompt,
    defense_ppt_prompt: defensePromptData.ppt_prompt,
    defense_speech_prompt: defensePromptData.speech_prompt,
    rewrite_api_key: modelData.rewrite_api_key,
    rewrite_model: modelData.rewrite_model,
    rewrite_base_url: modelData.rewrite_base_url,
    rewrite_max_tokens: modelData.rewrite_max_tokens,
    rewrite_temperature: modelData.rewrite_temperature,
    defense_api_key: modelData.defense_api_key,
    defense_model: modelData.defense_model,
    defense_base_url: modelData.defense_base_url,
    defense_max_tokens: modelData.defense_max_tokens,
    defense_temperature: modelData.defense_temperature,
    embedding_provider: vectorData.embedding_provider,
    embedding_api_key: vectorData.embedding_api_key,
    embedding_model: vectorData.embedding_model,
    embedding_base_url: vectorData.embedding_base_url,
    embedding_dimension: vectorData.embedding_dimension,
    vector_db_backend: vectorData.vector_db_backend,
    qdrant_url: vectorData.qdrant_url,
    qdrant_api_key: vectorData.qdrant_api_key,
    qdrant_collection: vectorData.qdrant_collection,
    enable_registration: flagsData.enable_registration,
  };
  vectorBackend.value = vectorData.vector_db_backend;
  setCachedRegistrationFlag(flagsData.enable_registration);
}

async function loadCurrentUser() {
  const data = await requestApi("GET", "/auth/me");
  currentUserId.value = data.id;
}

async function loadUsers() {
  const query = userSearch.value.trim()
    ? `?search=${encodeURIComponent(userSearch.value.trim())}`
    : "";
  const data = await requestApi("GET", `/admin/users${query}`);
  users.value = data.users || [];
}

async function loadAllHistory() {
  const params = new URLSearchParams();
  if (historySearch.value.trim()) {
    params.set("search", historySearch.value.trim());
  }
  if (historyUserIdFilter.value) {
    params.set("user_id", String(historyUserIdFilter.value));
  }

  const suffix = params.toString() ? `?${params.toString()}` : "";
  const data = await requestApi("GET", `/admin/history/all${suffix}`);
  allHistory.value = data.records || [];
}

async function initializePage() {
  pageLoading.value = true;
  pageError.value = null;

  try {
    if (!authStore.user || !authStore.user.is_admin) {
      throw new Error("权限不足：需要管理员权限才能访问此页面");
    }

    await Promise.all([
      loadCurrentUser(),
      loadConfigs(),
      loadUsers(),
      loadAllHistory(),
    ]);
  } catch (error) {
    pageError.value = getErrorMessage(error, "加载失败，请检查管理员权限");
  } finally {
    pageLoading.value = false;
  }
}

async function saveRAGConfig() {
  try {
    await requestApi("PUT", "/admin/config/rag/config", {
      top_k: config.value.top_k,
      similarity_threshold: config.value.similarity_threshold,
    });
    ElMessage.success("RAG 配置已保存");
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "保存失败"));
  }
}

async function saveRewritePrompt() {
  try {
    await requestApi("PUT", "/admin/config/prompt/rewrite", {
      zh_prompt: config.value.rewrite_prompt_zh,
      en_prompt: config.value.rewrite_prompt_en,
    });
    ElMessage.success("降重提示词已保存");
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "保存失败"));
  }
}

async function saveDefensePrompt() {
  try {
    await requestApi("PUT", "/admin/config/prompt/defense", {
      system_prompt: config.value.defense_system_prompt,
      ppt_prompt: config.value.defense_ppt_prompt,
      speech_prompt: config.value.defense_speech_prompt,
    });
    ElMessage.success("答辩提示词已保存");
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "保存失败"));
  }
}

async function saveModelConfig() {
  try {
    await requestApi("PUT", "/admin/config/model/config", {
      rewrite_api_key: config.value.rewrite_api_key,
      rewrite_model: config.value.rewrite_model,
      rewrite_base_url: config.value.rewrite_base_url,
      rewrite_max_tokens: config.value.rewrite_max_tokens,
      rewrite_temperature: config.value.rewrite_temperature,
      defense_api_key: config.value.defense_api_key,
      defense_model: config.value.defense_model,
      defense_base_url: config.value.defense_base_url,
      defense_max_tokens: config.value.defense_max_tokens,
      defense_temperature: config.value.defense_temperature,
    });
    ElMessage.success("模型配置已保存");
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "保存失败"));
  }
}

async function saveVectorConfig() {
  try {
    const data = await requestApi("PUT", "/admin/config/vector/config", {
      embedding_provider: config.value.embedding_provider,
      embedding_api_key: config.value.embedding_api_key,
      embedding_model: config.value.embedding_model,
      embedding_base_url: config.value.embedding_base_url,
      embedding_dimension: config.value.embedding_dimension,
      vector_db_backend: config.value.vector_db_backend,
      qdrant_url: config.value.qdrant_url,
      qdrant_api_key: config.value.qdrant_api_key,
      qdrant_collection: config.value.qdrant_collection,
    });
    vectorBackend.value = data.vector_db_backend;
    ElMessage.success("向量配置已保存");
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "保存失败"));
  }
}

async function saveFeatureFlags() {
  try {
    await requestApi("PUT", "/admin/config/flags", {
      enable_registration: config.value.enable_registration,
    });
    setCachedRegistrationFlag(config.value.enable_registration);
    ElMessage.success("功能开关已保存");
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "保存失败"));
  }
}

function resetUserForm() {
  editingUserId.value = null;
  userForm.username = "";
  userForm.password = "";
  userForm.is_admin = false;
}

function openCreateUserDialog() {
  resetUserForm();
  userDialogVisible.value = true;
}

function openEditUserDialog(user) {
  editingUserId.value = user.id;
  userForm.username = user.username;
  userForm.password = "";
  userForm.is_admin = user.is_admin;
  userDialogVisible.value = true;
}

async function submitUserForm() {
  if (!userForm.username.trim()) {
    ElMessage.warning("请输入用户名");
    return;
  }

  if (!editingUserId.value && !userForm.password.trim()) {
    ElMessage.warning("请输入密码");
    return;
  }

  try {
    if (editingUserId.value) {
      const payload = {
        username: userForm.username.trim(),
        is_admin: userForm.is_admin,
      };
      if (userForm.password.trim()) {
        payload.password = userForm.password.trim();
      }

      await requestApi("PUT", `/admin/users/${editingUserId.value}`, payload);
      ElMessage.success("用户更新成功");
    } else {
      await requestApi("POST", "/admin/users", {
        username: userForm.username.trim(),
        password: userForm.password.trim(),
        is_admin: userForm.is_admin,
      });
      ElMessage.success("用户创建成功");
    }

    userDialogVisible.value = false;
    resetUserForm();
    await loadUsers();
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "保存用户失败"));
  }
}

async function deleteUser(user) {
  if (user.id === currentUserId.value) {
    ElMessage.warning("不能删除自己");
    return;
  }

  try {
    await ElMessageBox.confirm(`确认删除用户“${user.username}”吗？`, "删除用户", {
      confirmButtonText: "删除",
      cancelButtonText: "取消",
      type: "warning",
    });

    await requestApi("DELETE", `/admin/users/${user.id}`);
    ElMessage.success("用户删除成功");
    await loadUsers();
  } catch (error) {
    if (error === "cancel") {
      return;
    }
    ElMessage.error(getErrorMessage(error, "删除用户失败"));
  }
}

function resetHistoryForm() {
  editingHistoryId.value = null;
  historyForm.name = "";
  historyForm.source_text = "";
  historyForm.result_text = "";
  historyForm.notes = "";
  historyForm.is_favorite = false;
}

function openEditHistoryDialog(record) {
  editingHistoryId.value = record.id;
  historyForm.name = record.name || "";
  historyForm.source_text = record.source_text || "";
  historyForm.result_text = record.result_text || "";
  historyForm.notes = record.notes || "";
  historyForm.is_favorite = Boolean(record.is_favorite);
  historyDialogVisible.value = true;
}

async function submitHistoryForm() {
  try {
    await requestApi("PUT", `/admin/history/${editingHistoryId.value}`, {
      name: historyForm.name,
      source_text: historyForm.source_text,
      result_text: historyForm.result_text,
      notes: historyForm.notes,
      is_favorite: historyForm.is_favorite,
    });

    historyDialogVisible.value = false;
    resetHistoryForm();
    ElMessage.success("历史记录更新成功");
    await loadAllHistory();
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "更新历史记录失败"));
  }
}

async function deleteHistory(record) {
  try {
    await ElMessageBox.confirm(
      `确认删除历史记录“${record.name || `#${record.id}`}”吗？`,
      "删除历史记录",
      {
        confirmButtonText: "删除",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await requestApi("DELETE", `/admin/history/${record.id}`);
    ElMessage.success("历史记录删除成功");
    await loadAllHistory();
  } catch (error) {
    if (error === "cancel") {
      return;
    }
    ElMessage.error(getErrorMessage(error, "删除历史记录失败"));
  }
}

onMounted(initializePage);
</script>

<style scoped>
.settings-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
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

.back-btn {
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 999px;
  background: #1f2937;
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.settings-tabs :deep(.el-tabs__header) {
  margin-bottom: 1rem;
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

.retry-btn,
.btn {
  margin-top: 1rem;
  padding: 0.75rem 1.25rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.settings-section {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}

.settings-section h2 {
  font-size: 1.5rem;
  color: #1a1a1a;
  margin-bottom: 1rem;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.model-config-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.model-config-card {
  padding: 1.25rem;
  border-radius: 14px;
  border: 1px solid #e5e7eb;
  background: #fafcff;
}

.model-config-card h3 {
  margin: 0 0 1rem;
  font-size: 1.1rem;
  color: #111827;
}

.model-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.form-input,
.form-textarea {
  width: 100%;
  border: 1px solid #d7dde6;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  font-size: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.form-checkbox {
  width: 18px;
  height: 18px;
  margin-top: 2px;
}

.hint {
  display: block;
  font-size: 0.9rem;
  color: #666;
  margin-top: 0.25rem;
}

@media (max-width: 900px) {
  .model-config-grid,
  .model-grid {
    grid-template-columns: 1fr;
  }
}

.toolbar {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
}

.toolbar :deep(.el-input) {
  max-width: 320px;
}

.toolbar-history {
  flex-wrap: wrap;
}

.info-box {
  background: #f8fafc;
  border-left: 4px solid #4c9ffe;
  padding: 1rem 1.25rem;
  border-radius: 8px;
}

.history-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

@media (max-width: 900px) {
  .settings-page {
    padding: 1rem;
  }

  .header,
  .section-head,
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar :deep(.el-input) {
    max-width: none;
  }
}
</style>
