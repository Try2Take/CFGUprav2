"""Проверки запуска приложения первого этапа."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    """Запускает реальную команду в отдельном процессе."""

    def test_prints_all_settings_as_key_value_pairs(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.yaml"
            config_path.write_text(
                "package_name: express\n"
                "repository: https://registry.npmjs.org\n"
                "test_mode: false\n"
                "output_file: graph.png\n"
                "ascii_tree: true\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "main.py"),
                    "--config",
                    str(config_path),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "package_name=express",
                "repository=https://registry.npmjs.org",
                "test_mode=false",
                "output_file=graph.png",
                "ascii_tree=true",
            ],
        )
        self.assertEqual(result.stderr, "")

    def test_reports_configuration_errors_without_traceback(self):
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

    def test_run_script_finds_default_config_from_another_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            environment = os.environ.copy()
            environment["PATH"] = (
                f"{Path(sys.executable).parent}:{environment['PATH']}"
            )
            result = subprocess.run(
                ["bash", str(PROJECT_ROOT / "run.sh")],
                cwd=directory,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("package_name=express", result.stdout)


if __name__ == "__main__":
    unittest.main()
