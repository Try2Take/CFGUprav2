"""Проверки вывода прямых зависимостей и ошибок запуска."""

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

    def test_prints_direct_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.yaml"
            config_path.write_text(
                "package_name: express\n"
                "repository: https://registry.npmjs.org\n"
                "test_mode: false\n"
                "output_file: graph.png\n"
                "ascii_tree: false\n",
                encoding="utf-8",
            )
            output = StringIO()
            with patch.object(sys, "argv", ["main.py", "--config",
                                           str(config_path)]), \
                    patch("main.direct_dependencies", return_value={
                        "zeta": "^2", "alpha": "~1",
                    }) as fetch, redirect_stdout(output):
                status = main()

        self.assertEqual(status, 0)
        fetch.assert_called_once_with("express", "https://registry.npmjs.org")
        self.assertEqual(output.getvalue().splitlines(), [
            "Прямые зависимости express:", "alpha: ~1", "zeta: ^2",
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
