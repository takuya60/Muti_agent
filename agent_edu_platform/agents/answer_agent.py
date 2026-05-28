import json
import logging
from openai import OpenAI
from backend.config import settings
from schemas.agent_state_schema import ChatState

logger = logging.getLogger(__name__)


def _get_client():
    """统一获取 OpenAI 客户端（DeepSeek 兼容）"""
    api_key = settings.DEEPSEEK_API_KEY
    base_url = settings.DEEPSEEK_BASE_URL
    if not api_key:
        return None, None
    client = OpenAI(api_key=api_key, base_url=base_url)
    return client, settings.DEEPSEEK_MODEL


def _build_messages(state: ChatState) -> list[dict]:
    """构建 system + 历史 + 当前用户消息的 messages 列表"""
    context_str = json.dumps(state.current_resource_context, ensure_ascii=False) if state.current_resource_context else "无参考讲义"
    
    system_prompt = f"""你是一个温柔且专业的机器学习实训导师。
【当前讲义内容】：
{context_str}

请结合上面的讲义内容，解答学生的疑问。如果问题超出讲义范围但属于机器学习领域，请基于你的专业知识解答。
如果是非常细节的代码疑问，可以结合实操指南的部分进行讲解。"""

    messages = [{"role": "system", "content": system_prompt}]
    # 限制保留最近 10 条历史对话以节省 Token
    recent_history = state.chat_history[-10:] if len(state.chat_history) > 10 else state.chat_history
    for msg in recent_history:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
    messages.append({"role": "user", "content": state.user_message})
    return messages


def run_answer_agent(state: ChatState) -> ChatState:
    client, model_name = _get_client()
    if not client:
        logger.error("Answer Agent: DEEPSEEK_API_KEY 未配置")
        state.agent_response = "系统未配置大模型 API Key。"
        return state

    messages = _build_messages(state)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7
        )
        state.agent_response = response.choices[0].message.content.strip()
        logger.info(f"Answer Agent 回复成功，长度: {len(state.agent_response)}")
    except Exception as e:
        logger.error(f"Answer Agent 调用失败: {type(e).__name__}: {e}")
        state.agent_response = f"抱歉，大模型请求出现异常：{e}"
        
    return state

def stream_answer_agent(state: ChatState):
    client, model_name = _get_client()
    if not client:
        logger.error("Stream Answer Agent: DEEPSEEK_API_KEY 未配置")
        yield "系统未配置大模型 API Key。"
        return

    messages = _build_messages(state)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            stream=True
        )
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        logger.error(f"Stream Answer Agent 调用失败: {type(e).__name__}: {e}")
        yield f"抱歉，大模型请求出现异常：{e}"
