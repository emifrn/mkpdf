# mkpdf

**mkpdf** is a command-line tool to merge PDFs and images into a single PDF
file, automatically generating a structured outline (bookmarks) based on
folder layout.

It’s ideal for organizing scanned documents, personal notes, service records, 
receipts, or photo albums — all without manually editing PDFs.

---

## Features

- Merges PDFs and images recursively from folders
- Builds navigable PDF outlines based on folder structure
- Honors `.order`, `.title`, `.label`, and `.ignore` dot-files
- Converts images (JPEG, PNG, etc.) to PDF pages with proper DPI and size
- Supports A4 and US Letter page sizes

---

## Installation

Requires **Python 3.10+**.

Clone the repository and install in editable mode:

```bash
git clone https://github.com/yourusername/mkpdf.git
cd mkpdf
pip install -e .
```

---

## Example Usage

```bash
# Merge everything under 'my_docs' into 'output.pdf'
mkpdf my_docs/ -o output.pdf

# Merge only folders matching '2023' but excluding 'temp'
mkpdf records/ -i '2023' -x 'temp' -o archive.pdf

# Convert all images with A4 page size at 300 DPI
mkpdf photos/ --page a4 -q medium -o album.pdf

# Use pretty labels (replace underscores, capitalize, etc.)
mkpdf invoices/ -p -o final.pdf

# Dry run: see what would be merged without creating output
mkpdf reports/ --dry-run
```

---

## Pretty Labels

If you use `-p`, mkpdf will automatically:

- Capitalize labels
- Replace underscores with spaces
- Use clean folder/file names even if `.label` or `.title` is not present

This is useful when your files have names like `bank_statement_2023.pdf`, which
would be rendered as **"Bank statement 2023"** in the PDF outline.

---

## Dotfile Controls

- `.order` — Custom file/folder order (one name per line)
- `.title` — Override folder name for outline (plain text)
- `.label` — Assign labels to files (`filename.pdf = Custom Label`)
- `.ignore` — Skip a folder or file entirely
- `.dpi` — Override DPI for all images in this folder

---

## Dependencies

- [`pypdf`](https://pypi.org/project/pypdf/)
- [`Pillow`](https://pypi.org/project/Pillow/)
- [`rich`](https://pypi.org/project/rich/)

Install via pip:

```bash
pip install pypdf Pillow rich
```

---

## License

This project is licensed under the [MIT License](LICENSE).
