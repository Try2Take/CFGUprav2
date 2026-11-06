"""Проверки текста D2, ASCII-дерева и создания PNG."""

import tempfile
import unittest
from pathlib import Path

from src.dependency_graph.visualization import (
    VisualizationError, ascii_tree, render_png, to_d2,
)


class VisualizationTests(unittest.TestCase):
    """Проверяет три результата визуализации графа."""

    def setUp(self):
        self.graph = {
            "A": ["B", "C"], "B": ["D"],
            "C": ["D"], "D": ["A"],
        }

    def test_d2_contains_every_edge_including_cycle(self):
        self.assertEqual(to_d2(self.graph), (
            '"A" -> "B"\n"A" -> "C"\n'
            '"B" -> "D"\n"C" -> "D"\n"D" -> "A"\n'
        ))

    def test_d2_keeps_isolated_package(self):
        self.assertEqual(to_d2({"E": []}), '"E"\n')

    def test_ascii_tree_marks_repeated_packages(self):
        self.assertEqual(ascii_tree("A", self.graph), (
            "A\n|-- B\n|   `-- D\n|       `-- A (повтор)\n"
            "`-- C\n    `-- D (повтор)\n"
        ))

    def test_renderer_reports_missing_d2(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(VisualizationError, "D2"):
                render_png('"E"\n', Path(directory) / "e.png",
                           executable="missing-d2-binary")


if __name__ == "__main__":
    unittest.main()
