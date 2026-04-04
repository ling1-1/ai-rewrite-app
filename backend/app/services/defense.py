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

DEFENSE_PPT_PROMPT_TEMPLATE = """
请根据下面这篇论文内容，直接生成一份“答辩PPT文字版”，要求如下：

1. 内容一定要精炼、直观、清晰，抓住重点。
2. 当前语言风格要求：{language_style}。
3. 当前表达视角：{persona_style}，语气保持谦虚稳妥。
4. 当前内容密度：{content_density}，不要写太多，每个部分控制在适合 PPT 展示的长度。
5. 本次 PPT 预计页数：{ppt_page_count} 页。
6. 请严格按照下面这份大纲输出，每一部分单独成段：
{ppt_outline}
7. 是否包含个人观点：{include_personal_view_text}
8. 是否包含致谢：{include_acknowledgement_text}

论文内容如下：
{thesis_text}
""".strip()

DEFENSE_SPEECH_PROMPT_TEMPLATE = """
请根据下面的论文内容和答辩PPT内容，生成一份适合 {speech_duration_minutes} 分钟左右中文本科毕业答辩的答辩稿，要求如下：

1. 内容一定要精炼、直观、清晰，讲重点。
2. 当前语言风格要求：{language_style}。
3. 当前表达视角：{persona_style}，表达直白自然，不要太书面化，不要太浮夸。
4. 当前内容密度：{content_density}。
5. 必须严格对应 PPT 大纲展开：
{ppt_outline}
6. 是否包含个人观点：{include_personal_view_text}
7. 是否包含致谢：{include_acknowledgement_text}
4. 不需要介绍个人信息。
5. 不要提论文不足、局限性、未来展望。
6. 直接输出可朗读的答辩稿正文，不要再附加说明。

论文内容：
{thesis_text}

答辩PPT内容：
{ppt_content}
""".strip()


def generate_defense_ppt(
    thesis_text: str,
    db: Optional[Session] = None,
    options: Optional[dict] = None,
) -> str:
    context = _build_generation_context(options)
    prompt_template = DEFENSE_PPT_PROMPT_TEMPLATE
    if db:
        try:
            from app.services.config_service import ConfigService
            config_service = ConfigService(db)
            prompt_template = config_service.get_defense_ppt_prompt() or DEFENSE_PPT_PROMPT_TEMPLATE
        except Exception as exc:
            print(f"⚠️ 获取答辩PPT提示词失败：{exc}")

    prompt = _render_prompt(
        prompt_template,
        thesis_text=thesis_text,
        **context,
    )

    return _call_chat_model(prompt, db=db)


def generate_defense_speech(
    thesis_text: str,
    ppt_content: str,
    db: Optional[Session] = None,
    options: Optional[dict] = None,
) -> str:
    context = _build_generation_context(options)
    prompt_template = DEFENSE_SPEECH_PROMPT_TEMPLATE
    if db:
        try:
            from app.services.config_service import ConfigService
            config_service = ConfigService(db)
            prompt_template = config_service.get_defense_speech_prompt() or DEFENSE_SPEECH_PROMPT_TEMPLATE
        except Exception as exc:
            print(f"⚠️ 获取答辩稿提示词失败：{exc}")

    prompt = _render_prompt(
        prompt_template,
        thesis_text=thesis_text,
        ppt_content=ppt_content,
        **context,
    )

    return _call_chat_model(prompt, db=db)


def generate_defense_flow(
    thesis_text: str,
    db: Optional[Session] = None,
    options: Optional[dict] = None,
) -> tuple[str, str]:
    ppt_content = generate_defense_ppt(thesis_text, db=db, options=options)
    speech_content = generate_defense_speech(thesis_text, ppt_content, db=db, options=options)
    return ppt_content, speech_content


def _call_chat_model(user_prompt: str, db: Optional[Session] = None) -> str:
    api_key = settings.defense_api_key or settings.anthropic_api_key
    if not api_key:
        raise DefenseServiceError("尚未配置答辩模型 API Key")

    model_name = settings.defense_model or settings.anthropic_model
    base_url = (settings.defense_base_url or settings.anthropic_base_url).rstrip("/")
    max_tokens = settings.defense_max_tokens
    temperature = settings.defense_temperature
    system_prompt = DEFENSE_SYSTEM_PROMPT
    if db:
        try:
            from app.services.config_service import ConfigService
            config_service = ConfigService(db)
            api_key = config_service.get_defense_api_key(api_key)
            model_name = config_service.get_defense_model(model_name)
            base_url = config_service.get_defense_base_url(base_url).rstrip("/")
            max_tokens = config_service.get_defense_max_tokens(max_tokens)
            temperature = config_service.get_defense_temperature(temperature)
            system_prompt = config_service.get_defense_system_prompt() or DEFENSE_SYSTEM_PROMPT
        except Exception as exc:
            print(f"⚠️ 获取答辩模型配置失败：{exc}")

    url = _build_chat_completions_url(base_url)

    payload = {
        "model": model_name,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "content-type": "application/json",
    }

    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=120.0)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        message = _extract_error_message(exc.response)
        raise DefenseServiceError(
            f"答辩模型 API 请求失败（HTTP {exc.response.status_code}）：{message}"
        ) from exc
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


def _build_chat_completions_url(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    if normalized.endswith("/v1") or normalized.endswith("/compatible-mode/v1"):
        return f"{normalized}/chat/completions"
    if normalized.endswith("/v3"):
        return f"{normalized}/chat/completions"
    return f"{normalized}/v1/chat/completions"


def _build_generation_context(options: Optional[dict]) -> dict:
    options = options or {}
    outline = (options.get("ppt_outline") or "").strip() or (
        "一、研究背景、目的与意义\n"
        "二、研究内容重点介绍\n"
        "三、研究成果\n"
        "四、个人观点\n"
        "五、致谢"
    )
    return {
        "ppt_page_count": int(options.get("ppt_page_count") or 5),
        "ppt_outline": outline,
        "speech_duration_minutes": int(options.get("speech_duration_minutes") or 4),
        "language_style": options.get("language_style") or "更直白",
        "persona_style": options.get("persona_style") or "普通本科生",
        "content_density": options.get("content_density") or "精简",
        "include_acknowledgement_text": "包含致谢" if options.get("include_acknowledgement", True) else "不包含致谢",
        "include_personal_view_text": "包含个人观点" if options.get("include_personal_view", True) else "不包含个人观点",
    }


class _SafeFormatDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def _render_prompt(template: str, **kwargs) -> str:
    return template.format_map(_SafeFormatDict(**kwargs))
