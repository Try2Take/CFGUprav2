"""Проверки рекурсивного BFS и тестового репозитория."""

import tempfile
import unittest
from pathlib import Path

from src.dependency_graph.graph import (
    GraphError, build_graph, load_test_repository,
)


class GraphTests(unittest.TestCase):
    """Проверяет порядок обхода, циклы и входной файл."""

    def test_bfs_visits_each_package_once_in_level_order(self):
        repository = {
            "A": ["B", "C"], "B": ["D"],
            "C": ["D"], "D": ["A"], "E": [],
        }
        visited = []

        def dependencies(name):
            visited.append(name)
            return repository[name]

        graph = build_graph("A", dependencies)

        self.assertEqual(visited, ["A", "B", "C", "D"])
        self.assertEqual(graph, {
            "A": ["B", "C"], "B": ["D"],
            "C": ["D"], "D": ["A"],
        })

    def test_loads_uppercase_test_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "repo.json"
            path.write_text('{"A":["B"],"B":[]}', encoding="utf-8")
            graph = load_test_repository(path)

        self.assertEqual(graph, {"A": ["B"], "B": []})

    def test_rejects_invalid_test_package_name(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "repo.json"
            path.write_text('{"A":["bad"]}', encoding="utf-8")
            with self.assertRaises(GraphError):
                load_test_repository(path)


if __name__ == "__main__":
    unittest.main()
