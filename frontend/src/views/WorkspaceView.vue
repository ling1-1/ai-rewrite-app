<template>
  <div class="workspace-page">
    <div class="workspace-shell">
      <header class="workspace-topbar">
        <div class="brand-badge">
          <span class="brand-mark">JS</span>
          <div>
            <div>JS 论文工作室</div>
            <small class="muted">Paper Rewrite Console</small>
          </div>
        </div>

        <div class="right">
          <span class="pill">{{ authStore.user?.username || "未命名用户" }}</span>
          <el-button v-if="authStore.user?.is_admin" round @click="goToSettings">⚙️ 设置</el-button>
          <el-button round @click="handleLogout">退出登录</el-button>
        </div>
      </header>

      <div class="app-workspace-layout">
        <FeatureSidebar />

        <main class="app-workspace-main">
        <div class="workspace-grid">
        <section class="workspace-panel">
          <div class="workspace-heading">
            <p class="section-kicker">Workspace</p>
            <h1>左边输入论文原文，右边查看处理结果，下面保留你的历史记录。</h1>
            <p>这一版先聚焦论文改写最常用的流程，让整个工作区更直接、更顺手。</p>
          </div>

          <div class="workspace-overview-strip">
            <div class="workspace-overview-item">
              <span class="overview-eyebrow">双模式</span>
              <strong>中文 / 英文分开处理</strong>
              <p>同一个工作台里切换改写模式，不用反复跳页面。</p>
            </div>
            <div class="workspace-overview-item">
              <span class="overview-eyebrow">参考开关</span>
              <strong>向量检索按次控制</strong>
              <p>每次改写前自己决定要不要带 RAG 参考示例。</p>
            </div>
            <div class="workspace-overview-item">
              <span class="overview-eyebrow">知识库闭环</span>
              <strong>待入库、已入库、已更新入库</strong>
              <p>历史记录和样本积累状态放在同一条链路里查看。</p>
            </div>
          </div>

          <div class="editor-grid">
            <article class="editor-card">
              <div class="editor-header">
                <div>
                  <p class="editor-label">Input</p>
                  <h2 class="editor-title">论文原文</h2>
                </div>
                <span class="muted">{{ sourceText.trim().length }} 字</span>
              </div>

              <div class="pane-ruler">
                <span>Thesis Source</span>
                <span>{{ rewriteMode === "en" ? "EN Mode" : "ZH Mode" }}</span>
              </div>

              <div class="rewrite-mode-bar">
                <div class="rewrite-mode-group">
                  <span class="rewrite-mode-label">降重模式</span>
                  <el-radio-group v-model="rewriteMode" size="small">
                    <el-radio-button label="zh">中文模式</el-radio-button>
                    <el-radio-button label="en">英文模式</el-radio-button>
                  </el-radio-group>
                </div>

                <label class="rag-toggle">
                  <span>向量检索</span>
                  <el-switch
                    v-model="useVectorRetrieval"
                    :disabled="!vectorRetrievalAvailable"
                    inline-prompt
                    active-text="开"
                    inactive-text="关"
                  />
                </label>
              </div>

              <p v-if="!vectorRetrievalAvailable" class="mode-hint">
                当前管理员已关闭向量检索，此处暂不可开启。
              </p>

              <div v-if="submissionStatusText" class="submission-status-banner">
                {{ submissionStatusText }}
              </div>

              <div class="editor-box">
                <textarea
                  v-model="sourceText"
                  :placeholder="
                    rewriteMode === 'en'
                      ? '把需要处理的英文论文原文直接粘贴到这里。后续如果要接“论文原文 + 降重报告分段处理”，会从左侧功能入口继续扩展。'
                      : '把需要处理的论文原文直接粘贴到这里。后续如果要接“论文原文 + 降重报告分段处理”，会从左侧功能入口继续扩展。'
                  "
                />
              </div>

              <div class="editor-actions">
                <el-button size="large" :disabled="loading" @click="handleClear">清空内容</el-button>
                <el-button type="primary" size="large" :loading="loading" :disabled="loading" @click="handleRewrite">
                  开始处理
                </el-button>
              </div>
            </article>

            <article class="editor-card">
              <div class="editor-header">
                <div>
                  <p class="editor-label">Output</p>
                  <h2 class="editor-title">论文处理结果</h2>
                </div>
                <span class="muted">{{ loading ? "处理中" : "已就绪" }}</span>
              </div>

              <div class="pane-ruler">
                <span>Rewrite Output</span>
                <span>{{ loading ? "Processing..." : "Ready" }}</span>
              </div>

              <div class="editor-box editor-result">
                {{ resultText || "处理完成后，这里会显示论文改写结果。" }}
              </div>

              <div class="editor-actions">
                <el-button size="large" :disabled="loading" @click="handleCopy">复制结果</el-button>
              </div>
            </article>
          </div>
        </section>

        <aside class="history-panel">
          <div class="history-header">
            <div>
              <p class="section-kicker">History</p>
              <h2 class="panel-title">历史记录</h2>
            </div>
            <div class="history-header-actions">
              <el-button text :loading="syncingFavorites" :disabled="syncingFavorites || loading" @click="syncFavoriteHistory">批量入库</el-button>
              <el-button text :disabled="syncingFavorites || loading" @click="loadHistory">刷新</el-button>
            </div>
          </div>

          <div v-if="history.length" class="history-list">
            <div
              v-for="item in history"
              :key="item.id"
              class="history-item"
              :class="{
                'is-active': activeId === item.id,
                'is-favorite': item.is_favorite,
                'is-synced': item.is_in_vector_db,
                'is-updated': item.history_status === 'updated'
              }"
              @click="applyHistory(item)"
            >
              <div class="history-item-head">
                <div class="history-item-title">
                  <strong>{{ item.name || formatDate(item.created_at) }}</strong>
                  <span v-if="item.history_status === 'updated'" class="updated-badge">已更新入库</span>
                  <span v-else-if="item.is_in_vector_db" class="synced-badge">已入库</span>
                  <span v-else-if="item.is_favorite" class="favorite-badge">待入库</span>
                </div>
                <div class="history-item-actions" @click.stop>
                  <el-button
                    v-if="item.is_favorite"
                    text
                    size="small"
                    type="success"
                    :loading="syncingRecordId === item.id"
                    :disabled="Boolean(syncingRecordId) || syncingFavorites || loading"
                    @click="handleSyncToVectorDb(item)"
                  >
                    {{ item.is_in_vector_db ? "更新入库" : "入库" }}
                  </el-button>
                  <el-button text size="small" :disabled="Boolean(syncingRecordId) || syncingFavorites || loading" @click="openEditDialog(item)">
                    编辑
                  </el-button>
                  <el-button text size="small" type="danger" :disabled="Boolean(syncingRecordId) || syncingFavorites || loading" @click="handleDelete(item)">
                    删除
                  </el-button>
                </div>
              </div>
              <div class="history-text">{{ item.source_text }}</div>
              <div class="history-item-foot">
                <div class="history-meta">
                  {{
                    item.history_status === 'updated'
                      ? `已更新入库${item.vector_db_sync_count ? ` · 第 ${item.vector_db_sync_count} 次` : ""}${item.vector_db_synced_at ? ` · ${formatDate(item.vector_db_synced_at)}` : ""}`
                      : item.is_in_vector_db
                        ? `已入库${item.vector_db_synced_at ? ` · ${formatDate(item.vector_db_synced_at)}` : ""}`
                        : item.is_favorite
                          ? "已标记成功，待入库"
                          : "点击可回填原文与结果"
                  }}
                </div>
                <span class="history-stamp">
                  {{ formatDate(item.updated_at || item.created_at) }}
                </span>
              </div>
            </div>
          </div>
          <div v-else class="history-empty">还没有历史记录，先试一段文本吧。</div>
        </aside>
      </div>
      </main>
      </div>
    </div>

    <HistoryEditDialog
      v-if="editingRecord"
      :record="editingRecord"
      @update="handleHistoryUpdated"
      @close="editingRecord = null"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { useAuthStore } from "../stores/auth";
