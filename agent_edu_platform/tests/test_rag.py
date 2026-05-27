import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from rag_engine import retrieve_knowledge


def test_retriever_returns_evidence():
    evidences = retrieve_knowledge("逻辑回归 标准化 模型评估")

    assert evidences
    assert any("逻辑回归" in evidence.content for evidence in evidences)
