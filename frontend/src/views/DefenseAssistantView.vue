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

                <div class="defense-toolbar thesis-toolbar">
                  <div class="view-toggle">
                    <button
                      class="view-toggle-btn"
                      :class="{ 'is-active': thesisViewMode === 'preview' }"
                      @click="thesisViewMode = 'preview'"
                    >
                      正文预览
                    </button>
                    <button
                      class="view-toggle-btn"
                      :class="{ 'is-active': thesisViewMode === 'edit' }"
                      @click="thesisViewMode = 'edit'"
                    >
                      手动编辑
                    </button>
                  </div>
                </div>

                <div class="defense-brief">
                  <strong>建议输入内容</strong>
                  <p>优先放摘要、研究背景、方法、结论和创新点。内容不需要特别完整，但至少要让模型能看清论文在研究什么、做出了什么结果。</p>
                </div>

                <div v-if="busyStatusText" class="submission-status-banner">
                  {{ busyStatusText }}
                </div>

                <div class="defense-config-panel">
                  <div class="defense-config-head">
                    <strong>生成配置</strong>
                    <span class="muted">这里改的是本次生成参数，不会覆盖后台默认提示词。</span>
                  </div>

                  <div class="defense-preset-bar">
                    <span class="muted">快速预设</span>
                    <div class="defense-preset-actions">
                      <el-button size="small" :disabled="isBusy" @click="applyPreset('compact')">3分钟精简版</el-button>
                      <el-button size="small" :disabled="isBusy" @click="applyPreset('standard')">4分钟标准版</el-button>
                      <el-button size="small" :disabled="isBusy" @click="applyPreset('steady')">稳妥答辩版</el-button>
                      <el-button size="small" type="primary" :disabled="isBusy" @click="saveGenerationDefaults">保存为默认配置</el-button>
                    </div>
                  </div>

                  <div class="defense-config-grid">
                    <label class="defense-config-field">
                      <span>PPT 页数</span>
                      <input v-model.number="generationConfig.ppt_page_count" type="number" min="3" max="12" class="form-input" />
                    </label>

                    <label class="defense-config-field">
                      <span>答辩时长（分钟）</span>
                      <input v-model.number="generationConfig.speech_duration_minutes" type="number" min="2" max="10" class="form-input" />
                    </label>

                    <label class="defense-config-field">
                      <span>语言风格</span>
                      <select v-model="generationConfig.language_style" class="form-input">
                        <option value="更直白">更直白</option>
                        <option value="更正式">更正式</option>
                        <option value="更稳妥">更稳妥</option>
                      </select>
                    </label>

                    <label class="defense-config-field">
                      <span>表达视角</span>
                      <select v-model="generationConfig.persona_style" class="form-input">
                        <option value="普通本科生">普通本科生</option>
                        <option value="稍正式一点">稍正式一点</option>
                        <option value="更谦虚稳妥">更谦虚稳妥</option>
                      </select>
                    </label>

                    <label class="defense-config-field">
                      <span>内容密度</span>
                      <select v-model="generationConfig.content_density" class="form-input">
                        <option value="精简">精简</option>
                        <option value="标准">标准</option>
                        <option value="稍详细">稍详细</option>
                      </select>
                    </label>
                  </div>

                  <div class="defense-config-switches">
                    <label class="checkbox-label compact-checkbox">
                      <input v-model="generationConfig.include_personal_view" type="checkbox" class="form-checkbox" />
                      <span>包含个人观点</span>
                    </label>

                    <label class="checkbox-label compact-checkbox">
                      <input v-model="generationConfig.include_acknowledgement" type="checkbox" class="form-checkbox" />
                      <span>包含致谢</span>
                    </label>
                  </div>

                  <label class="defense-config-field defense-config-outline">
                    <span>PPT 大纲</span>
                    <textarea
                      v-model="generationConfig.ppt_outline"
                      class="form-textarea defense-outline-input"
                      rows="7"
                      placeholder="一行一个部分，例如：&#10;一、研究背景、目的与意义&#10;二、研究内容重点介绍&#10;三、研究成果"
                    ></textarea>
                  </label>
                </div>

                <div class="upload-toolbar defense-upload-toolbar">
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
                      {{ uploadedFileName ? `当前文件：${uploadedFileName}` : "上传后会自动提取正文到论文内容中。" }}
                    </div>
                  </div>
                  <div class="defense-upload-actions">
                    <el-button size="large" :loading="uploading" :disabled="isBusy" @click="openFilePicker">
                      {{ uploading ? "解析中..." : uploadedFileName ? "替换文件" : "上传论文" }}
                    </el-button>
                    <el-button
                      v-if="uploadedFileName"
                      size="large"
                      :disabled="isBusy"
                      @click="clearUploadedFile"
                    >
                      清空文件
                    </el-button>
                  </div>
                </div>

                <div v-if="uploadedFileName || thesisText.trim()" class="defense-file-meta">
                  <span v-if="uploadedFileName">文件：{{ uploadedFileName }}</span>
                  <span>正文长度：{{ thesisText.trim().length }} 字</span>
                </div>

                <div v-if="thesisViewMode === 'preview'" class="document-preview-window">
                  <div v-if="thesisText.trim()" class="document-preview-content">
                    {{ thesisText }}
                  </div>
                  <div v-else class="defense-empty-state document-preview-empty">
                    <strong>还没有可预览的论文正文</strong>
                    <p>上传论文文件后，会先在这里展示提取出的正文内容。你也可以切到“手动编辑”直接粘贴文本。</p>
                  </div>
                </div>

                <div v-else class="editor-box defense-thesis-box">
                  <textarea
                    v-model="thesisText"
                    placeholder="把论文正文、摘要、结论或核心章节粘贴到这里。内容越完整，生成的 PPT 和稿子越稳。"
                  />
                </div>

                  <div class="editor-actions defense-actions">
                    <el-button size="large" :disabled="isBusy" @click="handleClear">清空内容</el-button>
                    <el-button size="large" :loading="pptLoading" :disabled="isBusy" @click="generatePpt">
                      {{ pptLoading ? "生成中..." : "只生成PPT" }}
                    </el-button>
                    <el-button type="primary" size="large" :loading="flowLoading" :disabled="isBusy" @click="generateFullFlow">
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

                  <div v-if="pptPageMismatchWarning" class="submission-status-banner warning-banner">
                    {{ pptPageMismatchWarning }}
                  </div>

                  <div v-if="pptViewMode === 'preview'" class="ppt-preview-board">
                    <div v-if="parsedPptSections.length" class="ppt-slide-grid">
                      <article
                        v-for="section in parsedPptSections"
                        :key="section.title"
                        class="ppt-slide-card"
                      >
                        <div class="ppt-slide-head">
                          <div class="ppt-slide-index">{{ section.index }}</div>
                          <span class="ppt-slide-chip">答辩PPT</span>
                        </div>
                        <h3>{{ section.title }}</h3>
                        <ul class="ppt-slide-bullets">
                          <li v-for="(line, lineIndex) in section.lines" :key="`${section.title}-${lineIndex}`">
                            {{ line }}
                          </li>
                        </ul>
                        <div class="ppt-slide-footer">第 {{ section.index }} 页 · 适合直接放进幻灯片</div>
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
                    <el-button size="large" :disabled="isBusy" @click="copyText(pptContent, 'PPT内容')">复制 PPT 内容</el-button>
                    <el-button type="primary" size="large" :loading="speechLoading" :disabled="isBusy" @click="generateSpeech">
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
                    <el-button size="large" :disabled="isBusy" @click="copyText(speechContent, '答辩稿')">复制答辩稿</el-button>
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
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../stores/auth";
import http from "../api/http";
import { getErrorMessage } from "../utils/error";
import FeatureSidebar from "../components/FeatureSidebar.vue";