import http from "../api/http";
import { fetchPublicFlags } from "../api/publicFlags";
import { getErrorMessage } from "../utils/error";
import HistoryEditDialog from "../components/HistoryEditDialog.vue";
import FeatureSidebar from "../components/FeatureSidebar.vue";

const router = useRouter();
const authStore = useAuthStore();
const sourceText = ref("");
const resultText = ref("");
const loading = ref(false);
const history = ref([]);
const activeId = ref(null);
const editingRecord = ref(null);
const rewriteMode = ref("zh");
const useVectorRetrieval = ref(true);
const vectorRetrievalAvailable = ref(true);
const syncingRecordId = ref(null);
const syncingFavorites = ref(false);
const submissionStatusText = computed(() => {
  if (loading.value) {
    return "正在处理论文内容，请勿重复提交。";
  }

  if (syncingFavorites.value) {
    return "正在批量入库，请勿重复点击。";
  }

  if (syncingRecordId.value) {
    return "正在同步当前记录，请勿重复点击。";
  }

  return "";
});

function sortHistoryItems(items) {
  return [...items].sort((a, b) => {
    if ((a.history_status === "updated") !== (b.history_status === "updated")) {
      return a.history_status === "updated" ? -1 : 1;
    }

    if (Boolean(a.is_in_vector_db) !== Boolean(b.is_in_vector_db)) {
      return a.is_in_vector_db ? -1 : 1;
    }

    if (Boolean(a.is_favorite) !== Boolean(b.is_favorite)) {
      return a.is_favorite ? -1 : 1;
    }

    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });
}

