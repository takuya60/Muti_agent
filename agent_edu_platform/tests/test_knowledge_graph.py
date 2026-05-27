import pytest
from knowledge_graph.graph_builder import KnowledgeGraphManager

def test_graph_manager():
    kg = KnowledgeGraphManager()
    
    # 假设目标是 logistic_regression，但是没有掌握任何前置
    # 它应该推荐从最基础的开始，例如 python_basics 或者其他根节点
    recommend = kg.recommend_next_node("logistic_regression", [])
    assert recommend is not None
    assert recommend != "logistic_regression"  # 因为没有掌握前置，所以一定推荐某个前置
    
    # 测试全路径推荐
    path = kg.recommend_learning_path("logistic_regression", [])
    assert len(path) > 1
    assert path[-1] == "logistic_regression"
    
    # 如果把所有前置都掌握了，应该推荐目标节点本身
    all_prereqs = kg.get_all_prerequisites("logistic_regression")
    recommend_target = kg.recommend_next_node("logistic_regression", all_prereqs)
    assert recommend_target == "logistic_regression"
