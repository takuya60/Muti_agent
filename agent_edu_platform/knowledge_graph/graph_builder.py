import json
import networkx as nx
from pathlib import Path

class KnowledgeGraphManager:
    def __init__(self, json_path: str = None):
        if json_path:
            self.data_path = Path(json_path)
        else:
            self.data_path = Path(__file__).resolve().parent / "data" / "ml_knowledge_graph.json"
            
        self.graph = nx.DiGraph()
        self.nodes_meta = {}
        self._load_graph()

    def _load_graph(self):
        """从 JSON 文件加载图谱结构"""
        if not self.data_path.exists():
            print(f"警告：未找到知识图谱文件 {self.data_path}")
            return
            
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for node in data.get("nodes", []):
            node_id = node["id"]
            self.graph.add_node(node_id, **node)
            self.nodes_meta[node_id] = node
            
        for edge in data.get("edges", []):
            from_id = edge["from"]
            to_id = edge["to"]
            edge_type = edge.get("type", "related")
            self.graph.add_edge(from_id, to_id, relation_type=edge_type)

    def get_prerequisites(self, target_node: str) -> list[str]:
        """获取目标节点的所有前置节点 (逆向追踪)"""
        if target_node not in self.graph:
            return []
            
        # 寻找所有指向 target_node 且类型为 prerequisite 的边
        prereqs = []
        for u, v, data in self.graph.in_edges(target_node, data=True):
            if data.get("relation_type") == "prerequisite":
                prereqs.append(u)
        return prereqs

    def get_all_prerequisites(self, target_node: str) -> list[str]:
        """获取目标节点的所有前置节点链（从最基础的开始）"""
        if target_node not in self.graph:
            return []
        
        prereqs_set = set()
        queue = [target_node]
        
        while queue:
            current = queue.pop(0)
            direct_prereqs = self.get_prerequisites(current)
            for p in direct_prereqs:
                if p not in prereqs_set:
                    prereqs_set.add(p)
                    queue.append(p)
        
        subgraph = self.graph.subgraph(list(prereqs_set))
        try:
            return list(nx.topological_sort(subgraph))
        except nx.NetworkXUnfeasible:
            return list(prereqs_set)

    def recommend_learning_path(self, target_node: str, mastered_nodes: list[str]) -> list[str]:
        """推荐通向目标的完整未掌握学习路径"""
        all_prereqs = self.get_all_prerequisites(target_node)
        path = [p for p in all_prereqs if p not in mastered_nodes]
        if target_node not in mastered_nodes:
            path.append(target_node)
        return path

    def recommend_next_node(self, target_node: str, mastered_nodes: list[str]) -> str:
        """
        核心算法：根据当前目标，和用户已掌握的知识点，推荐下一步应该学什么
        返回应该学习的 node_id
        """
        if target_node not in self.graph:
            return target_node
            
        # 1. 如果目标节点已经掌握，那么找它的后续节点
        if target_node in mastered_nodes:
            successors = list(self.graph.successors(target_node))
            unmastered_successors = [n for n in successors if n not in mastered_nodes]
            if unmastered_successors:
                return unmastered_successors[0]
            return target_node # 已经到头了
            
        # 2. 如果目标节点未掌握，检查它的前置是否都掌握了
        # 使用 BFS 或 DFS 逆向回溯，找到第一个缺失的前置知识
        def find_missing_prereq(node):
            prereqs = self.get_prerequisites(node)
            for p in prereqs:
                if p not in mastered_nodes:
                    # 递归检查这个缺失的前置，看它是不是还有缺失的前置
                    deeper_missing = find_missing_prereq(p)
                    if deeper_missing:
                        return deeper_missing
                    return p
            return None
            
        missing_prereq = find_missing_prereq(target_node)
        
        # 如果有缺失的前置，推荐去学前置；如果前置都满足了，推荐学当前目标
        return missing_prereq if missing_prereq else target_node
        
    def get_subgraph_for_visualization(self, focus_node: str = None) -> dict:
        """导出用于前端 ECharts / G6 渲染的结构"""
        return {
            "nodes": [data for _, data in self.graph.nodes(data=True)],
            "edges": [{"from": u, "to": v, "type": d.get("relation_type")} for u, v, d in self.graph.edges(data=True)]
        }

# 简单测试代码
if __name__ == "__main__":
    kg = KnowledgeGraphManager()
    print("图谱加载完成，节点数:", kg.graph.number_of_nodes())
    
    target = "logistic_regression"
    mastered = ["python_basics", "numpy_basics"]
    
    recommend = kg.recommend_next_node(target, mastered)
    print(f"目标: {target}, 已掌握: {mastered} -> 推荐下一步学习: {recommend}")
