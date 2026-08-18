from __future__ import annotations

from copy import deepcopy


STATUSES = (
    "uploading",
    "planning",
    "queued",
    "claimed",
    "preparing",
    "studio_processing",
    "exporting",
    "uploading_result",
    "completed",
    "failed",
    "cancelled",
)

ACTIVE_STATUSES = {
    "uploading", "planning", "queued", "claimed", "preparing",
    "studio_processing", "exporting", "uploading_result",
}

ROLE_TO_TRACK = {
    "lead_vocal": "Vocal",
    "vocal_2": "Vocal 2",
    "adlib": "Adlib",
    "instrumental": "Instrumental",
}

ALLOWED_ROLES = set(ROLE_TO_TRACK)
ALLOWED_GENRES = {"AUTO", "POP", "RAP", "FOLK", "LIVE_VOCAL", "UNKNOWN"}
DEFAULT_TEMPLATE_ID = "ZHISHENG_DEFAULT_MIX"
DEFAULT_MIX_MODE = "professional_mix"


def public_job(job: dict) -> dict:
    """Return only browser-safe job data; local filesystem paths never leave the server."""
    result = deepcopy(job)
    for item in result.get("inputs", []):
        item.pop("path", None)
    result.get("result", {}).pop("path", None)
    result.pop("agent", None)
    return result
