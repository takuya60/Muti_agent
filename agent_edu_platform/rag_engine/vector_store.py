import faiss
import json
import numpy as np
from pathlib import Path
from rag_engine.embedding import get_embeddings

class FaissVectorStore:
    def __init__(self, index_dir: Path, vector_dim: int = 512):
        self.index_dir = Path(index_dir)
        self.index_path = self.index_dir / "knowledge.index"
        self.meta_path = self.index_dir / "metadata.json"
        self.vector_dim = vector_dim
        
        self.index = None
        # metadata: dict mapping faiss vector id (int) to document chunks {title, content, source_id, ...}
        self.metadata = {}
        
        self._ensure_dir()
        
    def _ensure_dir(self):
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
    def load(self) -> bool:
        """从磁盘加载现有的 FAISS 索引和元数据"""
        import tempfile
        import shutil
        import os
        
        if self.index_path.exists() and self.meta_path.exists():
            try:
                # 解决 FAISS C++ 底层在 Windows 下不支持中文路径的问题
                # 先把文件拷贝到一个临时的纯英文路径
                fd, temp_path = tempfile.mkstemp(suffix=".index")
                os.close(fd)
                shutil.copy2(self.index_path, temp_path)
                
                self.index = faiss.read_index(temp_path)
                os.remove(temp_path)
                
                with open(self.meta_path, 'r', encoding='utf-8') as f:
                    # json keys are strings, convert back to int
                    raw_meta = json.load(f)
                    self.metadata = {int(k): v for k, v in raw_meta.items()}
                return True
            except Exception as e:
                print(f"加载 FAISS 索引失败: {e}")
        
        # 初始化新的空索引 (使用 L2 距离，如果做了 normalize 则相当于余弦相似度)
        self.index = faiss.IndexFlatL2(self.vector_dim)
        self.metadata = {}
        return False
        
    def save(self):
        """将 FAISS 索引和元数据持久化到磁盘"""
        import tempfile
        import shutil
        import os
        
        if self.index is not None:
            # 解决 FAISS C++ 底层在 Windows 下不支持中文路径的问题
            fd, temp_path = tempfile.mkstemp(suffix=".index")
            os.close(fd)
            
            faiss.write_index(self.index, temp_path)
            shutil.move(temp_path, self.index_path)
            
            with open(self.meta_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def add_documents(self, documents: list[dict]):
        """
        批量添加文档。
        documents 格式应为：[{"title": "...", "content": "...", "source_id": "..."}]
        """
        if not documents:
            return
            
        if self.index is None:
            self.load()
            
        texts = [doc["content"] for doc in documents]
        print(f"正在计算 {len(texts)} 个文本片段的嵌入向量...")
        
        # 获取向量
        embeddings = get_embeddings(texts)
        embeddings_np = np.array(embeddings).astype('float32')
        
        # 获取当前索引的起始 ID
        start_id = self.index.ntotal
        
        # 存入 FAISS
        self.index.add(embeddings_np)
        
        # 存入元数据
        for i, doc in enumerate(documents):
            vector_id = start_id + i
            self.metadata[vector_id] = doc
            
        print(f"成功添加 {len(documents)} 条文档记录。当前总索引数: {self.index.ntotal}")

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """检索最相似的片段"""
        if self.index is None or self.index.ntotal == 0:
            return []
            
        # 查询文本转向量
        query_emb = get_embeddings([query])[0]
        query_np = np.array([query_emb]).astype('float32')
        
        # FAISS 近似最近邻检索
        distances, indices = self.index.search(query_np, top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = int(indices[0][i])
            if idx != -1 and idx in self.metadata:
                dist = float(distances[0][i])
                # L2 越小越相似，这里做一个粗略的置信度转换 (只作相对参考)
                score = max(0.0, 1.0 - (dist / 2.0))
                
                doc = dict(self.metadata[idx])
                doc["score"] = score
                results.append(doc)
                
        return results
