export function getErrorMessage(error, fallback = "请求失败") {
  if (!error) {
    return fallback;
  }

  const detail = error.response?.data?.detail;

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail) && detail.length) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        if (item?.msg) {
          return item.msg;
        }

        return null;
      })
      .filter(Boolean)
      .join("；");
  }

  if (error.message) {
    return error.message;
  }

  return fallback;
}
