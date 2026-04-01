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

      <div class="workspace-grid">
        <section class="workspace-panel">
          <div class="workspace-heading">
            <p class="section-kicker">Workspace</p>
            <h1>左边输入论文原文，右边查看处理结果，下面保留你的历史记录。</h1>
            <p>这一版先聚焦论文改写最常用的流程，让整个工作区更直接、更顺手。</p>
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

              <div class="upload-toolbar">
                <input
                  ref="fileInput"
                  class="file-input"
                  type="file"
                  accept=".txt,.md,.pdf,.docx"
                  @change="handleFileChange"
                />
                <div>
                  <strong>支持上传 .txt / .md / .pdf / .docx</strong>
                  <div class="muted">
                    {{ uploadedFileName ? `当前文件：${uploadedFileName}` : "上传后会自动提取正文到输入框。" }}
                  </div>
                </div>
                <el-button size="large" :loading="uploading" @click="openFilePicker">
                  {{ uploading ? "解析中..." : "上传文件" }}
                </el-button>
              </div>

              <div class="editor-box">
                <textarea
                  v-model="sourceText"
                  placeholder="把需要处理的论文原文粘贴到这里。"
                />
              </div>

              <div class="editor-actions">
                <el-button size="large" @click="handleClear">清空内容</el-button>
                <el-button type="primary" size="large" :loading="loading" @click="handleRewrite">
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

              <div class="editor-box editor-result">
                {{ resultText || "处理完成后，这里会显示论文改写结果。" }}
              </div>

              <div class="editor-actions">
                <el-button size="large" @click="handleCopy">复制结果</el-button>
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
            <el-button text @click="loadHistory">刷新</el-button>
          </div>

          <div v-if="history.length" class="history-list">
            <div
              v-for="item in history"
              :key="item.id"
              class="history-item"
              :class="{ 'is-active': activeId === item.id }"
              @click="applyHistory(item)"
            >
              <strong>{{ formatDate(item.created_at) }}</strong>
              <div class="history-text">{{ item.source_text }}</div>
              <div class="history-meta">点击可回填原文与结果</div>
            </div>
          </div>
          <div v-else class="history-empty">还没有历史记录，先试一段文本吧。</div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../stores/auth";
import http from "../api/http";
import { getErrorMessage } from "../utils/error";

const router = useRouter();
const authStore = useAuthStore();
const sourceText = ref("");
const resultText = ref("");
const loading = ref(false);
const uploading = ref(false);
const history = ref([]);
const activeId = ref(null);
const uploadedFileName = ref("");
const fileInput = ref(null);

function goToSettings() {
  router.push('/settings');
}

async function loadHistory() {
  try {
    const { data } = await http.get("/history");
    history.value = data;
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "加载历史记录失败"));
  }
}

async function handleRewrite() {
  if (!sourceText.value.trim()) {
    ElMessage.warning("请先输入原文");
    return;
  }

  loading.value = true;

  try {
    const { data } = await http.post("/rewrite", {
      source_text: sourceText.value
    });
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

function openFilePicker() {
  fileInput.value?.click();
}

async function handleFileChange(event) {
  const file = event.target.files?.[0];
  if (!file) {
    return;
  }

  uploading.value = true;

  try {
    const formData = new FormData();
    formData.append("file", file);

    const { data } = await http.post("/rewrite/extract-file", formData);
    sourceText.value = data.source_text;
    resultText.value = "";
    activeId.value = null;
    uploadedFileName.value = data.filename;
    ElMessage.success(`已导入 ${data.filename}`);
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "文件解析失败"));
  } finally {
    uploading.value = false;
    event.target.value = "";
  }
}

function handleClear() {
  sourceText.value = "";
  resultText.value = "";
  activeId.value = null;
  uploadedFileName.value = "";
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
  uploadedFileName.value = "";
}

function handleLogout() {
  authStore.logout();
  router.push("/login");
}

function formatDate(value) {
  return new Date(value).toLocaleString("zh-CN");
}

onMounted(loadHistory);
</script>