const router = useRouter();
const authStore = useAuthStore();
const DEFENSE_DEFAULTS_KEY = "defense_generation_defaults";

const thesisText = ref("");
const pptContent = ref("");
const speechContent = ref("");
const uploadedFileName = ref("");
const uploading = ref(false);
const pptLoading = ref(false);
const speechLoading = ref(false);
const flowLoading = ref(false);
const pptViewMode = ref("preview");
const thesisViewMode = ref("preview");
const fileInput = ref(null);
const generationConfig = ref({
  ppt_page_count: 5,
  ppt_outline: [
    "一、研究背景、目的与意义",
    "二、研究内容重点介绍",
    "三、研究成果",
    "四、个人观点",
    "五、致谢",
  ].join("\n"),
  speech_duration_minutes: 4,
  language_style: "更直白",
  persona_style: "普通本科生",
  content_density: "精简",
  include_acknowledgement: true,
  include_personal_view: true,
});
const isBusy = computed(
  () => uploading.value || pptLoading.value || speechLoading.value || flowLoading.value
);
const busyStatusText = computed(() => {
  if (uploading.value) {
    return "正在解析论文文件，请勿重复提交。";
  }

  if (flowLoading.value) {
    return "正在生成完整答辩流程，请勿重复提交。";
  }

  if (pptLoading.value) {
    return "正在生成答辩PPT，请勿重复提交。";
  }

  if (speechLoading.value) {
    return "正在生成答辩稿，请勿重复提交。";
  }

  return "";
});

