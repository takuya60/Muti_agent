import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # 路径配置
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    PROBLEMS_DIR = os.path.join(DATA_DIR, "problems")
    RESULTS_DIR = os.path.join(DATA_DIR, "results")
    LOGS_DIR = os.path.join(DATA_DIR, "logs")

settings = Settings()
