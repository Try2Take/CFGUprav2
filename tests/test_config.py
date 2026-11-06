"""Проверки пользовательских настроек первого этапа."""

import tempfile
import unittest
from pathlib import Path

from src.dependency_graph.config import ConfigError, load_config


VALID_CONFIG = (
    "package_name: express\n"
    "repository: https://registry.npmjs.org\n"
    "test_mode: false\n"
    "output_file: graph.png\n"
    "ascii_tree: true\n"
)


class ConfigTests(unittest.TestCase):
    """Проверяет значения и ошибки, видимые пользователю."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.config_path = self.root / "config.yaml"

    def write_config(self, content=VALID_CONFIG):
        """Сохраняет YAML-конфигурацию во временном каталоге."""
        self.config_path.write_text(content, encoding="utf-8")

    def test_loads_five_settings_from_yaml(self):
        self.write_config()

        config = load_config(self.config_path)

        self.assertEqual(config.package_name, "express")
        self.assertEqual(config.repository, "https://registry.npmjs.org")
        self.assertIs(config.test_mode, False)
        self.assertEqual(config.output_file, "graph.png")
        self.assertIs(config.ascii_tree, True)

    def test_rejects_stage_four_only_mode(self):
        self.write_config(VALID_CONFIG + "reverse_mode: true\n")

        with self.assertRaisesRegex(ConfigError, "неизвестный параметр"):
            load_config(self.config_path)

    def test_resolves_test_repository_relative_to_config(self):
        repository = self.root / "repo.yaml"
        repository.write_text("A: []\n", encoding="utf-8")
        self.write_config(
            VALID_CONFIG.replace("express", "A")
            .replace("https://registry.npmjs.org", "repo.yaml")
            .replace("test_mode: false", "test_mode: true")
        )

        config = load_config(self.config_path)

        self.assertEqual(config.repository, str(repository.resolve()))

    def test_rejects_invalid_package_name(self):
        self.write_config(VALID_CONFIG.replace("express", "bad package"))

        with self.assertRaisesRegex(ConfigError, "package_name"):
            load_config(self.config_path)

    def test_rejects_invalid_repository_url(self):
        self.write_config(
            VALID_CONFIG.replace(
                "https://registry.npmjs.org", "not-a-url"
            )
        )

        with self.assertRaisesRegex(ConfigError, "repository"):
            load_config(self.config_path)

    def test_rejects_missing_test_repository_file(self):
        self.write_config(
            VALID_CONFIG.replace("express", "A")
            .replace("https://registry.npmjs.org", "missing.yaml")
            .replace("test_mode: false", "test_mode: true")
        )

        with self.assertRaisesRegex(ConfigError, "repository"):
            load_config(self.config_path)

    def test_rejects_non_boolean_test_mode(self):
        self.write_config(
            VALID_CONFIG.replace("test_mode: false", "test_mode: maybe")
        )

        with self.assertRaisesRegex(ConfigError, "test_mode"):
            load_config(self.config_path)

    def test_rejects_invalid_output_filename(self):
        self.write_config(
            VALID_CONFIG.replace("graph.png", "graph.svg")
        )

        with self.assertRaisesRegex(ConfigError, "output_file"):
            load_config(self.config_path)

    def test_rejects_non_boolean_ascii_tree(self):
        self.write_config(
            VALID_CONFIG.replace("ascii_tree: true", "ascii_tree: 1")
        )

        with self.assertRaisesRegex(ConfigError, "ascii_tree"):
            load_config(self.config_path)

    def test_rejects_missing_setting(self):
        self.write_config(
            VALID_CONFIG.replace("output_file: graph.png\n", "")
        )

        with self.assertRaisesRegex(ConfigError, "output_file"):
            load_config(self.config_path)

    def test_rejects_malformed_yaml(self):
        self.write_config("package_name: [\n")

        with self.assertRaises(ConfigError):
            load_config(self.config_path)

    def test_rejects_missing_config_file(self):
        with self.assertRaises(ConfigError):
            load_config(self.config_path)


if __name__ == "__main__":
    unittest.main()
