import os
import json
from openai import OpenAI
from schemas.agent_state_schema import ChatState

def run_answer_agent(state: ChatState) -> ChatState:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("DEEPSEEK_BASE_URL")
    model_name = os.environ.get("OPENAI_MODEL") or os.environ.get("DEEPSEEK_MODEL") or "deepseek-chat"
    
    if not api_key:
        state.agent_response = "系统未配置大模型 API Key。"
        return state

    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # 将全量讲义序列化作为 Context
    context_str = json.dumps(state.current_resource_context, ensure_ascii=False) if state.current_resource_context else "无参考讲义"
    
    system_prompt = f"""你是一个温柔且专业的机器学习实训导师。
【当前讲义内容】：
{context_str}

请结合上面的讲义内容，解答学生的疑问。如果问题超出讲义范围但属于机器学习领域，请基于你的专业知识解答。
如果是非常细节的代码疑问，可以结合实操指南的部分进行讲解。"""

    # 拼装历史消息，限制保留最近的 5 轮对话以节省 Token
    messages = [{"role": "system", "content": system_prompt}]
    recent_history = state.chat_history[-10:] if len(state.chat_history) > 10 else state.chat_history
    for msg in recent_history:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
    messages.append({"role": "user", "content": state.user_message})

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7
        )
        state.agent_response = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Answer agent error: {e}")
        state.agent_response = f"抱歉，大模型请求出现异常：{e}"
        
    return state

def stream_answer_agent(state: ChatState):
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("DEEPSEEK_BASE_URL")
    model_name = os.environ.get("OPENAI_MODEL") or os.environ.get("DEEPSEEK_MODEL") or "deepseek-chat"
    
    if not api_key:
        yield "系统未配置大模型 API Key。"
        return

    client = OpenAI(api_key=api_key, base_url=base_url)
    
    context_str = json.dumps(state.current_resource_context, ensure_ascii=False) if state.current_resource_context else "无参考讲义"
    
    system_prompt = f"""你是一个温柔且专业的机器学习实训导师。
【当前讲义内容】：
{context_str}

请结合上面的讲义内容，解答学生的疑问。如果问题超出讲义范围但属于机器学习领域，请基于你的专业知识解答。
如果是非常细节的代码疑问，可以结合实操指南的部分进行讲解。"""

    messages = [{"role": "system", "content": system_prompt}]
    recent_history = state.chat_history[-10:] if len(state.chat_history) > 10 else state.chat_history
    for msg in recent_history:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        
    messages.append({"role": "user", "content": state.user_message})

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
        print(f"Answer agent stream error: {e}")
        yield f"抱歉，大模型请求出现异常：{e}"
