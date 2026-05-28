import logging
from openai import OpenAI
from backend.config import settings
from schemas.agent_state_schema import ChatState

logger = logging.getLogger(__name__)


def run_router_agent(state: ChatState) -> ChatState:
    api_key = settings.DEEPSEEK_API_KEY
    base_url = settings.DEEPSEEK_BASE_URL
    model_name = settings.DEEPSEEK_MODEL
    
    if not api_key:
        logger.error("Router Agent: DEEPSEEK_API_KEY 未配置，默认分类为 off_topic")
        state.next_node = "off_topic"
        return state

    client = OpenAI(api_key=api_key, base_url=base_url)
    
    system_prompt = """你是一个意图分类器。用户的输入分为三类：
1. ask_question：用户针对正在学习的内容提问，或者要求继续讲解、推进进度等。
2. submit_quiz：用户在做题，提交了自己的答案。
3. off_topic：用户在完全闲聊、偏题（如问菜谱、天气等无关内容）。

请仅输出上述三个类别名称之一，不要输出任何额外字符。"""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": state.user_message}
            ],
            temperature=0.0,
            max_tokens=10
        )
        intent = response.choices[0].message.content.strip().lower()
        logger.info(f"Router Agent 意图分类: '{state.user_message}' -> '{intent}'")
        if "ask_question" in intent:
            state.next_node = "ask_question"
        elif "submit_quiz" in intent:
            state.next_node = "submit_quiz"
        else:
            state.next_node = "off_topic"
    except Exception as e:
        logger.error(f"Router Agent 调用失败: {type(e).__name__}: {e}")
        state.next_node = "off_topic"
        
    return state
