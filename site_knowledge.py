from __future__ import annotations

import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent

PEOPLE = [
    {"kind": "person", "service": "recording", "title": "董喆奥", "subtitle": "录音工程师", "description": "5 年录音经验；擅长流行、说唱、人声录音、乐器录音和影视配音。录音作品：AOE 干声、apologize干声、who am i干声。", "url": "/recording/dong-zheao", "image": "/assets/people/dong-zheao.jpeg"},
    {"kind": "person", "service": "recording", "title": "程鸿林", "subtitle": "录音工程师", "description": "6 年录音经验；擅长流行、说唱、人声录音、乐器录音、麦克风摆位和话放调节。录音作品：耳机线干声、原始股干声、原始股干声2。", "url": "/recording/cheng-honglin", "image": "/assets/people/cheng-honglin.jpeg"},
    {"kind": "person", "service": "mixing", "title": "董喆奥", "subtitle": "混音工程师", "description": "5 年混音经验；擅长说唱、流行、古典混音和母带处理。混音作品：all my love-MIX、Get Away-MIX、racks on racks。", "url": "/mixing/dong-zheao", "image": "/assets/people/dong-zheao.jpeg"},
    {"kind": "person", "service": "mixing", "title": "程鸿林", "subtitle": "混音工程师", "description": "多年混音经验；擅长流行、说唱、民谣、人声精修、声场搭建和母带处理。混音作品：nowadays、new song、demo。", "url": "/mixing/cheng-honglin", "image": "/assets/people/cheng-honglin.jpeg"},
    {"kind": "person", "service": "arrangement", "title": "P.M", "subtitle": "编曲制作人", "description": "擅长流行、嘻哈编曲、音色设计和编排统筹；熟练使用 FL Studio，制作超过 200 首伴奏。作品：juicewrld 136、呵呵小样、luvme134。", "url": "/arrangement/pm", "image": "/assets/people/pm.jpeg"},
    {"kind": "person", "service": "arrangement", "title": "太老师", "subtitle": "编曲制作人", "description": "流行、古典与影视配乐创作 10 余年，兼具钢琴、吉他演奏和乐器教学经验。", "url": "/arrangement/tai-laoshi", "image": "/assets/people/tai-laoshi.jpeg"},
    {"kind": "person", "service": "live", "title": "董喆奥", "subtitle": "直播音频工程师", "description": "擅长直播人声精调、降噪、声场搭建、设备适配和母带优化。", "url": "/live/dong-zheao", "image": "/assets/people/dong-zheao.jpeg"},
    {"kind": "person", "service": "live", "title": "程鸿林", "subtitle": "直播音频工程师", "description": "擅长直播人声调校、降噪优化、声场搭建和设备适配。", "url": "/live/cheng-honglin", "image": "/assets/people/cheng-honglin.jpeg"},
]

TEACHERS = {
    "recording": ("录音课程", ["董喆奥"] * 3),
    "mixing": ("混音课程", ["董喆奥"] * 5),
    "arrangement": ("编曲课程", ["P.M", "P.M", "太老师", "太老师"]),
}

PRESETS = [
    ("rap", "智声说唱预设", "强化咬字、动态与低频控制，适配 Rap 和 Hip-Hop。"),
    ("backing", "和声backing预设", "为和声与叠唱建立清晰、宽阔的空间层次。"),
    ("udg", "智声udg预设", "适合需要厚度与质感的人声起始处理。"),
    ("pop", "智声流行预设", "明亮、有空气感的流行人声起始方案。"),
    ("retro", "智声复古预设", "温暖、柔和的复古与磁带感声音方向。"),
    ("electronic", "电音电子预设", "适合电子人声与合成器的动态和空间处理。"),
]

CATEGORY_LABELS = {
    "microphones": "麦克风", "interfaces": "声卡", "preamps": "话放",
    "headphones": "监听耳机", "monitors": "监听音响", "plugins": "音频插件",
}


def _equipment_resources() -> list[dict]:
    path = ROOT / "equipment-data.js"
    try:
        text = path.read_text(encoding="utf-8")
        match = re.search(r"window\.gearProducts\s*=\s*(\[.*\]);\s*$", text, re.S)
        products = json.loads(match.group(1)) if match else []
    except (OSError, json.JSONDecodeError):
        products = []
    return [
        {
            "kind": "equipment",
            "service": item.get("category", ""),
            "title": item.get("name", "音频设备"),
            "subtitle": CATEGORY_LABELS.get(item.get("category", ""), "音频设备"),
            "description": f"智声科技设备供应中的{CATEGORY_LABELS.get(item.get('category', ''), '音频设备')}产品。",
            "url": "/equipment",
            "external_url": item.get("url", ""),
            "image": item.get("localImage", ""),
        }
        for item in products
    ]


