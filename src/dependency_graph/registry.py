"""Получение прямых зависимостей из HTTP-реестра npm."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


REQUEST_TIMEOUT = 10


class RegistryError(Exception):
    """Ошибка запроса или чтения ответа реестра npm."""


def direct_dependencies(package_name: str, repository: str) -> dict[str, str]:
    """Возвращает зависимости версии latest заданного npm-пакета."""
    package_path = quote(package_name, safe="@")
    url = f"{repository.rstrip('/')}/{package_path}/latest"
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            manifest = json.load(response)
    except HTTPError as error:
        raise RegistryError(
            f"пакет {package_name}: HTTP {error.code} ({url})"
        ) from error
    except (URLError, TimeoutError, OSError) as error:
        message = f"не удалось обратиться к {url}: {error}"
        raise RegistryError(message) from error
    except (ValueError, UnicodeError) as error:
        raise RegistryError(f"неверный JSON от {url}: {error}") from error
    if not isinstance(manifest, dict):
        raise RegistryError("ответ реестра должен содержать JSON-объект")
    dependencies = manifest.get("dependencies", {})
    if not isinstance(dependencies, dict):
        raise RegistryError("поле dependencies должно быть JSON-объектом")
    if any(
        not isinstance(name, str) or not isinstance(version, str)
        for name, version in dependencies.items()
    ):
        raise RegistryError("поле dependencies содержит неверные значения")
    return dependencies
