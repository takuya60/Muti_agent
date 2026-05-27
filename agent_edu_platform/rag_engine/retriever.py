from pathlib import Path
from schemas.agent_state_schema import KnowledgeEvidence
from rag_engine.vector_store import FaissVectorStore

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VECTOR_DIR = PROJECT_ROOT / "data" / "vector_store"
KB_DIR = PROJECT_ROOT / "data" / "knowledge_base" / "processed"

# 单例缓存向量库
_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        try:
            store = FaissVectorStore(index_dir=VECTOR_DIR, vector_dim=512)
            if store.load():
                _vector_store = store
            else:
                print("向量库尚未构建或为空，降级到关键词检索。")
        except Exception as e:
            print(f"初始化 FAISS 失败: {e}")
    return _vector_store

def keyword_retrieve(query: str, limit: int = 3) -> list[KnowledgeEvidence]:
    """基于本地文件的 fallback 关键词检索"""
    evidences = []
    if not KB_DIR.exists():
        return evidences
        
    for md_file in KB_DIR.glob("*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 极简的关键词匹配：只要 query 里的字在文本里出现的多，就认为有关
            # 真实场景可以用 BM25，这里用粗糙的 fallback
            if any(kw in content for kw in query.split()) or md_file.stem in query:
                snippet = content[:500] + "..." if len(content) > 500 else content
                evidences.append(
                    KnowledgeEvidence(
                        title=md_file.stem,
                        content=snippet,
                        source_id=md_file.name,
                        score=0.5  # 关键词检索置信度固定
                    )
                )
                if len(evidences) >= limit:
                    break
    return evidences

def vector_retrieve(query: str, limit: int = 3) -> list[KnowledgeEvidence]:
    """基于 FAISS 的语义向量检索"""
    store = get_vector_store()
    if not store:
        return []
        
    results = store.search(query, top_k=limit)
    evidences = []
    for r in results:
        # Strict RAG 控制：如果相似度过低，直接舍弃
        if r.get("score", 0) < 0.3:
            continue
            
        evidences.append(
            KnowledgeEvidence(
                title=r.get("title", ""),
                content=r.get("content", ""),
                source_id=r.get("source_path", r.get("source_id", "")),
                score=r.get("score", 0.0)
            )
        )
    return evidences

def hybrid_retrieve(query: str, limit: int = 3) -> list[KnowledgeEvidence]:
    """混合检索：先尝试向量检索，如果数量不足用关键词检索兜底，然后去重合并"""
    vec_results = vector_retrieve(query, limit)
    
    # 严格 RAG 需求：如果向量检索没有高质量结果，且用户倾向严谨回答，应该宁缺毋滥。
    # 这里我们通过阈值过滤。如果有向量检索结果，优先用向量；如果向量库完全挂了，降级用关键词。
    if len(vec_results) > 0:
        return vec_results[:limit]
        
    # Fallback to keyword
    kw_results = keyword_retrieve(query, limit)
    return kw_results[:limit]

def retrieve_knowledge(query: str, limit: int = 3) -> list[KnowledgeEvidence]:
    """对外暴露的唯一检索入口"""
    return hybrid_retrieve(query, limit)
