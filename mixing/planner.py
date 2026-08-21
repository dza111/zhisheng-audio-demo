from __future__ import annotations

from .models import DEFAULT_MIX_MODE, DEFAULT_TEMPLATE_ID


def create_plan(user_prompt: str = "", genre_hint: str = "") -> dict:
    """Return the fixed competition-demo plan.

    File roles are explicit and no audio/genre inference is needed here.
    DeepSeek remains available to the chat assistant, but is not in the
    critical Studio One execution path.
    """
    return {
        "genre": "USER_SPECIFIED",
        "template_id": DEFAULT_TEMPLATE_ID,
        "mix_mode": DEFAULT_MIX_MODE,
        "reason": "用户已明确指定伴奏与主人声，使用固定 Studio One 专业混音模板。",
    }
