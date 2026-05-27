import os
import sys
from pathlib import Path

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
    
    # 按行扫描，遇到 ## 则认为是一个新的 Chunk 块
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
                        "source_id": source_id,
                        "title": f"{title} - {current_heading}",
                        "content": text
                    })
            current_heading = line.replace('## ', '').strip()
            current_content = [line]
        else:
            current_content.append(line)
            
    # 最后一个 chunk
    if current_content:
        text = '\n'.join(current_content).strip()
        if text:
            chunks.append({
                "source_id": source_id,
                "title": f"{title} - {current_heading}",
                "content": text
            })
            
    return chunks

def build_index():
    print("=== 开始构建 RAG 向量知识库 ===")
    
    if not KB_DIR.exists():
        print(f"找不到知识库目录: {KB_DIR}")
        return
        
    store = FaissVectorStore(index_dir=VECTOR_DIR)
    
    all_chunks = []
    md_files = list(KB_DIR.glob("*.md"))
    
    print(f"发现 {len(md_files)} 篇讲义文档。正在切片...")
    
    for md_file in md_files:
        chunks = chunk_markdown(md_file)
        all_chunks.extend(chunks)
        
    print(f"切片完成，共获得 {len(all_chunks)} 个知识块。")
    print("开始生成 Embedding 向量并存入 FAISS (首次运行将下载 bge-small-zh 模型)...")
    
    store.add_documents(all_chunks)
    store.save()
    
    print(f"=== 向量库构建完成！已保存至 {VECTOR_DIR} ===")

if __name__ == "__main__":
    build_index()
