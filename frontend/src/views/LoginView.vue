<template>
  <div class="auth-page">
    <div class="auth-shell">
      <section class="auth-hero">
        <div>
          <div class="brand-badge">
            <span class="brand-mark">JS</span>
            <span>JS 论文工作室</span>
          </div>
          <h1>让你的论文改写网站，先从一个顺手又好看的工作台开始。</h1>
          <p>
            这一版先聚焦最核心的体验：登录后输入原文，获取处理结果，并自动保存到历史记录。
          </p>
          <div class="auth-list">
            <div class="auth-list-item">
              <strong>双栏工作区</strong>
              <span class="muted">左侧输入，右侧输出，减少来回跳转。</span>
            </div>
            <div class="auth-list-item">
              <strong>账号体系</strong>
              <span class="muted">你自己先用也没问题，后面扩用户也顺手。</span>
            </div>
            <div class="auth-list-item">
              <strong>历史记录</strong>
              <span class="muted">每次处理都保留下来，方便回看和继续改。</span>
            </div>
          </div>
        </div>
        <div class="hero-strip">
          <div class="hero-strip-grid">
            <div class="hero-stat">
              <strong>登录后直达论文工作区</strong>
              <span class="muted">减少多余页面，保持工具效率。</span>
            </div>
            <div class="hero-stat">
              <strong>后端可接论文改写模型</strong>
              <span class="muted">演示逻辑后续可直接替换真实 API。</span>
            </div>
            <div class="hero-stat">
              <strong>可逐步加功能</strong>
              <span class="muted">支付、批量处理、文件上传后续再扩。</span>
            </div>
          </div>
        </div>
      </section>

      <section class="auth-card">
        <div>
          <p class="section-kicker">Login</p>
          <h2>欢迎回来</h2>
          <p>输入你的邮箱和密码，进入 JS 论文工作室。</p>
        </div>

        <el-form class="auth-form" :model="form" @submit.prevent="handleLogin">
          <el-input v-model="form.email" size="large" placeholder="邮箱" />
          <el-input
            v-model="form.password"
            size="large"
            show-password
            placeholder="密码"
          />
          <el-button type="primary" size="large" :loading="loading" @click="handleLogin">
            登录进入
          </el-button>
        </el-form>

        <div class="auth-footer">
          还没有账号？
          <RouterLink to="/register">立即注册</RouterLink>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter, RouterLink } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../stores/auth";
import { getErrorMessage } from "../utils/error";

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
const form = reactive({
  email: "",
  password: ""
});

async function handleLogin() {
  if (!form.email || !form.password) {
    ElMessage.warning("请先填写邮箱和密码");
    return;
  }

  loading.value = true;

  try {
    await authStore.login(form);
    ElMessage.success("登录成功");
    router.push("/");
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "登录失败"));
  } finally {
    loading.value = false;
  }
}
</script>
