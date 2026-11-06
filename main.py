"""Запуск инструмента построения графа зависимостей npm."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.dependency_graph.config import Config, ConfigError, load_config
from src.dependency_graph.graph import (
    GraphError, build_graph, load_test_repository,
)
from src.dependency_graph.registry import RegistryError, direct_dependencies
from src.dependency_graph.visualization import (
    VisualizationError, ascii_tree, render_png, to_d2,
)


def _forward_graph(config: Config) -> dict[str, list[str]]:
    """Строит обычный граф из тестового файла или npm-реестра."""
    if config.test_mode:
        repository = load_test_repository(config.repository)
        if config.package_name not in repository:
            raise GraphError("заданный пакет отсутствует в графе")
        resolver = repository.__getitem__
    else:
        def resolver(package_name: str):
            """Читает прямые зависимости пакета из npm-реестра."""
            return direct_dependencies(package_name, config.repository)
    return build_graph(config.package_name, resolver)


def main() -> int:
    """Печатает D2 и ASCII-дерево и сохраняет PNG графа."""
    parser = argparse.ArgumentParser(description="Граф зависимостей npm")
    parser.add_argument("--config", default="config.yaml",
                        help="путь к YAML-конфигурации")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        graph = _forward_graph(config)
        description = to_d2(graph)
        render_png(description, Path(config.output_file))
    except (ConfigError, RegistryError, GraphError,
            VisualizationError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    print(f"D2-граф зависимостей {config.package_name}:")
    print(description, end="")
    print(f"PNG: {config.output_file}")
    if config.ascii_tree:
        print("ASCII-дерево:")
        print(ascii_tree(config.package_name, graph), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
