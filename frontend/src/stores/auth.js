import { defineStore } from "pinia";
import http from "../api/http";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("rewrite_token") || "",
    user: JSON.parse(localStorage.getItem("rewrite_user") || "null")
  }),
  actions: {
    async login(payload) {
      const { data } = await http.post("/auth/login", payload);
      this.token = data.access_token;
      this.user = data.user;
      localStorage.setItem("rewrite_token", data.access_token);
      localStorage.setItem("rewrite_user", JSON.stringify(data.user));
    },
    async register(payload) {
      await http.post("/auth/register", payload);
    },
    logout() {
      this.token = "";
      this.user = null;
      localStorage.removeItem("rewrite_token");
      localStorage.removeItem("rewrite_user");
    }
  }
});

