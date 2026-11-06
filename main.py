"""Запуск инструмента построения графа зависимостей npm."""

from __future__ import annotations

import argparse
import sys

from src.dependency_graph.config import Config, ConfigError, load_config
from src.dependency_graph.graph import (
    GraphError, build_graph, load_test_repository, reverse_graph,
)
from src.dependency_graph.registry import RegistryError, direct_dependencies


def _reverse_dependencies(config: Config) -> list[str]:
    """Ищет обратные зависимости в тестовом или ограниченном npm-графе."""
    if config.test_mode:
        graph = load_test_repository(config.repository)
    else:
        graph = _forward_graph(config, config.graph_root)
    if config.package_name not in graph:
        raise GraphError("заданный пакет отсутствует в графе")
    reversed_graph = reverse_graph(graph)
    visited = build_graph(config.package_name, reversed_graph.__getitem__)
    return list(visited)[1:]


def _forward_graph(
    config: Config, package_name: str | None = None,
) -> dict[str, list[str]]:
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
    return build_graph(package_name or config.package_name, resolver)


def _print_forward_graph(
    package_name: str, graph: dict[str, list[str]],
) -> None:
    """Печатает связи обычного графа в порядке BFS."""
    print(f"Граф зависимостей {package_name}:")
    for name, dependencies in graph.items():
        names = ", ".join(dependencies) if dependencies else "(нет)"
        print(f"{name} -> {names}")


def main() -> int:
    """Показывает граф или обратные зависимости пакета."""
    parser = argparse.ArgumentParser(description="Граф зависимостей npm")
    parser.add_argument("--config", default="config.yaml",
                        help="путь к YAML-конфигурации")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if config.reverse_mode:
            reverse_names = _reverse_dependencies(config)
        else:
            graph = _forward_graph(config)
    except (ConfigError, RegistryError, GraphError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    if config.reverse_mode:
        print(f"Обратные зависимости {config.package_name}:")
        print("\n".join(reverse_names) if reverse_names else "(нет)")
    else:
        _print_forward_graph(config.package_name, graph)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
