from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings


class DefenseServiceError(Exception):
    pass


DEFENSE_SYSTEM_PROMPT = """
你是“JS 论文工作室”的答辩辅助助手。

你的任务是基于用户提供的论文内容，输出适合中文本科毕业答辩场景的材料。你必须遵守以下规则：
1. 表达精炼、直白、清晰，优先抓重点，不堆砌术语。
2. 语气要像普通本科生，保持谦虚、稳妥，不夸大研究价值。
3. 不要主动写“研究不足”“未来展望”“感谢各位聆听”等用户未要求内容。
4. 不要编造论文中没有出现的数据、实验或结论。
5. 输出内容必须方便直接粘贴到 PPT 或答辩稿中。
""".strip()


def generate_defense_ppt(thesis_text: str, db: Optional[Session] = None) -> str:
    prompt = f"""
请根据下面这篇论文内容，直接生成一份“答辩PPT文字版”，要求如下：

1. 内容一定要精炼、直观、清晰，抓住重点。
2. 语言直白一点，不要写得太复杂。
3. 研究目的、意义、研究成果、个人观点都要站在普通本科生角度写，语气谦虚稳妥。
4. 不要写太多，每个部分控制在适合 PPT 展示的长度。
5. 只输出以下五个部分，按顺序写：
一、研究背景、目的与意义（意义分为理论意义、实践意义）
二、研究内容重点介绍
三、研究成果
四、个人观点（只写个人观点，不要提研究不足）
五、致谢（简短，不要太多）

论文内容如下：
{thesis_text}
""".strip()

    return _call_chat_model(prompt, db=db)


def generate_defense_speech(thesis_text: str, ppt_content: str, db: Optional[Session] = None) -> str:
    prompt = f"""
请根据下面的论文内容和答辩PPT内容，生成一份适合 3 到 4 分钟中文本科毕业答辩的答辩稿，要求如下：

1. 内容一定要精炼、直观、清晰，讲重点。
2. 表达直白自然，不要太书面化，不要太浮夸。
3. 必须严格对应 PPT 的五个部分展开。
4. 不需要介绍个人信息。
5. 不要提论文不足、局限性、未来展望。
6. 直接输出可朗读的答辩稿正文，不要再附加说明。

论文内容：
{thesis_text}

答辩PPT内容：
{ppt_content}
""".strip()

    return _call_chat_model(prompt, db=db)


def generate_defense_flow(thesis_text: str, db: Optional[Session] = None) -> tuple[str, str]:
    ppt_content = generate_defense_ppt(thesis_text, db=db)
    speech_content = generate_defense_speech(thesis_text, ppt_content, db=db)
    return ppt_content, speech_content


def _call_chat_model(user_prompt: str, db: Optional[Session] = None) -> str:
    if not settings.anthropic_api_key:
        raise DefenseServiceError("尚未配置 API Key")

    model_name = settings.defense_model or settings.anthropic_model
    if db:
        try:
            from app.services.config_service import ConfigService
            config_service = ConfigService(db)
            model_name = config_service.get_defense_model(model_name)
        except Exception as exc:
            print(f"⚠️ 获取答辩模型配置失败：{exc}")

    base_url = settings.anthropic_base_url.rstrip("/")
    if base_url.endswith("/v3"):
        url = f"{base_url}/chat/completions"
    else:
        url = f"{base_url}/v1/chat/completions"

    payload = {
        "model": model_name,
        "max_tokens": settings.anthropic_max_tokens,
        "temperature": 0.5,
        "messages": [
            {"role": "system", "content": DEFENSE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.anthropic_api_key}",
        "content-type": "application/json",
    }

    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=120.0)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise DefenseServiceError(_extract_error_message(exc.response)) from exc
    except httpx.HTTPError as exc:
        raise DefenseServiceError("无法连接 API，请检查网络或接口配置。") from exc

    data = response.json()
    if "choices" in data and data["choices"]:
        result = data["choices"][0]["message"]["content"].strip()
    elif "content" in data:
        result = "\n".join(
            item.get("text", "").strip()
            for item in data.get("content", [])
            if item.get("type") == "text" and item.get("text")
        ).strip()
    else:
        result = ""

    if not result:
        raise DefenseServiceError("API 已返回响应，但没有解析到可用文本。")

    return result


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or f"HTTP {response.status_code}"

    error = payload.get("error", {})
    if isinstance(error, dict):
        return error.get("message") or error.get("type") or f"HTTP {response.status_code}"

    return str(error) or f"HTTP {response.status_code}"
