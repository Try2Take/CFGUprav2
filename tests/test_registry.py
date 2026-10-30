"""Проверки получения прямых зависимостей из npm-реестра."""

import unittest
from io import BytesIO
from unittest.mock import patch

from src.dependency_graph.registry import direct_dependencies


class RegistryTests(unittest.TestCase):
    """Проверяет чтение манифеста и адрес пакета."""

    def test_reads_only_direct_dependencies(self):
        body = (
            b'{"dependencies":{"accepts":"^2","body-parser":"^2.0"},'
            b'"devDependencies":{"mocha":"^10"}}'
        )
        with patch("src.dependency_graph.registry.urlopen",
                   return_value=BytesIO(body)) as request:
            dependencies = direct_dependencies(
                "express", "https://registry.npmjs.org"
            )

        self.assertEqual(dependencies, {
            "accepts": "^2", "body-parser": "^2.0",
        })
        self.assertEqual(
            request.call_args.args[0].full_url,
            "https://registry.npmjs.org/express/latest",
        )

    def test_encodes_scoped_package_name(self):
        with patch("src.dependency_graph.registry.urlopen",
                   return_value=BytesIO(b'{"dependencies":{}}')) as request:
            dependencies = direct_dependencies(
                "@scope/name", "https://registry.npmjs.org"
            )

        self.assertEqual(dependencies, {})
        self.assertEqual(
            request.call_args.args[0].full_url,
            "https://registry.npmjs.org/@scope%2Fname/latest",
        )


if __name__ == "__main__":
    unittest.main()