function goToSettings() {
  router.push('/settings');
}

async function loadHistory() {
  try {
    const { data } = await http.get("/history");
    history.value = sortHistoryItems(data);
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "加载历史记录失败"));
  }
}

async function handleRewrite() {
  if (loading.value) {
    return;
  }
  if (!sourceText.value.trim()) {
    ElMessage.warning("请先输入原文");
    return;
  }

  loading.value = true;

  try {
    const { data } = await http.post(
      `/rewrite?use_rag=${useVectorRetrieval.value && vectorRetrievalAvailable.value}`,
      {
        source_text: sourceText.value,
        rewrite_mode: rewriteMode.value,
      }
    );
    resultText.value = data.result_text;
    activeId.value = data.id;
    ElMessage.success("处理完成");
    await loadHistory();
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "处理失败"));
  } finally {
    loading.value = false;
  }
}

function handleClear() {
  sourceText.value = "";
  resultText.value = "";
  activeId.value = null;
}

async function handleCopy() {
  if (!resultText.value) {
    ElMessage.warning("当前没有可复制内容");
    return;
  }

  try {
    await navigator.clipboard.writeText(resultText.value);
    ElMessage.success("复制成功");
  } catch (error) {
    ElMessage.error("复制失败");
  }
}

function applyHistory(item) {
  activeId.value = item.id;
  sourceText.value = item.source_text;
  resultText.value = item.result_text;
}

function openEditDialog(item) {
  editingRecord.value = { ...item };
}

function handleHistoryUpdated(updatedRecord) {
  history.value = sortHistoryItems(
    history.value.map((item) =>
      item.id === updatedRecord.id ? updatedRecord : item
    )
  );
}

