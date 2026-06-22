import os
import time
import json
import logging
import datetime
from openai import OpenAI
from backend.config import settings

logger = logging.getLogger(__name__)

# 确保 logs 目录存在
os.makedirs("logs", exist_ok=True)
LLM_TRACE_FILE = "logs/llm_trace.jsonl"

def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    timeout: float = 30.0,
    temperature: float = 0.3,
) -> dict:
    """
    调用 DeepSeek LLM 并返回解析后的 JSON dict。
    失败时抛出异常，由调用方决定如何 fallback。
    同时会将完整的调用链路写入 logs/llm_trace.jsonl，便于后续复现幻觉。
    """
    api_key = settings.DEEPSEEK_API_KEY
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY 未配置")
        
    client = OpenAI(api_key=api_key, base_url=settings.DEEPSEEK_BASE_URL)
    
    start_time = time.time()
    error_msg = None
    raw_content = ""
    
    try:
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
        raw_content = response.choices[0].message.content.strip()
        parsed_data = json.loads(raw_content)
        return parsed_data
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(f"[LLM Error] 调用大模型失败: {error_msg}\nRaw Content:\n{raw_content}")
        raise
    finally:
        latency = time.time() - start_time
        
        # 本地 Trace 存盘
        trace_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "latency": round(latency, 2),
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "raw_response": raw_content,
            "error": error_msg
        }
        
        try:
            with open(LLM_TRACE_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(trace_record, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning(f"写入 LLM Trace 失败: {e}")
