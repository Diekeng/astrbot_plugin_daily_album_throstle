# astrbot_plugin_daily_album 🎵
> 这是 `astrbot_plugin_daily_album` 的个人练习Fork,优化了搜索体验并新增了风格偏好池
每天给你推一张专辑！用 LLM 挑专辑、写文案，还能顺手发个网易云音乐卡片——
不管是吃饭、通勤、或者发呆的时候，都有好东西听(｡•̀ᴗ-)✧

---

## 能做什么
- **风格偏好池**：支持配置多个推荐风格描述，每天随机抽取一条，拒绝单调！
- **核心词提取**：自动从长名称（如日系 Live 专辑）提取核心关键词，搜索更精准。
- 每天定时向配置的群或私聊推送一张专辑推荐
- 文案由 LLM 用当前人格的口吻生成，每次都不一样
- 自动去网易云搜对应专辑，发音乐卡片（aiocqhttp 平台专属）
- 搜不到的话会提醒你去 Spotify / Apple Music 手动找
- 有去重记录，推过的专辑不会重复出现

---

## 三种推荐来源

可以同时开多个，按权重随机抽，混着用最好玩！

| 来源 | 说明 |
|------|------|
| `llm` | 直接让 LLM 根据你的偏好描述推荐 |
| `web_search` | 先联网搜一圈，再让 LLM 结合搜索结果推荐，信息更新更准 |
| `script` | 自己写 Python 脚本，完全自定义推荐逻辑 |

> 联网搜索优先走 Tavily，没有 Tavily Key 的话会自动爬 Bing。

---

## 配置项

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `target_sessions` | list | `[]` | 要推送的会话，填 `unified_msg_origin` 格式，比如 `aiocqhttp:GroupMessage:123456` |
| `push_time` | string | `10:00` | 几点推，格式 `HH:MM`（服务器时区） |
| `recommend_prompt` | list | **风格池** | **[New]** 推荐偏好池列表，每次随机抽一条使用。 |
| `max_history_in_prompt` | int | `30` | 给 LLM 看的历史推荐条数，越多越不容易重复 |
| `source_llm_enabled` / `_weight` | bool / int | `true` / `1` | LLM 来源的开关和权重 |
| `source_web_search_enabled` / `_weight` | bool / int | `true` / `2` | 联网搜索来源的开关和权重 |
| `source_script_enabled` / `_weight` | bool / int | `false` / `1` | 自定义脚本来源的开关和权重 |
| `script_file` | file | — | 自定义脚本文件（`.py`） |
| `netease_search_max_attempts` | int | `3` | 网易云搜索时最多取几个候选，逐一让 LLM 核验 |

Tavily Key 在 AstrBot 全局设置的 `provider_settings.websearch_tavily_key` 里配，跟其他插件共用同一个就行。

---

## 命令

| 命令 | 说明 |
|------|------|
| `/album_today` | 不想等定时？现在就要！推荐发到当前会话 |
| `/album_history` | 看看最近推过哪 10 张 |

---

## 自定义脚本怎么写

开启 `script` 来源后，上传一个 `.py` 文件，里面实现这个函数就行：

```python
async def fetch_album(prompt: str, history: list[dict]) -> dict:
    """
    prompt: 推荐偏好描述
    history: 历史推荐记录，每项有 album_name、artist 等字段
    返回 dict，字段：album_name, artist（list[str]）, year, genre, cover_url, description, listen_tip
    """
    ...
```

`test/dummy_script.py` 里有个示例可以参考。

---

## 网易云音乐卡片是怎么找的

找专辑这件事比想象中复杂一点，大概是这样：

1. **核心关键词提取**：自动将 `《Love Live! ... ～μ'sic Forever...～》` 简化为 `μ'sic Forever...`。
2. **三段式搜索**：`核心词` → `全名 + 艺术家` → `全名`。
3. **LLM 二次核验**：对搜索结果进行智能比对，确保版本（Deluxe/Remastered）匹配。

> 音乐卡片只在 aiocqhttp（NapCat / LLOneBot）下能用，其他平台会静默跳过，不影响文案发送。


感谢原作者 [wanger](https://github.com/10knamesmore/astrbot_plugin_daily_album) 。本仓库为个人学习分支。  