const DEFENSE_PRESETS = {
  compact: {
    ppt_page_count: 5,
    speech_duration_minutes: 3,
    language_style: "更直白",
    persona_style: "普通本科生",
    content_density: "精简",
    include_acknowledgement: true,
    include_personal_view: true,
    ppt_outline: [
      "一、研究背景、目的与意义",
      "二、研究内容重点介绍",
      "三、研究成果",
      "四、个人观点",
      "五、致谢",
    ].join("\n"),
  },
  standard: {
    ppt_page_count: 5,
    speech_duration_minutes: 4,
    language_style: "更直白",
    persona_style: "普通本科生",
    content_density: "标准",
    include_acknowledgement: true,
    include_personal_view: true,
    ppt_outline: [
      "一、研究背景、目的与意义",
      "二、研究思路与方法",
      "三、研究内容重点介绍",
      "四、研究成果",
      "五、个人观点与致谢",
    ].join("\n"),
  },
  steady: {
    ppt_page_count: 6,
    speech_duration_minutes: 4,
    language_style: "更稳妥",
    persona_style: "更谦虚稳妥",
    content_density: "精简",
    include_acknowledgement: true,
    include_personal_view: true,
    ppt_outline: [
      "一、研究背景",
      "二、研究目的与意义",
      "三、研究内容与方法",
      "四、研究成果",
      "五、个人观点",
      "六、致谢",
    ].join("\n"),
  },
};

const fallbackSectionTitles = [
  "研究背景、目的与意义",
  "研究内容重点介绍",
  "研究成果",
  "个人观点",
  "致谢",
];

const outlineSectionTitles = computed(() =>
  generationConfig.value.ppt_outline
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => item.replace(/^[一二三四五六七八九十]+、\s*/, ""))
);

const parsedPptSections = computed(() => {
  const content = pptContent.value.trim();
  if (!content) {
    return [];
  }

  const normalized = content
    .replace(/\r/g, "")
    .replace(/（/g, "(")
    .replace(/）/g, ")");

  const pageBlocks = normalized
    .split(/\n(?=【第\d+页】)/)
    .map((block) => block.trim())
    .filter(Boolean);

  if (pageBlocks.length) {
    return pageBlocks.map((block, index) => {
      const lines = block
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean);

      const markerLine = lines.shift() || "";
      const titleLine = lines.shift() || outlineSectionTitles.value[index] || fallbackSectionTitles[index] || `第 ${index + 1} 页`;
      const cleanedLines = lines.map((line) => line.replace(/^[-*•]\s*/, "").trim()).filter(Boolean);

      return {
        index: index + 1,
        title: titleLine.replace(/^【第\d+页】/, "").trim(),
        lines: cleanedLines.length ? cleanedLines : ["建议根据论文内容补充这一页的重点内容。"],
        marker: markerLine,
      };
    });
  }

  const markdownSectionBlocks = normalized
    .split(/\n(?=\*\*第[一二三四五六七八九十0-9]+部分[：:].*\*\*)/)
    .map((block) => block.trim())
    .filter(Boolean);

  if (markdownSectionBlocks.length > 1) {
    return markdownSectionBlocks.map((block, index) => {
      const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
      const titleLine = lines.shift() || outlineSectionTitles.value[index] || fallbackSectionTitles[index] || `第 ${index + 1} 部分`;
      return {
        index: index + 1,
        title: titleLine.replace(/^\*\*|\*\*$/g, "").replace(/^第[一二三四五六七八九十0-9]+部分[：:]\s*/, "").trim(),
        lines: lines.length ? lines : ["建议根据论文内容补充这一页的重点内容。"],
      };
    });
  }

  const blocks = normalized
    .split(/\n(?=[一二三四五六七八九十]+、)/)
    .map((block) => block.trim())
    .filter(Boolean);

  if (blocks.length) {
    return blocks.map((block, index) => {
      const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
      const titleLine = lines.shift() || outlineSectionTitles.value[index] || fallbackSectionTitles[index] || `第 ${index + 1} 部分`;
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
    title: outlineSectionTitles.value[index] || fallbackSectionTitles[index] || `第 ${index + 1} 部分`,
    lines: paragraph.split("\n").map((line) => line.trim()).filter(Boolean),
  }));
});

