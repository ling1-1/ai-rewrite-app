import json
import re
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

1. 你必须严格遵守本次前端传入的生成配置，不能自行忽略、删减或改写这些配置。
2. 内容一定要精炼、直观、清晰，抓住重点。
3. 当前语言风格要求：{language_style}。
4. 当前表达视角：{persona_style}，语气保持谦虚稳妥。
5. 当前内容密度：{content_density}，不要写太多，每个部分控制在适合 PPT 展示的长度。
6. 本次 PPT 预计页数：{ppt_page_count} 页。
7. 请严格按照下面这份大纲输出，每一部分单独成段：
{ppt_outline}
8. 是否包含个人观点：{include_personal_view_text}
9. 是否包含致谢：{include_acknowledgement_text}
10. 必须严格输出为 {ppt_page_count} 页，少一页或多一页都不可以。
11. 每一页都必须使用下面这种固定格式，不能改写页标记，不能合并多页：
【第1页】页标题
- 要点1
- 要点2
- 要点3
12. 每页只保留 2 到 4 条要点，每条要点一句话，不要写成长段落，不要写成答辩稿，不要写“大家好”这类演讲开场。
13. 除了上述页结构，不要输出额外说明、前言、总结提示或 markdown 代码块。

论文内容如下：
{thesis_text}
""".strip()

DEFENSE_SPEECH_PROMPT_TEMPLATE = """
请根据下面的论文内容和答辩PPT内容，生成一份适合 {speech_duration_minutes} 分钟左右中文本科毕业答辩的答辩稿，要求如下：

1. 你必须严格遵守本次前端传入的生成配置，不能自行忽略、删减或改写这些配置。
2. 内容一定要精炼、直观、清晰，讲重点。
3. 当前语言风格要求：{language_style}。
4. 当前表达视角：{persona_style}，表达直白自然，不要太书面化，不要太浮夸。
5. 当前内容密度：{content_density}。
6. 答辩时长必须控制在 {speech_duration_minutes} 分钟左右，不能明显过长。
7. 必须严格对应 PPT 大纲展开：
{ppt_outline}
8. 是否包含个人观点：{include_personal_view_text}
9. 是否包含致谢：{include_acknowledgement_text}
10. 不需要介绍个人信息。
11. 不要提论文不足、局限性、未来展望。
12. 这是一份“答辩讲稿”，不是 PPT 提纲。必须写成可直接朗读的自然段，不要写成 bullet 列表。
13. 每一页 PPT 最多对应 1 到 2 个自然段，整体结构要和 PPT 页面一一对应。
14. 直接输出可朗读的答辩稿正文，不要再附加说明。

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
    prompt = f"{prompt}\n\n{_build_ppt_json_instruction(context)}"

    raw_result = _call_chat_model(prompt, db=db)
    return _normalize_ppt_output(raw_result, expected_pages=context["ppt_page_count"])


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
    prompt = f"{prompt}\n\n{_build_speech_json_instruction(context)}"

    raw_result = _call_chat_model(prompt, db=db)
    return _normalize_speech_output(raw_result)


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


def _build_ppt_json_instruction(context: dict) -> str:
    return (
        "你必须只返回 JSON，不要输出解释、前言、Markdown 代码块或额外文字。\n"
        "JSON 结构必须如下：\n"
        "{\n"
        '  "slides": [\n'
        "    {\n"
        '      "page": 1,\n'
        '      "title": "第一页标题",\n'
        '      "bullets": ["要点1", "要点2", "要点3"]\n'
        "    }\n"
        "  ]\n"
        "}\n"
        f"slides 数组长度必须严格等于 {context['ppt_page_count']}。\n"
        "每页 bullets 必须是 2 到 4 条短句，不能写成长段落，不能输出答辩稿语气。"
    )


def _build_speech_json_instruction(context: dict) -> str:
    return (
        "你必须只返回 JSON，不要输出解释、前言、Markdown 代码块或额外文字。\n"
        "JSON 结构必须如下：\n"
        "{\n"
        '  "sections": [\n'
        "    {\n"
        '      "page": 1,\n'
        '      "title": "对应PPT页标题",\n'
        '      "paragraphs": ["这一页对应的讲稿段落1", "这一页对应的讲稿段落2"]\n'
        "    }\n"
        "  ]\n"
        "}\n"
        f"sections 数组长度尽量贴近 {context['ppt_page_count']} 页 PPT，整体时长控制在 {context['speech_duration_minutes']} 分钟左右。\n"
        "paragraphs 必须是可直接朗读的讲稿，不要改写成 PPT 要点。"
    )


def _normalize_ppt_output(raw_result: str, expected_pages: int) -> str:
    payload = _extract_json_payload(raw_result)
    slides = payload.get("slides")
    if not isinstance(slides, list) or not slides:
        raise DefenseServiceError("答辩PPT结构化解析失败：未找到 slides 数组。")

    normalized_blocks = []
    for index, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            continue

        title = _clean_text(slide.get("title")) or f"第 {index} 页"
        bullets = slide.get("bullets") or []
        if isinstance(bullets, str):
            bullets = [bullets]
        bullets = [_clean_text(item) for item in bullets if _clean_text(item)]
        bullets = bullets[:4]
        if len(bullets) < 2:
            bullets = bullets + ["请补充这一页的重点信息。"]

        normalized_blocks.append(
            "\n".join(
                [f"【第{index}页】", title, *[f"- {bullet}" for bullet in bullets]]
            )
        )

    if len(normalized_blocks) != expected_pages:
        raise DefenseServiceError(
            f"答辩PPT结构化解析失败：预期 {expected_pages} 页，实际只生成了 {len(normalized_blocks)} 页。"
        )

    return "\n\n".join(normalized_blocks)


def _normalize_speech_output(raw_result: str) -> str:
    payload = _extract_json_payload(raw_result)
    sections = payload.get("sections")
    if not isinstance(sections, list) or not sections:
        raise DefenseServiceError("答辩稿结构化解析失败：未找到 sections 数组。")

    parts = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        title = _clean_text(section.get("title"))
        paragraphs = section.get("paragraphs") or []
        if isinstance(paragraphs, str):
            paragraphs = [paragraphs]
        paragraphs = [_clean_text(item) for item in paragraphs if _clean_text(item)]
        if not paragraphs:
            continue

        if title:
            parts.append(title)
        parts.extend(paragraphs)

    if not parts:
        raise DefenseServiceError("答辩稿结构化解析失败：没有解析到可用段落。")

    return "\n\n".join(parts)


def _extract_json_payload(raw_result: str) -> dict:
    candidate = raw_result.strip()
    fenced_match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", candidate, re.IGNORECASE)
    if fenced_match:
        candidate = fenced_match.group(1).strip()
    else:
        brace_match = re.search(r"(\{[\s\S]*\})", candidate)
        if brace_match:
            candidate = brace_match.group(1).strip()

    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise DefenseServiceError("模型没有按约定返回 JSON，建议检查答辩提示词是否被改乱。") from exc

    if not isinstance(payload, dict):
        raise DefenseServiceError("模型返回的 JSON 结构不正确，顶层必须是对象。")

    return payload


def _clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = re.sub(r"^\*\*|\*\*$", "", text)
    return text.strip()


class _SafeFormatDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def _render_prompt(template: str, **kwargs) -> str:
    return template.format_map(_SafeFormatDict(**kwargs))
