import os


from sentence_transformers import SentenceTransformer

# 全局缓存单例，避免重复加载
_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print("正在加载嵌入模型 BAAI/bge-small-zh-v1.5 (初次可能需要下载)...")
        # bge-small-zh-v1.5 是非常优秀的中文轻量级嵌入模型，输出 512 维向量 (之前版本是768，小版本通常是512)
        _model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
    return _model

def get_embedding(text: str) -> list[float]:
    """获取单个文本片段的向量表示"""
    model = get_embedding_model()
    # 转换为 list 方便处理和存储
    return model.encode(text, normalize_embeddings=True).tolist()

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """批量获取文本片段的向量表示"""
    model = get_embedding_model()
    return model.encode(texts, normalize_embeddings=True).tolist()
