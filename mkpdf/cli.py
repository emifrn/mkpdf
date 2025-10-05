#!/usr/bin/env python3

"""
mkpdf: Merge PDF and image files into a single PDF with outline structure based on folders.

Folder conventions (dotfiles):
  .title   → Custom name for this folder in the PDF outline (plain text)
  .ignore  → If present, skip this folder or file and all its content
  .order   → List of filenames or subfolders in custom order (one per line)
  .label   → Optional label overrides for leaf files (key = value format)
  .dpi     → Optional DPI override for this folder's images (e.g., 150 or 300)

Examples:
  mkpdf my_docs/ -o my_docs.pdf
  mkpdf services/ -o service.pdf -x 'temp' -i 'cars'

"""

import sys
import argparse
from pathlib import Path
from walker import select_paths, build_tree_description
from merger import merge, clear_temp_files, add_metadata
from rich.console import Console


VERSION = "1.0.0"


def main():
    parser = argparse.ArgumentParser(description="Merge folders of PDFs and images into a single structured PDF.")
    parser.add_argument("root", nargs="?", type=Path, help="Root folder to process")
    parser.add_argument("-o", "--output", metavar="FILE", type=Path, default="output.pdf", help="Output PDF file, default: output.pdf")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be merged without creating output")
    parser.add_argument("--log", metavar="FILE", type=Path, help="Save output messages to this log file")    
    parser.add_argument("--version", action="store_true", help="Show version and exit")

    filter_group = parser.add_argument_group("Input folder and files filter options")
    filter_group.add_argument("-i", "--include", metavar="REXP", action="append", help="Include paths matching a regular expression (can repeat)")
    filter_group.add_argument("-x", "--exclude", metavar="REXP", action="append", help="Exclude paths matching a regular expression (can repeat)")

    format_group = parser.add_argument_group("PDF page and outline format options")
    format_group.add_argument("-p", action="store_true", default=False, help="Replace underscores and capitalize labels")
    format_group.add_argument("-q", choices=["low", "medium", "high"], help="Select image quality")
    format_group.add_argument("--dpi", type=int, help="Select DPI resolution")
    format_group.add_argument("--page", choices=["letter", "a4", "none"], default="letter", help="Set image page size: 'letter' or 'a4' (default 'letter')")

    meta_group = parser.add_argument_group("PDF metadata options")
    meta_group.add_argument("-t", "--title", metavar="STR", help="Set the PDF title")
    meta_group.add_argument("-a", "--author", metavar="STR", help="Set the PDF author")
    meta_group.add_argument("-s", "--subject", metavar="STR", help="Set the PDF subject")
    meta_group.add_argument("-k", "--keywords", metavar="STR", help="Set the PDF keywords (comma-separated)")

    args = parser.parse_args()

    if args.log:
        log_file = open(args.log, "w", encoding="utf-8")
        console = Console(file=log_file, force_terminal=False)
    else:
        console = Console()

    if args.version:
        console.print(f"[dim]mkpdf v{VERSION}[/]")
        return

    if args.root is None:
        parser.error("the following arguments are required: root")
        return

    if args.dry_run:
        console.print("[cyan][i] Dry run mode. The following files/folders would be processed:[/]")
        files = select_paths(args.root, includes=args.include, excludes=args.exclude)
        for f in files:
            console.print(f"[dim]  - {f}[/]")
        return

    tree = build_tree_description(select_paths(args.root, includes=args.include, excludes=args.exclude))

    dpi = args.dpi or {"low": 150, "medium": 300, "high": 600}.get(args.q, 150)
    merger, tempfiles = merge(tree, console=console, pretty_labels=args.p, page_size=args.page, dpi=dpi)
    add_metadata(merger, 
                 title=args.title or args.root.name, 
                 author=args.author, 
                 subject=args.subject, 
                 keywords=args.keywords,
                 creator=f"mkpdf {VERSION}")

    output_path = args.output
    if output_path.suffix.lower() != ".pdf":
        output_path = output_path.with_suffix(".pdf")

    with open(output_path, "wb") as f:
        merger.write(f)

    clear_temp_files(tempfiles, console=console)
    console.print(f"[green][✓] PDF successfully written to: {output_path}[/]")


if __name__ == "__main__":
    main()
