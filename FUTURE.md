# FUTURE.md

This file collects ideas for future development of `mkpdf`. These features are
not part of version 1.0.0, but reflect possible enhancements to support more
flexibility, polish, and workflow integration.

They are designed to align with the project's core philosophy: quiet, simple,
offline, and transparent CLI tools for structured PDF creation.

---

## Dot-file Enhancements

### `.rotation`
- Specify image rotation per file or per folder.
- Useful for scanned notes with inconsistent orientation.
- Example `.rotation` content:
  ```
  page1.jpg = 90
  page2.jpg = 270
  ```

### `.margin`, `.scale`, `.align`
- `.margin` — control white border padding
- `.scale` — auto-resize larger images to fit
- `.align` — left, center, right alignment on the page

### `.meta`
- Use a single structured file (e.g. YAML) to replace multiple dot-files:
  ```yaml
  title: My Custom Title
  dpi: 300
  label_map:
    scan1.pdf: Receipt Jan
    scan2.pdf: Receipt Feb
  ```

---

## CLI/Behavioral Enhancements

### `--dry-run` TOC preview
- Print a tree of what will be merged, with page counts and labels.

### `--split-by-folder`
- Generate one output PDF per top-level folder.

### `.txt` as intro/cover
- Treat a `.txt` file in a folder as a rendered first page.

---

## Experimental / Long-Term Ideas

- `mkpdf.yaml` master config for root-level overrides
- Page ranges in `.order` or filenames (e.g. `report.pdf:1-3`)
- JSON export of metadata or structure alongside final PDF
- Optional OCR-based `.label.auto` support
- Outline export to Markdown or HTML
