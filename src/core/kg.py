import networkx as nx
from typing import List
from src.domain.exceptions import KnowledgeGraphNodeError

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._cache = {}

    def add_inclusion(self, parent: str, children: List[str]) -> None:
        for child in children:
            self.graph.add_edge(parent, child)
        self._cache.clear()

    def add_atomic_node(self, node: str) -> None:
        """Adiciona um nó atômico individual (folha) diretamente ao grafo."""
        self.graph.add_node(node)
        self._cache.clear()

    def add_atomic_nodes(self, nodes: List[str]) -> None:
        """Adiciona múltiplos nós atômicos diretamente ao grafo."""
        for node in nodes:
            self.graph.add_node(node)
        self._cache.clear()

    def contains_node(self, node: str) -> bool:
        """Verifica se um nó (seja grupo abstrato ou endpoint atômico) pertence ao grafo."""
        return node in self.graph

    def __contains__(self, node: str) -> bool:
        return node in self.graph

    def get_atomic_nodes(self, node: str) -> List[str]:
        """Retorna os subgrupos não divisíveis (folhas) de um grupo abstrato."""
        if node in self._cache:
            return self._cache[node]

        if node not in self.graph:
            raise KnowledgeGraphNodeError(
                f"O nó '{node}' não foi encontrado no Grafo de Conhecimento."
            )
        
        descendants = nx.descendants(self.graph, node)
        leaves = [n for n in descendants if self.graph.out_degree(n) == 0]
        
        result = leaves if leaves else [node]
        self._cache[node] = result
        return result
