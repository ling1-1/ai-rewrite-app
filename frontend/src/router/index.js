import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { getCachedRegistrationFlag } from "../api/publicFlags";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import WorkspaceView from "../views/WorkspaceView.vue";
import SettingsView from "../views/SettingsView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginView },
    { path: "/register", name: "register", component: RegisterView },
    { path: "/", name: "workspace", component: WorkspaceView, meta: { requiresAuth: true } },
    { path: "/settings", name: "settings", component: SettingsView, meta: { requiresAuth: true, requiresAdmin: true } }
  ]
});

router.beforeEach((to) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.token) {
    return { name: "login" };
  }

  if (to.meta.requiresAdmin) {
    // 检查是否是管理员
    const isAdmin = authStore.user?.is_admin === true || authStore.isAdmin === true;
    if (!isAdmin) {
      alert('权限不足：需要管理员权限');
      return { name: "workspace" };
    }
  }

  if ((to.name === "login" || to.name === "register") && authStore.token) {
    return { name: "workspace" };
  }

  if (to.name === "register") {
    const cachedFlag = getCachedRegistrationFlag();
    if (cachedFlag === false) {
      return { name: "login" };
    }
  }

  return true;
});

export default router;
