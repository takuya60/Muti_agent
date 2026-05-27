import json
import sys
from pathlib import Path

# Add project root to path so we can import from backend
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from backend.database import Base, engine, SessionLocal, DATA_DIR
from backend.models import Learner, Session, Message, QuizAttempt

def init_db():
    print("正在创建数据库表结构...")
    Base.metadata.create_all(bind=engine)
    print("数据库表结构创建完成！")

def migrate_learner_profiles():
    db = SessionLocal()
    try:
        profiles_dir = DATA_DIR / "learner_profiles"
        if not profiles_dir.exists():
            print(f"未找到 JSON 画像目录: {profiles_dir}")
            return
            
        print("开始迁移本地 JSON 画像数据到数据库...")
        json_files = list(profiles_dir.glob("*.json"))
        
        count = 0
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if exists
                existing = db.query(Learner).filter(Learner.id == data.get("learner_id")).first()
                if existing:
                    print(f"画像 {data.get('learner_id')} 已存在，跳过。")
                    continue
                
                learner = Learner(
                    id=data.get("learner_id"),
                    name=data.get("name", "Unknown"),
                    background=data.get("background", ""),
                    goal=data.get("goal", ""),
                    preferred_style=data.get("preferred_style", "案例驱动"),
                    test_scores=data.get("test_scores", {}),
                    known_skills=data.get("known_skills", []),
                    weak_points=data.get("weak_points", []),
                    mastered_points=[],
                    current_level="beginner_plus"
                )
                db.add(learner)
                count += 1
            except Exception as e:
                print(f"迁移文件 {json_file.name} 时出错: {e}")
                
        db.commit()
        print(f"成功迁移了 {count} 个学习者画像记录！")
    finally:
        db.close()

if __name__ == "__main__":
    print(f"=== AgentEdu 数据库初始化脚本 ===")
    print(f"数据库路径: {DATA_DIR / 'agent_edu.db'}")
    init_db()
    migrate_learner_profiles()
    print("=== 初始化完成 ===")
