const sourceText = document.getElementById("sourceText");
const resultText = document.getElementById("resultText");
const statusText = document.getElementById("statusText");
const sourceCount = document.getElementById("sourceCount");
const rewriteButton = document.getElementById("rewriteButton");
const clearButton = document.getElementById("clearButton");
const copyButton = document.getElementById("copyButton");

function updateCount() {
  const count = sourceText.value.trim().length;
  sourceCount.textContent = `${count} 字`;
}

function simulateRewrite(text) {
  const normalized = text
    .replace(/不仅/g, "不只")
    .replace(/然而/g, "与此同时")
    .replace(/仍然需要/g, "依旧需要")
    .replace(/应用/g, "实践运用")
    .replace(/提高/g, "提升")
    .replace(/推动/g, "带动");

  const parts = normalized
    .split(/(?<=[。！？])/)
    .map((item) => item.trim())
    .filter(Boolean);

  if (!parts.length) {
    return "这里将显示改写后的结果。正式接入时，请将这段演示逻辑替换为大模型 API 的返回内容。";
  }

  return parts
    .map((sentence, index) => {
      if (index === 0) {
        return `从当前发展趋势来看，${sentence}`;
      }
      if (index === parts.length - 1) {
        return `因此，在实际落地阶段，${sentence}`;
      }
      return `进一步来说，${sentence}`;
    })
    .join("\n\n");
}

async function handleRewrite() {
  const text = sourceText.value.trim();

  if (!text) {
    statusText.textContent = "请输入原文";
    resultText.textContent = "请先在左侧输入需要处理的内容。";
    return;
  }

  statusText.textContent = "正在生成";
  rewriteButton.disabled = true;
  rewriteButton.textContent = "生成中...";

  await new Promise((resolve) => setTimeout(resolve, 700));

  resultText.textContent = simulateRewrite(text);
  statusText.textContent = "演示结果已生成";
  rewriteButton.disabled = false;
  rewriteButton.textContent = "开始改写";
}

function handleClear() {
  sourceText.value = "";
  resultText.textContent =
    "点击“开始改写”后，这里会展示模型的输出结果。当前页面仅用演示逻辑模拟改写效果，正式开发时只需将此处替换为后端 API 的返回内容。";
  statusText.textContent = "等待处理";
  updateCount();
}

async function handleCopy() {
  const text = resultText.textContent.trim();

  if (!text) {
    return;
  }

  try {
    await navigator.clipboard.writeText(text);
    statusText.textContent = "结果已复制";
  } catch (error) {
    statusText.textContent = "复制失败";
  }
}

sourceText.addEventListener("input", updateCount);
rewriteButton.addEventListener("click", handleRewrite);
clearButton.addEventListener("click", handleClear);
copyButton.addEventListener("click", handleCopy);

updateCount();
