"""Проверки вывода графа зависимостей и ошибок запуска."""

import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from main import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    """Проверяет результат запуска с YAML-конфигурацией."""

    def test_prints_test_graph_with_cycle(self):
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
                "ascii_tree: false\n",
                encoding="utf-8",
            )
            output = StringIO()
            with patch.object(sys, "argv", ["main.py", "--config",
                                           str(config_path)]):
                with redirect_stdout(output):
                    status = main()

        self.assertEqual(status, 0)
        self.assertEqual(output.getvalue().splitlines(), [
            "Граф зависимостей A:", "A -> B", "B -> A",
        ])

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
