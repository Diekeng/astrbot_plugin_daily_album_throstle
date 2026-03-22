from __future__ import annotations

import random

from astrbot.api import logger
from astrbot.api.star import Context

from .base import AlbumInfo, AlbumSource
from .llm import LLMSource
from .script import ScriptSource
from .web_search import WebSearchSource

__all__ = ["AlbumInfo", "AlbumSource", "select_source", "extract_search_query"]


async def extract_search_query(context: Context, prompt: str) -> str:
    """用 LLM 从推荐提示词中提炼出适合搜索引擎的关键词短语。"""
    provider = context.get_using_provider()
    if not provider:
        logger.debug("[DailyAlbum] 无可用 Provider，跳过关键词提取")
        return prompt

    try:
        resp = await context.llm_generate(
            chat_provider_id=provider.meta().id,
            prompt=(
                f"以下是一段专辑推荐需求描述：\n{prompt}\n\n"
                "请从中提炼出 3-6 个用于搜索引擎的关键词，"
                "以空格分隔输出，不要有任何其他内容。"
            ),
            system_prompt="你是搜索关键词提取助手，只输出关键词，不输出任何解释。",
        )
        keywords = resp.completion_text.strip()
        logger.debug(f"[DailyAlbum] 关键词提取结果：{keywords!r}")
        return keywords
    except Exception as e:
        logger.warning(f"[DailyAlbum] 关键词提取失败，回退原始截断后提示词：{e}")
        return prompt[:50]


# 来源名 → (config 子键, 默认启用, 默认权重)
_SOURCE_DEFS: list[tuple[str, str, bool, int]] = [
    ("llm", "source_llm", True, 1),
    ("web_search", "source_web_search", True, 2),
    ("script", "source_script", False, 1),
]


def select_source(context: Context, config: dict) -> AlbumSource:
    """根据各来源的 enabled/weight 配置加权随机选择一个来源实例。"""
    candidates: list[str] = []
    weights: list[int] = []

    for name, cfg_key, default_enabled, default_weight in _SOURCE_DEFS:
        sub = config.get(cfg_key, {})
        if sub.get(f"source_{name}_enabled", default_enabled):
            weight = max(1, int(sub.get(f"source_{name}_weight", default_weight)))
            candidates.append(name)
            weights.append(weight)

    if not candidates:
        logger.warning("[DailyAlbum] 所有来源均已禁用，回退到 llm")
        return LLMSource(context, config)

    chosen = random.choices(candidates, weights=weights, k=1)[0]
    logger.info(
        f"[DailyAlbum] 本次选择来源：{chosen}  "
        f"（候选：{list(zip(candidates, weights))}）"
    )

    match chosen:
        case "llm":
            return LLMSource(context, config)
        case "web_search":
            return WebSearchSource(context, config)
        case "script":
            return ScriptSource(config)
        case _:
            return LLMSource(context, config)
