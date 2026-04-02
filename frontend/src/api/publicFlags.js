import http from "./http";

const REGISTRATION_FLAG_KEY = "rewrite_enable_registration";

function getFallbackBaseUrls() {
  if (typeof window === "undefined") {
    return [];
  }

  const hostname = window.location.hostname;
  if (hostname === "localhost" || hostname === "127.0.0.1") {
    return ["http://127.0.0.1:8002", "http://localhost:8002"];
  }

  return [];
}

export function getCachedRegistrationFlag() {
  const rawValue = localStorage.getItem(REGISTRATION_FLAG_KEY);
  if (rawValue === null) {
    return null;
  }

  return rawValue === "true";
}

export function setCachedRegistrationFlag(enabled) {
  localStorage.setItem(REGISTRATION_FLAG_KEY, String(Boolean(enabled)));
}

export async function fetchPublicFlags() {
  try {
    const { data } = await http.get("/config/public/flags");
    setCachedRegistrationFlag(data.enable_registration);
    return data;
  } catch (error) {
    let lastError = error;

    for (const baseUrl of getFallbackBaseUrls()) {
      try {
        const response = await fetch(`${baseUrl}/config/public/flags`);
        if (!response.ok) {
          throw new Error(`请求失败（${response.status}）`);
        }

        const data = await response.json();
        setCachedRegistrationFlag(data.enable_registration);
        return data;
      } catch (fallbackError) {
        lastError = fallbackError;
      }
    }

    throw lastError;
  }
}