const pptPageMismatchWarning = computed(() => {
  const expectedCount = Number(generationConfig.value.ppt_page_count) || 0;
  const actualCount = parsedPptSections.value.length;

  if (!pptContent.value.trim() || !expectedCount || !actualCount) {
    return "";
  }

  if (expectedCount === actualCount) {
    return "";
  }

  return `当前预设为 ${expectedCount} 页，但本次只解析到 ${actualCount} 页。建议重新生成，或调整提示词和大纲后再试。`;
});

function buildGenerationPayload(extra = {}) {
  return {
    ...generationConfig.value,
    ...extra,
  };
}

function applyPreset(name) {
  const preset = DEFENSE_PRESETS[name];
  if (!preset) {
    return;
  }
  generationConfig.value = {
    ...generationConfig.value,
    ...preset,
  };
  ElMessage.success("已应用预设模板");
}

async function loadGenerationDefaults() {
  try {
    const rawValue = localStorage.getItem(DEFENSE_DEFAULTS_KEY);
    if (!rawValue) {
      return;
    }

    const data = JSON.parse(rawValue);
    generationConfig.value = {
      ...generationConfig.value,
      ...data,
    };
  } catch (error) {
    console.warn("加载本地答辩默认配置失败，使用页面默认值", error);
  }
}

async function saveGenerationDefaults() {
  try {
    localStorage.setItem(
      DEFENSE_DEFAULTS_KEY,
      JSON.stringify(buildGenerationPayload())
    );
    ElMessage.success("已保存为默认配置");
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "保存默认配置失败"));
  }
}

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
  if (isBusy.value) {
    return;
  }
  if (!ensureThesisText()) {
    return;
  }

  pptLoading.value = true;
  try {
    const { data } = await http.post("/defense/ppt", {
      thesis_text: thesisText.value,
      ...buildGenerationPayload(),
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
  if (isBusy.value) {
    return;
  }
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
      ppt_content: pptContent.value,
      ...buildGenerationPayload(),
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
  if (isBusy.value) {
    return;
  }
  if (!ensureThesisText()) {
    return;
  }

  flowLoading.value = true;
  try {
    const { data } = await http.post("/defense/flow", {
      thesis_text: thesisText.value,
      ...buildGenerationPayload(),
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

function openFilePicker() {
  if (isBusy.value) {
    return;
  }
  fileInput.value?.click();
}

async function handleFileChange(event) {
  if (isBusy.value) {
    event.target.value = "";
    return;
  }
  const file = event.target.files?.[0];
  if (!file) {
    return;
  }

  uploading.value = true;

  try {
    const formData = new FormData();
    formData.append("file", file);

    const { data } = await http.post("/rewrite/extract-file", formData);
    thesisText.value = data.source_text;
    uploadedFileName.value = data.filename;
    thesisViewMode.value = "preview";
    ElMessage.success(`已导入 ${data.filename}`);
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "论文文件解析失败"));
  } finally {
    uploading.value = false;
    event.target.value = "";
  }
}

function handleClear() {
  thesisText.value = "";
  pptContent.value = "";
  speechContent.value = "";
  pptViewMode.value = "preview";
  thesisViewMode.value = "preview";
  uploadedFileName.value = "";
}

function clearUploadedFile() {
  uploadedFileName.value = "";
  thesisText.value = "";
  ElMessage.success("已清空上传内容");
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

onMounted(loadGenerationDefaults);
</script>
