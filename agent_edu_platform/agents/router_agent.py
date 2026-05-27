import os
from openai import OpenAI
from schemas.agent_state_schema import ChatState

def run_router_agent(state: ChatState) -> ChatState:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("DEEPSEEK_BASE_URL")
    model_name = os.environ.get("OPENAI_MODEL") or os.environ.get("DEEPSEEK_MODEL") or "deepseek-chat"
    
    if not api_key:
        state.next_node = "off_topic"
        return state

    client = OpenAI(api_key=api_key, base_url=base_url)
    
    system_prompt = """你是一个意图分类器。用户的输入分为三类：
1. ask_question：用户针对正在学习的内容提问，或者提出关于机器学习的疑问。
2. submit_quiz：用户在做题，提交了自己的答案。
3. off_topic：用户在闲聊、偏题（如问菜谱、天气等无关内容）。

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
        if "ask_question" in intent:
            state.next_node = "ask_question"
        elif "submit_quiz" in intent:
            state.next_node = "submit_quiz"
        else:
            state.next_node = "off_topic"
    except Exception as e:
        print(f"Router error: {e}")
        state.next_node = "off_topic"
        
    return state
