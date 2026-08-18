from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

from .models import ALLOWED_GENRES, DEFAULT_MIX_MODE, DEFAULT_TEMPLATE_ID


DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


def _genre_from_hint(value: str) -> str:
    normalized = (value or "").upper().strip()
    aliases = {
        "AI 自动判断": "AUTO", "AUTO": "AUTO", "流行": "POP", "POP": "POP",
        "说唱 / HIP-HOP": "RAP", "说唱": "RAP", "HIP-HOP": "RAP", "RAP": "RAP",
        "民谣": "FOLK", "FOLK": "FOLK", "直播人声": "LIVE_VOCAL", "LIVE_VOCAL": "LIVE_VOCAL",
    }
    return aliases.get(normalized, "AUTO")


def _fallback(genre_hint: str, reason: str) -> dict:
    genre = _genre_from_hint(genre_hint)
    return {
        "genre": genre if genre != "AUTO" else "UNKNOWN",
        "template_id": DEFAULT_TEMPLATE_ID,
        "mix_mode": DEFAULT_MIX_MODE,
        "reason": reason[:500],
    }


def _parse_json(value: str) -> dict:
    stripped = value.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", stripped, flags=re.IGNORECASE)
    parsed = json.loads(stripped)
    if not isinstance(parsed, dict):
        raise ValueError("AI plan is not an object")
    return parsed


def create_plan(user_prompt: str, genre_hint: str) -> dict:
    """Ask DeepSeek for interpretation only, then force the safe first-phase template."""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        return _fallback(genre_hint, "未配置 DeepSeek，已使用默认混音任务方案。")

    system = (
        "You are a music request classifier for a professional mixing workflow. "
        "Return exactly one JSON object and nothing else. Allowed genre values: POP, RAP, FOLK, LIVE_VOCAL, UNKNOWN. "
        "Do not output plugin parameters, commands, code, file paths, or automation steps. "
        "The template_id must be ZHISHENG_DEFAULT_MIX and mix_mode must be professional_mix. "
        "reason must be a concise Chinese explanation."
    )
    message = f"用户类型选择：{genre_hint or 'AI 自动判断'}\n用户描述：{user_prompt or '未提供额外描述'}"
    payload = json.dumps({
        "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": message}],
    }).encode("utf-8")
    request = urllib.request.Request(
        DEEPSEEK_URL,
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = json.loads(response.read().decode("utf-8"))
        raw = body["choices"][0]["message"]["content"]
        proposed = _parse_json(raw)
        genre = str(proposed.get("genre", "UNKNOWN")).upper()
        return {
            "genre": genre if genre in ALLOWED_GENRES else "UNKNOWN",
            "template_id": DEFAULT_TEMPLATE_ID,
            "mix_mode": DEFAULT_MIX_MODE,
            "reason": str(proposed.get("reason", "已生成默认专业混音任务方案。")).replace("\x00", "")[:500],
        }
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError, json.JSONDecodeError):
        return _fallback(genre_hint, "AI 分析暂时不可用，已根据用户选择建立默认混音任务。")
