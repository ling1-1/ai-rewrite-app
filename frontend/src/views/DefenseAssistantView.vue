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
          <section class="workspace-panel defense-page-panel">
            <div class="workspace-heading defense-heading">
              <p class="section-kicker">Defense</p>
              <h1>答辩 PPT 内容和答辩稿，分开生成，也能一键走完整流程。</h1>
              <p>这页更适合“先看结构，再微调内容”。PPT 优先按板块预览，答辩稿按朗读节奏展示，不再是三块纯文本大框。</p>
            </div>

            <div class="defense-hero-strip">
              <div class="defense-hero-item">
                <strong>先生成结构</strong>
                <span>先拿到 5 个 PPT 板块，再看哪里要补。</span>
              </div>
              <div class="defense-hero-item">
                <strong>再生成稿子</strong>
                <span>稿子会和 PPT 对齐，方便你按页讲。</span>
              </div>
              <div class="defense-hero-item">
                <strong>保留扩展入口</strong>
                <span>后续“论文+报告分段处理”会继续接在这里。</span>
              </div>
            </div>

            <div class="defense-workbench">
              <section class="defense-control-panel">
                <article class="editor-card defense-input-card">
                  <div class="editor-header">
                    <div>
                      <p class="editor-label">Input</p>
                      <h2 class="editor-title">论文内容</h2>
                    </div>
                    <span class="muted">{{ thesisText.trim().length }} 字</span>
                  </div>

                  <div class="defense-brief">
                    <strong>建议输入内容</strong>
                    <p>优先放摘要、研究背景、方法、结论和创新点。内容不需要特别完整，但至少要让模型能看清论文在研究什么、做出了什么结果。</p>
                  </div>

                  <div class="editor-box defense-thesis-box">
                    <textarea
                      v-model="thesisText"
                      placeholder="把论文正文、摘要、结论或核心章节粘贴到这里。内容越完整，生成的 PPT 和稿子越稳。"
                    />
                  </div>

                  <div class="editor-actions defense-actions">
                    <el-button size="large" @click="handleClear">清空内容</el-button>
                    <el-button size="large" :loading="pptLoading" @click="generatePpt">
                      {{ pptLoading ? "生成中..." : "只生成PPT" }}
                    </el-button>
                    <el-button type="primary" size="large" :loading="flowLoading" @click="generateFullFlow">
                      {{ flowLoading ? "生成中..." : "一键生成完整流程" }}
                    </el-button>
                  </div>
                </article>
              </section>

              <section class="defense-output-panel">
                <article class="editor-card defense-preview-card">
                  <div class="editor-header defense-section-header">
                    <div>
                      <p class="editor-label">PPT</p>
                      <h2 class="editor-title">答辩 PPT 内容</h2>
                    </div>
                    <div class="defense-toolbar">
                      <div class="view-toggle">
                        <button
                          class="view-toggle-btn"
                          :class="{ 'is-active': pptViewMode === 'preview' }"
                          @click="pptViewMode = 'preview'"
                        >
                          预览模式
                        </button>
                        <button
                          class="view-toggle-btn"
                          :class="{ 'is-active': pptViewMode === 'edit' }"
                          @click="pptViewMode = 'edit'"
                        >
                          编辑原文
                        </button>
                      </div>
                      <span class="muted">{{ pptLoading || flowLoading ? "生成中" : "可编辑" }}</span>
                    </div>
                  </div>

                  <div v-if="pptViewMode === 'preview'" class="ppt-preview-board">
                    <div v-if="parsedPptSections.length" class="ppt-slide-grid">
                      <article
                        v-for="section in parsedPptSections"
                        :key="section.title"
                        class="ppt-slide-card"
                      >
                        <div class="ppt-slide-index">{{ section.index }}</div>
                        <h3>{{ section.title }}</h3>
                        <p v-for="(line, lineIndex) in section.lines" :key="`${section.title}-${lineIndex}`">
                          {{ line }}
                        </p>
                      </article>
                    </div>
                    <div v-else class="defense-empty-state">
                      <strong>还没有可预览的 PPT 内容</strong>
                      <p>先生成 PPT，或者切到“编辑原文”手动填写。生成完成后，这里会自动按 5 个板块拆成更像 PPT 的预览卡片。</p>
                    </div>
                  </div>

                  <div v-else class="editor-box defense-edit-box">
                    <textarea
                      v-model="pptContent"
                      placeholder="生成后会在这里展示 5 个板块的答辩 PPT 文字内容。你也可以直接手动修改。"
                    />
                  </div>

                  <div class="editor-actions defense-actions">
                    <el-button size="large" @click="copyText(pptContent, 'PPT内容')">复制 PPT 内容</el-button>
                    <el-button type="primary" size="large" :loading="speechLoading" @click="generateSpeech">
                      {{ speechLoading ? "生成中..." : "生成答辩稿" }}
                    </el-button>
                  </div>
                </article>

                <article class="editor-card defense-preview-card">
                  <div class="editor-header defense-section-header">
                    <div>
                      <p class="editor-label">Speech</p>
                      <h2 class="editor-title">3-4 分钟答辩稿</h2>
                    </div>
                    <span class="muted">{{ speechLoading || flowLoading ? "生成中" : "朗读视图" }}</span>
                  </div>

                  <div class="speech-reading-board">
                    <div v-if="speechParagraphs.length" class="speech-reading-content">
                      <p
                        v-for="(paragraph, index) in speechParagraphs"
                        :key="`speech-${index}`"
                        class="speech-paragraph"
                      >
                        {{ paragraph }}
                      </p>
                    </div>
                    <div v-else class="defense-empty-state">
                      <strong>还没有答辩稿</strong>
                      <p>先生成 PPT，再生成答辩稿。这里会按朗读节奏显示，不会挤成一整块难看的长文本。</p>
                    </div>
                  </div>

                  <div class="editor-actions defense-actions">
                    <el-button size="large" @click="copyText(speechContent, '答辩稿')">复制答辩稿</el-button>
                  </div>
                </article>
              </section>
            </div>
          </section>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
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
const pptViewMode = ref("preview");

