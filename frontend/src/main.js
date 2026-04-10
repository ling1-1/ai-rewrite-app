import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";
import "./styles.css";

// ElementPlus 按需引入，避免全局样式覆盖
// import ElementPlus from "element-plus";
// import "element-plus/dist/index.css";

const app = createApp(App);

app.use(createPinia());
app.use(router);
// app.use(ElementPlus);
app.mount("#app");

