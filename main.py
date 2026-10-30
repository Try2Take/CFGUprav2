"""Запуск инструмента построения графа зависимостей npm."""

from __future__ import annotations

import argparse
import sys

from src.dependency_graph.config import ConfigError, load_config


def main() -> int:
    """Показывает проверенные настройки первого этапа."""
    parser = argparse.ArgumentParser(description="Граф зависимостей npm")
    parser.add_argument("--config", default="config.yaml",
                        help="путь к YAML-конфигурации")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
    except ConfigError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    print(f"package_name={config.package_name}")
    print(f"repository={config.repository}")
    print(f"test_mode={str(config.test_mode).lower()}")
    print(f"output_file={config.output_file}")
    print(f"ascii_tree={str(config.ascii_tree).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