const fallbackSectionTitles = [
  "研究背景、目的与意义",
  "研究内容重点介绍",
  "研究成果",
  "个人观点",
  "致谢",
];

const parsedPptSections = computed(() => {
  const content = pptContent.value.trim();
  if (!content) {
    return [];
  }

  const normalized = content
    .replace(/\r/g, "")
    .replace(/（/g, "(")
    .replace(/）/g, ")");

  const blocks = normalized
    .split(/\n(?=[一二三四五六七八九十]+、)/)
    .map((block) => block.trim())
    .filter(Boolean);

  if (blocks.length) {
    return blocks.map((block, index) => {
      const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
      const titleLine = lines.shift() || fallbackSectionTitles[index] || `第 ${index + 1} 部分`;
      return {
        index: index + 1,
        title: titleLine.replace(/^[一二三四五六七八九十]+、\s*/, ""),
        lines: lines.length ? lines : ["建议根据论文内容补充这一页的重点内容。"],
      };
    });
  }

  const paragraphs = normalized.split(/\n{2,}/).map((item) => item.trim()).filter(Boolean);
  if (!paragraphs.length) {
    return [];
  }

  return paragraphs.slice(0, 5).map((paragraph, index) => ({
    index: index + 1,
    title: fallbackSectionTitles[index] || `第 ${index + 1} 部分`,
    lines: paragraph.split("\n").map((line) => line.trim()).filter(Boolean),
  }));
});

const speechParagraphs = computed(() =>
  speechContent.value
    .split(/\n{2,}/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean)
);

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
    pptViewMode.value = "preview";
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
    pptViewMode.value = "preview";
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
  pptViewMode.value = "preview";
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
