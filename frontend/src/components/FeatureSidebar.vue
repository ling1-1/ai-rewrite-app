<template>
  <aside class="feature-sidebar">
    <div class="feature-sidebar-card">
      <p class="feature-sidebar-kicker">功能入口</p>
      <div class="feature-sidebar-list">
        <button
          v-for="item in featureItems"
          :key="item.route"
          class="feature-nav-item"
          :class="{ 'is-active': route.name === item.route }"
          @click="router.push({ name: item.route })"
        >
          <strong>{{ item.title }}</strong>
          <span>{{ item.description }}</span>
        </button>
      </div>

      <div class="feature-sidebar-note">
        <strong>后续扩展预留</strong>
        <p>这里后面可以继续挂“论文原文 + 降重报告 -> 提取需降重片段 -> 分段降重”的工作流，不会和当前历史记录混在一起。</p>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const featureItems = [
  {
    route: "workspace",
    title: "论文降重",
    description: "保留当前改写与历史记录工作台"
  },
  {
    route: "defense",
    title: "答辩辅助",
    description: "生成答辩 PPT 文字和 3-4 分钟稿子"
  }
];
</script>
