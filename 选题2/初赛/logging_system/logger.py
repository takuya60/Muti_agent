import json
import time
from pathlib import Path
from datetime import datetime

class ProblemLogger:
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    
    def log(self, entry: dict):
        """追加一条日志"""
        entry["timestamp"] = datetime.now().isoformat()
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
