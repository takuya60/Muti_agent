# RAG 引擎升级方案 (Phase 1.3)

根据我们的开发约定，下面是**阶段 1 的第 3 项任务：RAG 引擎升级（引入向量检索）**的具体技术方案。

目前系统中的检索是极其基础的“关键词匹配”（在 `retriever.py` 中写死的数据字典匹配），这在面对 50+ 篇文档时完全无法应对用户的长难句提问。为了达到企业级，我们将引入真正的**向量检索 (Vector Search)**。

## 1. 依赖与核心选型
- **嵌入模型 (Embedding Model)**: 采用目前中文圈轻量且表现优异的 `BAAI/bge-small-zh-v1.5`。它非常小（大概一百多MB），可以在普通 CPU 上秒级运行，不用担心评委没显卡跑不动。
- **向量库 (Vector Store)**: 采用 Facebook 的 `faiss-cpu`。不需要额外部署中间件（比如 ChromaDB 或 Milvus），FAISS 可以直接把向量索引存为本地的一个 `.index` 文件，随走随用。

## 2. 代码实现设计

### `rag_engine/embedding.py`
使用 `sentence-transformers` 封装加载 `bge-small-zh` 模型，暴露一个 `get_embedding(text)` 方法，负责将用户提问或文档切片转化为 768 维的浮点数组。

### `rag_engine/vector_store.py`
定义 `FaissVectorStore` 类：
- `add_documents(documents)`: 接收文本块，调 embedding 变向量，存入 faiss 索引，并维护一个映射字典记录 `index_id -> document_metadata (title, source_id, chunk_text)`。
- `search(query, top_k)`: 把 query 变向量，在 FAISS 中做近似最近邻 (ANN) 检索，返回最相关的几条文本快照。
- `save_local()` / `load_local()`: 把索引和元数据保存到硬盘 `data/vector_store/` 目录下。

### `scripts/build_vector_store.py`
构建脚本。它的作用是：
1. 遍历 `data/knowledge_base/processed` 目录下的所有 Markdown 讲义。
2. 进行最基础的按段落切分 (Chunking)。
3. 调用 `FaissVectorStore.add_documents` 并保存到本地，生成真正的索引库。

##  开放问题与确认项
> [!IMPORTANT]
> 1. 关于嵌入模型 `bge-small-zh-v1.5`，它第一次运行会自动从 HuggingFace 下载。由于国内网络原因，HuggingFace 可能连不上。您希望我在代码中配置 HF 镜像源以防万一吗？
> 2. 当前我们采用“离线 FAISS”方案。如果是真正的大型企业应用可能会用 Milvus，但在挑战杯中我们优先保证便携性（拷贝即走）。您同意这个设计权衡吗？

请您审阅此方案。确认后我就开始写这套真正有含金量的 RAG 底层代码。
