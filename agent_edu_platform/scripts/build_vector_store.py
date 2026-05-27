import os
import sys
import uuid
from pathlib import Path
import shutil

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from rag_engine.vector_store import FaissVectorStore

DATA_DIR = PROJECT_ROOT / "data"
KB_DIR = DATA_DIR / "knowledge_base" / "processed"
VECTOR_DIR = DATA_DIR / "vector_store"

def chunk_markdown(file_path: Path) -> list[dict]:
    """简单的 Markdown 文本切片逻辑（按二级标题划分）"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    title = file_path.stem
    source_id = file_path.name
    source_path = str(file_path.relative_to(PROJECT_ROOT))
    
    chunks = []
    lines = content.split('\n')
    current_heading = title
    current_content = []
    
    for line in lines:
        if line.startswith('## '):
            if current_content:
                text = '\n'.join(current_content).strip()
                if text:
                    chunks.append({
                        "chunk_id": str(uuid.uuid4()),
                        "source_id": source_id,
                        "source_path": source_path,
                        "title": f"{title} - {current_heading}",
                        "heading": current_heading,
                        "knowledge_points": [title], # 暂用文件名作为粗粒度知识点标签
                        "content": text
                    })
            current_heading = line.replace('## ', '').strip()
            current_content = [line]
        else:
            current_content.append(line)
            
    if current_content:
        text = '\n'.join(current_content).strip()
        if text:
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "source_id": source_id,
                "source_path": source_path,
                "title": f"{title} - {current_heading}",
                "heading": current_heading,
                "knowledge_points": [title],
                "content": text
            })
            
    return chunks

def build_index(rebuild: bool = True):
    print("=== 开始构建 RAG 向量知识库 ===")
    
    if not KB_DIR.exists():
        print(f"找不到知识库目录: {KB_DIR}")
        return
        
    if rebuild and VECTOR_DIR.exists():
        print("清理旧的向量索引目录...")
        shutil.rmtree(VECTOR_DIR)
        
    store = FaissVectorStore(index_dir=VECTOR_DIR, vector_dim=512)
    
    all_chunks = []
    md_files = list(KB_DIR.glob("*.md"))
    
    print(f"发现 {len(md_files)} 篇讲义文档。正在切片...")
    
    for md_file in md_files:
        chunks = chunk_markdown(md_file)
        all_chunks.extend(chunks)
        
    print(f"切片完成，共获得 {len(all_chunks)} 个知识块。")
    print("开始生成 Embedding 向量并存入 FAISS...")
    
    store.add_documents(all_chunks)
    store.save()
    
    print(f"=== 向量库构建完成！已保存至 {VECTOR_DIR} ===")

if __name__ == "__main__":
    # 默认执行重建模式
    build_index(rebuild=True)
