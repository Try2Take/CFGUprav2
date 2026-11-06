"""Проверки вывода графа зависимостей и ошибок запуска."""

import subprocess
import tempfile
import unittest
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    """Проверяет результат запуска с YAML-конфигурацией."""

    def test_prints_d2_and_ascii_tree_and_saves_png(self):
        with tempfile.TemporaryDirectory() as directory:
            repository_path = Path(directory) / "repo.json"
            repository_path.write_text(
                '{"A":["B"],"B":["A"]}', encoding="utf-8"
            )
            config_path = Path(directory) / "config.yaml"
            config_path.write_text(
                "package_name: A\n"
                "repository: repo.json\n"
                "test_mode: true\n"
                "output_file: graph.png\n"
                "ascii_tree: true\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "main.py"),
                 "--config", str(config_path)],
                cwd=directory, text=True, capture_output=True,
                check=False,
            )
            image = Path(directory) / "graph.png"
            self.assertTrue(image.is_file())
            self.assertEqual(image.read_bytes()[:8],
                             b"\x89PNG\r\n\x1a\n")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"A" -> "B"', result.stdout)
        self.assertIn('"B" -> "A"', result.stdout)
        self.assertIn("`-- B", result.stdout)

    def test_reports_configuration_error_without_traceback(self):
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "main.py"),
             "--config", "missing.yaml"],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Ошибка:", result.stderr)
        self.assertIn("missing.yaml", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

if __name__ == "__main__":
    unittest.main()
