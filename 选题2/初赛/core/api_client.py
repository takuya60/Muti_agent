import time
import logging
from openai import OpenAI
from core.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    """LLM API 封装，带重试和日志"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        self.api_key = api_key or settings.API_KEY
        self.base_url = base_url or settings.BASE_URL
        self.model = model or settings.MODEL
        
        if not self.api_key:
            logger.warning("未配置 DEEPSEEK_API_KEY")
            
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.max_retries = 3
        self.retry_delay = 2.0  # 秒
    
    def call(self, problem: str, system_prompt: str = "", temperature: float = 0.3) -> str | None:
        """调用 API，失败自动重试，返回模型回复文本"""
        if not self.api_key:
             return "【系统提示】缺少 API KEY，无法调用模型"
             
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": problem})
        
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    timeout=300.0,
                )
                content = response.choices[0].message.content.strip()
                if content:
                    return content
                logger.warning(f"API 返回空内容 (第 {attempt} 次)")
            except Exception as e:
                logger.error(f"API 调用失败 (第 {attempt} 次): {e}")
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** (attempt - 1))
                    logger.info(f"等待 {delay}s 后重试...")
                    time.sleep(delay)
        
        logger.error("API 调用已达最大重试次数，放弃")
        return None
