import logging
from schemas.agent_state_schema import ChatState

logger = logging.getLogger(__name__)

# 只有命中这些明显无关关键词时才拒答，其余全部放行
_OFF_TOPIC_KEYWORDS = [
    "天气", "菜谱", "做饭", "炒菜", "外卖", "游戏攻略",
    "追星", "八卦", "综艺", "电视剧", "电影推荐",
    "星座", "算命", "占卜", "塔罗",
]


def run_router_agent(state: ChatState) -> ChatState:
    """
    意图分类器（规则版）。

    产品策略（来自 product_discussion_update_summary.md §9）：
      在学习页内的 AI 导师，默认用户问题与当前关卡相关。
      只有明显无关的问题才拒答。

    因此不再使用 LLM 做路由判断（既慢又不稳定），
    改为简单关键词匹配：只拦截极少数明确无关的消息。
    """
    user_msg = state.user_message.strip()

    # 空消息直接放行
    if not user_msg:
        state.next_node = "ask_question"
        return state

    # 检查是否包含测验提交的典型标记
    msg_lower = user_msg.lower()
    quiz_markers = ["答案是", "选 ", "选a", "选b", "选c", "选d", "我选", "answer"]
    if any(marker in msg_lower for marker in quiz_markers):
        state.next_node = "submit_quiz"
        logger.info(f"Router Agent (规则): '{user_msg}' -> submit_quiz")
        return state

    # 只拦截极少数明确无关的消息
    if any(keyword in user_msg for keyword in _OFF_TOPIC_KEYWORDS):
        state.next_node = "off_topic"
        logger.info(f"Router Agent (规则): '{user_msg}' -> off_topic (命中关键词)")
        return state

    # 默认全部视为与学习相关
    state.next_node = "ask_question"
    logger.info(f"Router Agent (规则): '{user_msg}' -> ask_question")
    return state
