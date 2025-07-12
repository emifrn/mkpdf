"""
merger.py - Combines PDF and image files into a single structured PDF.

Responsibilities:
  - Convert images to PDF pages with DPI and page size options
  - Merge all pages into one file while tracking page positions
  - Generate hierarchical PDF outlines based on folder structure
  - Inject optional PDF metadata (title, author, keywords, etc.)
  - Clean up temporary image-to-PDF conversions after merge
"""

import sys
import tempfile
from PIL import Image
from typing import Any
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from rich.progress import track
from rich.console import Console


def merge(tree: list[dict[str, Any]],
          console: Console,
          pretty_labels: bool = False,
          page_size: str = None,
          dpi: int = 150) -> tuple[PdfWriter, list[Path]]:

    _update_files_page_count(tree, dpi, console)
    _assign_folder_page_indices(tree)

    writer = PdfWriter()
    tempfiles: list[Path] = []
    parents: dict[Path, Any] = {}
    folders = {x["path"]: x for x in tree if x["type"] == "folder"}

    page_index = 0

    for item in track(tree, description="Merging PDFs"):
        num_pages = 0

        tmp = _insert_into_pdf(writer, item, page_size, dpi, console)
        if tmp is not None:
            tempfiles.append(tmp)

        num_pages = item.get("pages", 0)
        item["page"] = page_index
        page_index += num_pages

        if item["type"] == "img":
            if folders[item["path"].parent].get("only_images"):
                continue

        outline = _add_outline(writer, item, parents.get(item["path"].parent), pretty_labels, console)
        if item["type"] == "folder":
            parents[item["path"]] = outline

    return writer, tempfiles


def add_metadata(writer, title, author, subject, keywords, creator):
    keys = ["/Title", "/Author", "/Subject", "/Keywords", "/Creator"]
    vals = [title, author, subject, keywords, creator]
    metadata = {k: v for k,v in zip(keys,vals) if v is not None}
    writer.add_metadata(metadata)


def clear_temp_files(tempfiles: list[Path], console: Console):
    for tmp in tempfiles:
        try:
            tmp.unlink()
        except Exception as e:
            console.print(f"[yellow][!] Warning: could not delete temp file {tmp}: {e}[/]", file=sys.stderr)


def _update_files_page_count(tree: list[dict[str, Any]], dpi: int, console: Console) -> None:
    for item in tree:
        if item["type"] not in {"pdf", "img"}:
            continue

        try:
            if item["type"] == "pdf":
                reader = PdfReader(item["path"])
                item["pages"] = len(reader.pages)
            elif item["type"] == "img":
                item["pages"] = 1

        except Exception as e:
            console.print(f"[yellow][!] Skipping unreadable file {item['path']}: {e}[/]", file=sys.stderr)
            item["pages"] = 0


def _assign_folder_page_indices(tree: list[dict[str, Any]]) -> None:
    last_valid_page = 0
    for item in reversed(tree):
        if "page" in item and item.get("pages", 0) > 0:
            last_valid_page = item["page"]
        elif item["type"] == "folder":
            item["page"] = last_valid_page


def _insert_into_pdf(writer: PdfWriter, item: dict[str, Any], page: str, dpi: int, console: Console) -> Path | None:
    if item["type"] == "pdf":
        try:
            reader = PdfReader(item["path"])
            for page_obj in reader.pages:
                writer.add_page(page_obj)
        except Exception as e:
            console.print(f"[red][!] Failed to add PDF {item['path']}: {e}[/]", file=sys.stderr)

    elif item["type"] == "img":
        try:
            tmp = _convert_img_to_pdf(str(item["path"]), page, dpi)
            reader = PdfReader(str(tmp))
            for page_obj in reader.pages:
                writer.add_page(page_obj)
            return tmp
        except Exception as e:
            console.print(f"[red][!] Failed to convert image {item['path']} to PDF: {e}[/]", file=sys.stderr)


def _add_outline(writer: PdfWriter, item: dict[str, Any], parent: Any, pretty_labels: bool, console: Console) -> Any:
    if "page" not in item or item["page"] is None:
        return None

    if item["type"] != "folder" and item.get("pages", 0) == 0:
        return None

    label = item.get("label", item["path"].stem)
    if pretty_labels and "label" not in item:
        label = _prettify_label(label)

    try:
        return writer.add_outline_item(
            title=label,
            page_number=item["page"],
            parent=parent)
    except Exception as e:
        console.print(f"[yellow][!] Failed to add outline for {item['path']}: {e}[/]", file=sys.stderr)
        return None


def _convert_img_to_pdf(file: str, page: str, dpi: int) -> Path:
    with Image.open(file) as img:
        rgb = img.convert("RGB")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.close()

        if page is not None:
            canvas = _resize_and_center(rgb, _get_canvas_size(page, dpi))
            canvas.save(tmp.name, format="PDF", dpi=(dpi, dpi))
        else:
            rgb.save(tmp.name, format="PDF", dpi=(dpi, dpi))

        return Path(tmp.name)


def _resize_and_center(image: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGB", target_size, "white")

    image.thumbnail(target_size, Image.Resampling.LANCZOS)

    offset_x = (target_size[0] - image.width) // 2
    offset_y = (target_size[1] - image.height) // 2
    canvas.paste(image, (offset_x, offset_y))

    return canvas


def _get_canvas_size(page: str, dpi: int) -> tuple[int, int] | None:
    if page == "letter":
        return int(8.5 * dpi), int(11 * dpi)
    elif page == "a4":
        return int(8.27 * dpi), int(11.69 * dpi)
    else:
        return None

def _prettify_label(label: str) -> str:
    return label.replace("_", " ").strip().capitalize()
