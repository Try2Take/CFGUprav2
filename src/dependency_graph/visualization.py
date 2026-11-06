"""Текстовое и графическое представление зависимостей."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


class VisualizationError(Exception):
    """Ошибка запуска D2 или сохранения изображения."""


def to_d2(graph: dict[str, list[str]]) -> str:
    """Описывает все вершины и связи графа на языке D2."""
    lines = []
    for package, dependencies in graph.items():
        source = json.dumps(package, ensure_ascii=False)
        if not dependencies:
            lines.append(source)
        for dependency in dependencies:
            target = json.dumps(dependency, ensure_ascii=False)
            lines.append(f"{source} -> {target}")
    return "\n".join(lines) + "\n"


def ascii_tree(root: str, graph: dict[str, list[str]]) -> str:
    """Строит ASCII-дерево, помечая уже показанные пакеты."""
    lines = [root]
    visited = {root}

    def add_children(package: str, prefix: str) -> None:
        """Добавляет потомков пакета с отступом текущей ветви."""
        children = graph.get(package, [])
        for index, child in enumerate(children):
            last = index == len(children) - 1
            branch = "`-- " if last else "|-- "
            repeated = child in visited
            suffix = " (повтор)" if repeated else ""
            lines.append(f"{prefix}{branch}{child}{suffix}")
            if not repeated:
                visited.add(child)
                indent = "    " if last else "|   "
                add_children(child, prefix + indent)

    add_children(root, "")
    return "\n".join(lines) + "\n"


def render_png(
    description: str, output_path: Path, executable: str = "d2",
) -> None:
    """Передаёт описание D2 внешнему рендереру и сохраняет PNG."""
    try:
        result = subprocess.run(
            [executable, "-", str(output_path)], input=description,
            text=True, capture_output=True, check=False,
        )
    except FileNotFoundError as error:
        raise VisualizationError("D2 не найден: установите команду d2") \
            from error
    except OSError as error:
        raise VisualizationError(f"не удалось запустить D2: {error}") \
            from error
    if result.returncode:
        message = result.stderr.strip() or "неизвестная ошибка"
        raise VisualizationError(f"D2 не создал PNG: {message}")
