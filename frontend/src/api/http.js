import axios from "axios";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
  || (import.meta.env.DEV ? "http://127.0.0.1:8002" : "");

const http = axios.create({
  baseURL: apiBaseUrl
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("rewrite_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default http;
