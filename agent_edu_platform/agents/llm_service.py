import json
import logging
from openai import OpenAI
from backend.config import settings

logger = logging.getLogger(__name__)

def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    timeout: float = 30.0,
    temperature: float = 0.3,
) -> dict:
    """
    调用 DeepSeek LLM 并返回解析后的 JSON dict。
    失败时抛出异常，由调用方决定如何 fallback。
    """
    api_key = settings.DEEPSEEK_API_KEY
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY 未配置")
        
    client = OpenAI(api_key=api_key, base_url=settings.DEEPSEEK_BASE_URL)
    
    response = client.chat.completions.create(
        model=settings.DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        timeout=timeout,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content.strip()
    return json.loads(content)
