"""
walker.py - Scans a directory structure and builds a file list based on filtering
rules and metadata control files like .ignore, .order, .label, etc.
"""

import re
from re import Pattern
from typing import Any
from pathlib import Path
from collections.abc import Iterator, Sequence


def select_paths(root: Path, 
           includes: Sequence[Pattern] | None = None, 
           excludes: Sequence[Pattern] | None = None) -> Iterator[Path]:

    selection = []
    root = Path(root).resolve()

    def walk(current_path, rel_parts=[]):
        if _should_ignore(current_path):
            return

        rel_path = Path(*rel_parts)
        if not _match_filters(rel_path, includes, excludes):
            return

        order_file = current_path / ".order"
        children = sorted(current_path.iterdir(), key=lambda p: p.name.lower())

        if order_file.exists():
            preferred = _load_dotfile_lines(order_file)
            preferred_map = {name: i for i, name in enumerate(preferred)}
            children.sort(key=lambda p: preferred_map.get(p.name, len(preferred_map) + hash(p.name.lower())))

        selection.append(current_path)

        for child in children:
            if not _is_valid(child):
                continue

            if child.name.startswith(".") or child.name in (".order", ".label", ".title", ".dpi"):
                continue

            if child.is_dir():
                walk(child, rel_parts + [child.name])
            elif _match_filters(rel_path / child.name, includes, excludes):
                selection.append(child)

    walk(root)

    return selection


def build_tree_description(files: Iterator[Path]) -> list[dict[str, Any]]:
    folders = {}
    for path in files:
        if path.is_dir():
            folders[path] = _describe_folder(path)

    tree = []
    for path in files:
        if path.is_dir():
            tree.append(folders[path])
        elif desc := _describe_file(path, folders[path.parent]):
            tree.append(desc)

    return tree


def _should_ignore(path: Path) -> bool:
    return (path / ".ignore").exists() or path.name == ".ignore"


def _match_filters(path: Path, includes: list[Pattern] | None, excludes: list[Pattern] | None) -> bool:
    as_str = str(path)
    if includes and not any(re.search(pattern, as_str) for pattern in includes):
        return False
    if excludes and any(re.search(pattern, as_str) for pattern in excludes):
        return False
    return True


def _load_dotfile_lines(path: Path) -> list[str]:
    try:
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except Exception:
        return []


def _is_img(path: Path) -> bool:
    if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"}:
        return True
    else:
        return False


def _is_pdf(path: Path) -> bool:
    if path.suffix.lower() == ".pdf":
        return True
    else:
        return False


def _is_valid(path: Path) -> bool:
    return path.is_dir() or _is_pdf(path) or _is_img(path)


def _describe_folder(path: Path) -> dict[str, Any]:
    desc = { "type": "folder", 
             "path": path, 
             "title": _resolve_title(path),
             "labels": _resolve_labels(path) }

    children = list(path.iterdir())
    has_pdf = any(_is_pdf(child) for child in children if child.is_file())
    has_img = any(_is_img(child) for child in children if child.is_file())

    if has_img and not has_pdf:
        desc["only_images"] = True

    return desc


def _describe_file(path: Path, folder: dict[str, Any]) -> dict[str, Any] | None:
    desc = { "path": path }

    if label := folder["labels"].get(path.name):
        desc["label"] = label

    if _is_pdf(path):
        desc["type"] = "pdf"
    elif _is_img(path):
        desc["type"] = "img"
    else:
        return None

    return desc


def _resolve_title(path: Path) -> str:
    dot_title = path / ".title"
    if dot_title.exists():
        try:
            return dot_title.read_text(encoding="utf-8").strip()
        except Exception:
            pass

    return path.name


def _resolve_labels(folder: Path) -> dict[str, str]:
    dot_label = folder / ".label"
    labels = {}
    if dot_label.exists():
        try:
            for line in dot_label.read_text(encoding="utf-8").splitlines():
                if "=" in line:
                    key, value = line.split("=", 1)
                    labels[key.strip()] = value.strip()
        except Exception:
            pass

    return labels
