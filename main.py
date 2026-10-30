"""Запуск инструмента построения графа зависимостей npm."""

from __future__ import annotations

import argparse
import sys

from src.dependency_graph.config import ConfigError, load_config
from src.dependency_graph.registry import RegistryError, direct_dependencies


def main() -> int:
    """Показывает прямые зависимости пакета из npm-реестра."""
    parser = argparse.ArgumentParser(description="Граф зависимостей npm")
    parser.add_argument("--config", default="config.yaml",
                        help="путь к YAML-конфигурации")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if config.test_mode:
            raise RegistryError("тестовый репозиторий доступен с этапа 3")
        dependencies = direct_dependencies(config.package_name,
                                           config.repository)
    except (ConfigError, RegistryError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    print(f"Прямые зависимости {config.package_name}:")
    for name in sorted(dependencies):
        print(f"{name}: {dependencies[name]}")
    if not dependencies:
        print("(нет)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
