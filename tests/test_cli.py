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

    def test_prints_reverse_dependencies_from_test_repository(self):
        repository = PROJECT_ROOT / "examples" / "test-repository.json"
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "reverse.yaml"
            config_path.write_text(
                "package_name: D\n"
                f"repository: {repository}\n"
                "test_mode: true\n"
                "output_file: graph.png\n"
                "ascii_tree: false\n"
                "reverse_mode: true\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "main.py"),
                 "--config", str(config_path)],
                cwd=PROJECT_ROOT, text=True, capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "Обратные зависимости D:", "B", "C", "A",
        ])

    def test_prints_reverse_dependencies_from_npm_scope(self):
        manifests = {
            "is-even": {"is-odd": "^0.1.2"},
            "is-odd": {"is-number": "^6.0.0"},
            "is-number": {},
        }
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "reverse-npm.yaml"
            config_path.write_text(
                "package_name: is-number\n"
                "repository: https://registry.npmjs.org\n"
                "test_mode: false\n"
                "output_file: graph.png\n"
                "ascii_tree: false\n"
                "reverse_mode: true\n"
                "graph_root: is-even\n",
                encoding="utf-8",
            )
            with patch.object(sys, "argv", ["main.py", "--config",
                                           str(config_path)]):
                with patch("main.direct_dependencies",
                           side_effect=lambda name, _: manifests[name]):
                    output = StringIO()
                    with redirect_stdout(output):
                        status = main()

        self.assertEqual(status, 0)
        self.assertEqual(output.getvalue().splitlines(), [
            "Обратные зависимости is-number:", "is-odd", "is-even",
        ])


if __name__ == "__main__":
    unittest.main()
