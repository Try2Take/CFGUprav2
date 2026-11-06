"""Рекурсивный обход графа зависимостей в ширину."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable, Iterable


TEST_NAME = re.compile(r"[A-Z]+")


class GraphError(Exception):
    """Ошибка описания тестового графа зависимостей."""


def _visit_level(
    frontier: list[str], visited: set[str], graph: dict[str, list[str]],
    dependencies: Callable[[str], Iterable[str]],
) -> None:
    """Обрабатывает один уровень BFS и рекурсивно переходит к следующему."""
    if not frontier:
        return
    next_frontier = []
    for package in frontier:
        neighbors = sorted(set(dependencies(package)))
        graph[package] = neighbors
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                next_frontier.append(neighbor)
    _visit_level(next_frontier, visited, graph, dependencies)


def build_graph(
    package_name: str, dependencies: Callable[[str], Iterable[str]],
) -> dict[str, list[str]]:
    """Строит транзитивный граф рекурсивным BFS без повторных посещений."""
    graph = {}
    _visit_level([package_name], {package_name}, graph, dependencies)
    return graph


def _validate_test_entry(package: object, neighbors: object) -> None:
    """Проверяет имя пакета и список его прямых зависимостей."""
    if not isinstance(package, str) or not TEST_NAME.fullmatch(package):
        raise GraphError(f"недопустимое имя пакета: {package}")
    if not isinstance(neighbors, list):
        raise GraphError(f"{package}: ожидается список зависимостей")
    if any(
        not isinstance(name, str) or not TEST_NAME.fullmatch(name)
        for name in neighbors
    ):
        raise GraphError(f"{package}: недопустимое имя зависимости")


def load_test_repository(path: str | Path) -> dict[str, list[str]]:
    """Читает JSON-граф с именами пакетов из заглавных латинских букв."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        message = f"не удалось прочитать тестовый граф: {error}"
        raise GraphError(message) from error
    if not isinstance(data, dict):
        raise GraphError("тестовый граф должен быть JSON-объектом")
    for package, neighbors in data.items():
        _validate_test_entry(package, neighbors)
    missing = {name for names in data.values() for name in names} - data.keys()
    if missing:
        raise GraphError(f"пакет отсутствует в тестовом графе: {min(missing)}")
    return data
