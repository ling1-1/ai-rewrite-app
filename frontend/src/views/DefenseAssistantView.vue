<template>
  <div class="workspace-page">
    <div class="workspace-shell">
      <header class="workspace-topbar">
        <div class="brand-badge">
          <span class="brand-mark">JS</span>
          <div>
            <div>JS 论文工作室</div>
            <small class="muted">Defense Assistant</small>
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
          <section class="workspace-panel">
            <div class="workspace-heading">
              <p class="section-kicker">Defense</p>
              <h1>根据论文内容，直接生成答辩 PPT 文字和对应答辩稿。</h1>
              <p>这一版先聚焦“内容精炼、直观清晰、普通本科生口吻”的答辩辅助流程，后续再继续接入分段降重与报告解析。</p>
            </div>

            <div class="defense-layout">
              <article class="editor-card defense-input-card">
                <div class="editor-header">
                  <div>
                    <p class="editor-label">Input</p>
                    <h2 class="editor-title">论文内容</h2>
                  </div>
                  <span class="muted">{{ thesisText.trim().length }} 字</span>
                </div>

                <div class="defense-brief">
                  <strong>输出规则</strong>
                  <p>系统会优先生成精炼版 PPT 文字，再基于论文和 PPT 生成 3 到 4 分钟答辩稿，避免空话和明显漏洞。</p>
                </div>

                <div class="editor-box">
                  <textarea
                    v-model="thesisText"
                    placeholder="把论文正文、摘要、结论或核心章节粘贴到这里。内容越完整，生成的 PPT 和稿子越稳。"
                  />
                </div>

                <div class="editor-actions defense-actions">
                  <el-button size="large" @click="handleClear">清空内容</el-button>
                  <el-button size="large" :loading="pptLoading" @click="generatePpt">
                    {{ pptLoading ? "生成中..." : "生成答辩PPT" }}
                  </el-button>
                  <el-button type="primary" size="large" :loading="flowLoading" @click="generateFullFlow">
                    {{ flowLoading ? "生成中..." : "一键生成完整流程" }}
                  </el-button>
                </div>
              </article>

              <article class="editor-card">
                <div class="editor-header">
                  <div>
                    <p class="editor-label">PPT</p>
                    <h2 class="editor-title">答辩 PPT 文字内容</h2>
                  </div>
                  <span class="muted">{{ pptLoading ? "生成中" : "可编辑" }}</span>
                </div>

                <div class="editor-box">
                  <textarea
                    v-model="pptContent"
                    placeholder="生成后会在这里展示 5 个板块的答辩 PPT 文字内容。你也可以手动调整。"
                  />
                </div>

                <div class="editor-actions defense-actions">
                  <el-button size="large" @click="copyText(pptContent, 'PPT内容')">复制 PPT 内容</el-button>
                  <el-button type="primary" size="large" :loading="speechLoading" @click="generateSpeech">
                    {{ speechLoading ? "生成中..." : "生成答辩稿" }}
                  </el-button>
                </div>
              </article>

              <article class="editor-card">
                <div class="editor-header">
                  <div>
                    <p class="editor-label">Speech</p>
                    <h2 class="editor-title">3-4 分钟答辩稿</h2>
                  </div>
                  <span class="muted">{{ speechLoading || flowLoading ? "生成中" : "可复制" }}</span>
                </div>

                <div class="editor-box editor-result">
                  {{ speechContent || "生成后，这里会展示和答辩 PPT 对应的 3-4 分钟答辩稿。" }}
                </div>

                <div class="editor-actions defense-actions">
                  <el-button size="large" @click="copyText(speechContent, '答辩稿')">复制答辩稿</el-button>
                </div>
              </article>
            </div>
          </section>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../stores/auth";
import http from "../api/http";
import { getErrorMessage } from "../utils/error";
import FeatureSidebar from "../components/FeatureSidebar.vue";

const router = useRouter();
const authStore = useAuthStore();

const thesisText = ref("");
const pptContent = ref("");
const speechContent = ref("");
const pptLoading = ref(false);
const speechLoading = ref(false);
const flowLoading = ref(false);

function ensureThesisText() {
  if (!thesisText.value.trim()) {
    ElMessage.warning("请先输入论文内容");
    return false;
  }
  return true;
}

async function generatePpt() {
  if (!ensureThesisText()) {
    return;
  }

  pptLoading.value = true;
  try {
    const { data } = await http.post("/defense/ppt", {
      thesis_text: thesisText.value
    });
    pptContent.value = data.ppt_content;
    ElMessage.success("答辩PPT内容已生成");
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "生成答辩PPT失败"));
  } finally {
    pptLoading.value = false;
  }
}

async function generateSpeech() {
  if (!ensureThesisText()) {
    return;
  }
  if (!pptContent.value.trim()) {
    ElMessage.warning("请先生成或填写答辩PPT内容");
    return;
  }

  speechLoading.value = true;
  try {
    const { data } = await http.post("/defense/speech", {
      thesis_text: thesisText.value,
      ppt_content: pptContent.value
    });
    speechContent.value = data.speech_content;
    ElMessage.success("答辩稿已生成");
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "生成答辩稿失败"));
  } finally {
    speechLoading.value = false;
  }
}

async function generateFullFlow() {
  if (!ensureThesisText()) {
    return;
  }

  flowLoading.value = true;
  try {
    const { data } = await http.post("/defense/flow", {
      thesis_text: thesisText.value
    });
    pptContent.value = data.ppt_content;
    speechContent.value = data.speech_content;
    ElMessage.success("答辩流程内容已生成");
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "生成失败"));
  } finally {
    flowLoading.value = false;
  }
}

function handleClear() {
  thesisText.value = "";
  pptContent.value = "";
  speechContent.value = "";
}

async function copyText(content, label) {
  if (!content) {
    ElMessage.warning(`当前没有可复制的${label}`);
    return;
  }

  try {
    await navigator.clipboard.writeText(content);
    ElMessage.success(`${label}复制成功`);
  } catch (error) {
    ElMessage.error(`${label}复制失败`);
  }
}

function goToSettings() {
  router.push("/settings");
}

function handleLogout() {
  authStore.logout();
  router.push("/login");
}
</script>
