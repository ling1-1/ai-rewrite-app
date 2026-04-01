<template>
  <div class="auth-page">
    <div class="auth-shell">
      <section class="auth-hero">
        <div>
          <div class="brand-badge">
            <span class="brand-mark">JS</span>
            <span>JS 论文工作室</span>
          </div>
          <h1>先把论文工作室的账号体系搭起来，后面扩展功能就会轻松很多。</h1>
          <p>
            当前版本只做最必要的注册和登录，保持产品轻巧，同时给历史记录和个人使用留好结构。
          </p>
        </div>
        <div class="hero-strip">
          <div class="hero-strip-grid">
            <div class="hero-stat">
              <strong>注册即用</strong>
              <span class="muted">创建后直接登录进入工作台。</span>
            </div>
            <div class="hero-stat">
              <strong>后续可扩</strong>
              <span class="muted">可以继续加验证码、手机号或第三方登录。</span>
            </div>
            <div class="hero-stat">
              <strong>个人版优先</strong>
              <span class="muted">先保证你自己稳定使用，再扩其他人。</span>
            </div>
          </div>
        </div>
      </section>

      <section class="auth-card">
        <div>
          <p class="section-kicker">Register</p>
          <h2>创建账号</h2>
          <p>填完下面的信息，就可以开始使用你的改写工作台。</p>
        </div>

        <el-form class="auth-form" :model="form" @submit.prevent="handleRegister">
          <el-input v-model="form.username" size="large" placeholder="用户名" />
          <el-input v-model="form.email" size="large" placeholder="邮箱" />
          <el-input
            v-model="form.password"
            size="large"
            show-password
            placeholder="密码"
          />
          <el-button type="primary" size="large" :loading="loading" @click="handleRegister">
            注册账号
          </el-button>
        </el-form>

        <div class="auth-footer">
          已经有账号？
          <RouterLink to="/login">去登录</RouterLink>
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
  username: "",
  email: "",
  password: ""
});

async function handleRegister() {
  if (!form.username || !form.email || !form.password) {
    ElMessage.warning("请把注册信息填写完整");
    return;
  }

  loading.value = true;

  try {
    await authStore.register(form);
    ElMessage.success("注册成功，请登录");
    router.push("/login");
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "注册失败"));
  } finally {
    loading.value = false;
  }
}
</script>
