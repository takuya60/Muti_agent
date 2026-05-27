import pytest
from rag_engine.retriever import retrieve_knowledge, keyword_retrieve, vector_retrieve

def test_keyword_retrieve():
    results = keyword_retrieve("回归", limit=2)
    assert isinstance(results, list)
    # 即使没有找到，也应该返回列表

def test_hybrid_retrieve_structure():
    results = retrieve_knowledge("什么是梯度下降？", limit=3)
    assert isinstance(results, list)
    if len(results) > 0:
        evidence = results[0]
        assert hasattr(evidence, "title")
        assert hasattr(evidence, "content")
        assert hasattr(evidence, "source_id")
        assert hasattr(evidence, "score")
        # 确保 score 返回为 float
        assert isinstance(evidence.score, float)