def all_resources() -> list[dict]:
    resources = list(PEOPLE)
    for service, (title, teachers) in TEACHERS.items():
        for index, teacher in enumerate(teachers, 1):
            resources.append({
                "kind": "teaching", "service": service,
                "title": f"{title} · 视频 {index}", "subtitle": f"讲解人：{teacher}",
                "description": f"智声科技{title}的真实讲解视频，由{teacher}讲解。",
                "url": f"/teaching/{service}#video-{index}",
                "image": f"/assets/teaching/{service}/{index}.jpg",
            })
    for preset_id, name, description in PRESETS:
        resources.append({
            "kind": "preset", "service": "presets", "title": name,
            "subtitle": "Studio One 效果预设", "description": description,
            "url": f"/presets/{preset_id}", "image": f"/assets/preset-photos/{preset_id}.jpg",
        })
    resources.extend(_equipment_resources())
    return resources


SERVICE_TERMS = {
    "recording": ("录音", "录制", "干声", "麦克风"),
    "mixing": ("混音", "母带", "贴唱", "修音"),
    "arrangement": ("编曲", "作曲", "伴奏", "配乐"),
    "live": ("直播", "调试", "声场", "降噪"),
    "presets": ("预设", "效果链", "trackpreset"),
    "microphones": ("麦克风", "话筒", "收音"),
    "interfaces": ("声卡", "音频接口"),
    "preamps": ("话放", "前级"),
    "headphones": ("监听耳机", "耳机"),
    "monitors": ("监听音响", "监听音箱", "音箱"),
    "plugins": ("音频插件", "插件", "fabfilter"),
}


def _score(resource: dict, query: str) -> int:
    q = query.casefold()
    haystack = " ".join(str(resource.get(key, "")) for key in ("title", "subtitle", "description", "service")).casefold()
    score = 0
    title = str(resource.get("title", "")).casefold()
    if title and title in q:
        score += 20
    for token in re.findall(r"[a-z0-9.+-]+|[\u4e00-\u9fff]{2,}", q):
        if token in haystack:
            score += min(8, len(token))
    service = resource.get("service", "")
    if any(term.casefold() in q for term in SERVICE_TERMS.get(service, ())):
        score += 10
    if resource.get("kind") == "teaching" and any(word in q for word in ("教学", "教程", "课程", "视频", "学习")):
        score += 14
    if resource.get("kind") == "person" and any(word in q for word in ("师傅", "老师", "工程师", "制作人", "找人", "推荐人")):
        score += 12
    if resource.get("kind") == "equipment" and any(word in q for word in ("设备", "产品", "购买", "推荐")):
        score += 6
    if resource.get("kind") == "preset" and "预设" in q:
        score += 12
    return score


def search_site_resources(query: str, limit: int = 6) -> list[dict]:
    ranked = sorted(((_score(item, query), item) for item in all_resources()), key=lambda row: row[0], reverse=True)
    meaningful = [(score, item) for score, item in ranked if score >= 10]
    if not meaningful:
        return []
    top_score = meaningful[0][0]
    floor = max(10, top_score - 6)
    return [dict(item, relevance=score) for score, item in meaningful if score >= floor][:limit]


def search_web(query: str, limit: int = 4) -> list[dict]:
    """Fetch public Bing RSS results for questions not covered by the website."""
    url = "https://www.bing.com/search?format=rss&q=" + urllib.parse.quote(query)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 ZhishengAI/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            root = ET.fromstring(response.read())
    except (OSError, ET.ParseError):
        return []
    results = []
    for item in root.findall(".//item")[:limit]:
        title = html.unescape(item.findtext("title", "")).strip()
        link = item.findtext("link", "").strip()
        description = re.sub(r"<[^>]+>", "", html.unescape(item.findtext("description", ""))).strip()
        if title and link.startswith(("http://", "https://")):
            results.append({"title": title, "url": link, "description": description[:300]})
    return results


def build_ai_context(query: str) -> tuple[str, list[dict]]:
    resources = search_site_resources(query)
    lines = [
        "你是智声科技网站的 AI 资源顾问。优先使用下面提供的站内真实资料回答。",
        "不得编造网站人员、履历、课程、视频、作品、价格或链接。",
        "命中站内资源时，应说明为什么符合用户需求，并提醒用户可点击回答下方的站内资源卡片查看。",
        "如果站内资料没有答案，可以根据常识和联网检索结果回答，并明确区分‘智声科技站内资源’和‘全网资料’。",
        "回答使用中文、简洁自然；不确定时明确说明，不要假装已经浏览不存在的页面。",
    ]
    if resources:
        lines.append("\n本轮检索到的智声科技站内资源：")
        for item in resources:
            lines.append(f"- {item['title']}｜{item['subtitle']}｜{item['description']}｜站内链接：{item['url']}")
    else:
        web_results = search_web(query)
        if web_results:
            lines.append("\n本轮站内没有直接匹配，以下是实时全网检索结果。引用时请给出完整来源链接：")
            for item in web_results:
                lines.append(f"- {item['title']}｜{item['description']}｜{item['url']}")
        else:
            lines.append("\n本轮站内没有直接匹配，联网检索暂时无结果；可使用通用知识回答并说明信息可能需要核实。")
    return "\n".join(lines), resources


def public_resources(query: str, limit: int = 6) -> list[dict]:
    keys = ("kind", "service", "title", "subtitle", "description", "url", "external_url", "image")
    return [{key: item.get(key, "") for key in keys} for item in search_site_resources(query, limit)]
