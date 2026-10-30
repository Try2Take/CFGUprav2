"""Запуск инструмента построения графа зависимостей npm."""

from __future__ import annotations

import argparse
import sys

from src.dependency_graph.config import ConfigError, load_config
from src.dependency_graph.graph import (
    GraphError, build_graph, load_test_repository,
)
from src.dependency_graph.registry import RegistryError, direct_dependencies


def main() -> int:
    """Показывает транзитивный граф зависимостей заданного пакета."""
    parser = argparse.ArgumentParser(description="Граф зависимостей npm")
    parser.add_argument("--config", default="config.yaml",
                        help="путь к YAML-конфигурации")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if config.test_mode:
            repository = load_test_repository(config.repository)
            if config.package_name not in repository:
                raise GraphError("заданный пакет отсутствует в графе")
            resolver = repository.__getitem__
        else:
            def resolver(package_name: str):
                """Читает прямые зависимости пакета из npm-реестра."""
                return direct_dependencies(package_name, config.repository)
        graph = build_graph(config.package_name, resolver)
    except (ConfigError, RegistryError, GraphError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    print(f"Граф зависимостей {config.package_name}:")
    for name, dependencies in graph.items():
        names = ", ".join(dependencies) if dependencies else "(нет)"
        print(f"{name} -> {names}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