async function handleSyncToVectorDb(item) {
  if (syncingRecordId.value || syncingFavorites.value || loading.value) {
    return;
  }

  syncingRecordId.value = item.id;
  try {
    const { data } = await http.post(`/rewrite/${item.id}/sync-to-vector-db`);
    ElMessage.success(data.message || "已同步到向量数据库");
    await loadHistory();
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "同步失败"));
  } finally {
    syncingRecordId.value = null;
  }
}

async function syncFavoriteHistory() {
  if (syncingFavorites.value || syncingRecordId.value || loading.value) {
    return;
  }

  syncingFavorites.value = true;
  try {
    const { data } = await http.post("/rewrite/sync-to-vector-db?favorites_only=true");
    ElMessage.success(data.message || "同步完成");
    await loadHistory();
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "同步失败"));
  } finally {
    syncingFavorites.value = false;
  }
}

async function handleDelete(item) {
  try {
    await ElMessageBox.confirm(
      `确认删除“${item.name || formatDate(item.created_at)}”吗？`,
      "删除历史记录",
      {
        confirmButtonText: "删除",
        cancelButtonText: "取消",
        type: "warning"
      }
    );

    await http.delete(`/history/${item.id}`);
    history.value = history.value.filter((record) => record.id !== item.id);

    if (activeId.value === item.id) {
      activeId.value = null;
      sourceText.value = "";
      resultText.value = "";
    }

    ElMessage.success("删除成功");
  } catch (error) {
    if (error === "cancel") {
      return;
    }

    ElMessage.error(getErrorMessage(error, "删除失败"));
  }
}

function handleLogout() {
  authStore.logout();
  router.push("/login");
}

function formatDate(value) {
  return new Date(value).toLocaleString("zh-CN");
}

async function initializeWorkspace() {
  await loadHistory();

  try {
    const flags = await fetchPublicFlags();
    vectorRetrievalAvailable.value = flags.enable_vector_retrieval !== false;
    useVectorRetrieval.value = vectorRetrievalAvailable.value;
  } catch (error) {
    vectorRetrievalAvailable.value = true;
    useVectorRetrieval.value = true;
    console.warn("加载公开功能开关失败，向量检索默认开启", error);
  }
}

onMounted(initializeWorkspace);
</script>

<style scoped>
.rewrite-mode-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.history-item-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.rewrite-mode-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.rewrite-mode-label {
  color: #475569;
  font-size: 13px;
  font-weight: 700;
}

.rag-toggle {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: #475569;
  font-size: 13px;
  font-weight: 700;
}

.mode-hint {
  margin: -4px 0 12px;
  color: #94a3b8;
  font-size: 12px;
}

.submission-status-banner {
  margin: 0 0 14px;
}

.history-item-title {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.history-item-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.history-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.favorite-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.16);
  color: #b45309;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.synced-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.14);
  color: #047857;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.updated-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.14);
  color: #1d4ed8;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.history-item.is-favorite {
  border-color: rgba(245, 158, 11, 0.38);
  background: linear-gradient(135deg, rgba(255, 248, 235, 0.96), rgba(255, 255, 255, 0.92));
  box-shadow: 0 14px 30px rgba(245, 158, 11, 0.12);
}

.history-item.is-favorite .history-meta {
  color: #b45309;
  font-weight: 600;
}

.history-item.is-synced {
  border-color: rgba(16, 185, 129, 0.35);
  background: linear-gradient(135deg, rgba(236, 253, 245, 0.96), rgba(255, 255, 255, 0.92));
  box-shadow: 0 16px 32px rgba(16, 185, 129, 0.12);
}

.history-item.is-synced .history-meta {
  color: #047857;
  font-weight: 600;
}

.history-item.is-updated {
  border-color: rgba(59, 130, 246, 0.35);
  background: linear-gradient(135deg, rgba(239, 246, 255, 0.96), rgba(255, 255, 255, 0.92));
  box-shadow: 0 16px 32px rgba(59, 130, 246, 0.12);
}

.history-item.is-updated .history-meta {
  color: #1d4ed8;
  font-weight: 600;
}
</style>
