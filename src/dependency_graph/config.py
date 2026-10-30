"""Загрузка и проверка YAML-конфигурации приложения."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

import yaml


FIELDS = (
    "package_name",
    "repository",
    "test_mode",
    "output_file",
    "ascii_tree",
)
NPM_NAME = re.compile(
    r"(?:@[a-z0-9][a-z0-9._~-]*/)?[a-z0-9][a-z0-9._~-]*"
)
TEST_NAME = re.compile(r"[A-Z]+")


class ConfigError(ValueError):
    """Ошибка чтения или проверки пользовательской конфигурации."""


@dataclass(frozen=True)
class Config:
    """Проверенные настройки текущего и следующих этапов."""

    package_name: str
    repository: str
    test_mode: bool
    output_file: str
    ascii_tree: bool


def _boolean(value: object, name: str) -> bool:
    """Принимает только логическое значение YAML для переключателя."""
    if not isinstance(value, bool):
        raise ConfigError(f"{name}: ожидается true или false")
    return value


def _package_name(value: object, test_mode: bool) -> str:
    """Проверяет имя npm-пакета или тестовое имя из заглавных букв."""
    pattern = TEST_NAME if test_mode else NPM_NAME
    if not isinstance(value, str) or not pattern.fullmatch(value):
        kind = "заглавные латинские буквы" if test_mode else "имя npm"
        raise ConfigError(f"package_name: ожидается корректное {kind}")
    return value


def _test_repository(value: str, base: Path) -> str:
    """Находит существующий тестовый файл относительно YAML."""
    path = Path(value)
    path = path if path.is_absolute() else base / path
    if not path.is_file():
        raise ConfigError(f"repository: файл не найден: {path}")
    return str(path.resolve())


def _registry_url(value: str) -> str:
    """Проверяет абсолютный HTTP(S)-адрес реестра npm."""
    try:
        url = urlsplit(value)
        valid = url.scheme in {"http", "https"} and bool(url.hostname)
        if valid:
            _ = url.port
    except ValueError:
        valid = False
    if not valid or url.query or url.fragment:
        raise ConfigError("repository: ожидается URL с HTTP или HTTPS")
    return value


def _repository(value: object, test_mode: bool, base: Path) -> str:
    """Выбирает проверку адреса реестра или тестового файла."""
    if not isinstance(value, str) or not value.strip():
        raise ConfigError("repository: ожидается непустой URL или путь")
    if test_mode:
        return _test_repository(value, base)
    return _registry_url(value)


def _output_file(value: object) -> str:
    """Проверяет имя PNG-файла для последнего этапа."""
    if not isinstance(value, str):
        raise ConfigError("output_file: ожидается имя PNG-файла")
    path = Path(value)
    if path.name != value or not path.stem or path.suffix.lower() != ".png":
        raise ConfigError("output_file: ожидается имя PNG-файла")
    return value


def load_config(config_path: Path) -> Config:
    """Читает YAML и сообщает об ошибках каждого параметра."""
    path = Path(config_path)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        message = f"config: не удалось прочитать {path}: {error}"
        raise ConfigError(message) from error
    if not isinstance(data, dict):
        raise ConfigError("config: ожидается YAML-словарь")
    if any(not isinstance(key, str) for key in data):
        raise ConfigError("config: имена настроек должны быть строками")
    for name in FIELDS:
        if name not in data:
            raise ConfigError(f"{name}: параметр отсутствует")
    unknown = data.keys() - FIELDS
    if unknown:
        raise ConfigError(f"config: неизвестный параметр: {sorted(unknown)[0]}")
    test_mode = _boolean(data["test_mode"], "test_mode")
    return Config(
        package_name=_package_name(data["package_name"], test_mode),
        repository=_repository(data["repository"], test_mode, path.parent),
        test_mode=test_mode,
        output_file=_output_file(data["output_file"]),
        ascii_tree=_boolean(data["ascii_tree"], "ascii_tree"),
    )
