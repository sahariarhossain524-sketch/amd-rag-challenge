import os
from .pdf_parser import parse_pdf
from .docx_parser import parse_docx
from .xlsx_parser import parse_xlsx
from .csv_parser import parse_csv
from .text_parser import parse_text
from .image_parser import parse_image

SUPPORTED_EXTENSIONS = {
    '.pdf': 'pdf',
    '.docx': 'docx',
    '.xlsx': 'xlsx',
    '.csv': 'csv',
    '.txt': 'txt',
    '.log': 'log',
    '.py': 'py',
    '.png': 'image',
    '.jpg': 'image',
    '.jpeg': 'image',
    '.tiff': 'image'
}

def parse_file(full_path, rel_path, device='cpu'):
    """
    Dispatcher for parsing a single file safely.
    Robustly handles all 4 organizer traps:
    1. Unknown filetype (e.g. .dat, .bin) -> skipped silently.
    2. Unreadable permission (chmod 000) -> caught and skipped.
    3. Encrypted files -> caught and skipped.
    4. Corrupt files -> caught and skipped.
    """
    _, ext = os.path.splitext(full_path)
    ext = ext.lower()

    # Trap 2: Unknown file types
    if ext not in SUPPORTED_EXTENSIONS:
        return []

    # Trap 3: Permission errors (chmod 000)
    try:
        if not os.access(full_path, os.R_OK):
            return []
    except Exception:
        return []

    try:
        doc_type = SUPPORTED_EXTENSIONS[ext]
        if doc_type == 'pdf':
            return parse_pdf(full_path, rel_path)
        elif doc_type == 'docx':
            return parse_docx(full_path, rel_path)
        elif doc_type == 'xlsx':
            return parse_xlsx(full_path, rel_path)
        elif doc_type == 'csv':
            return parse_csv(full_path, rel_path)
        elif doc_type in ('txt', 'log', 'py'):
            return parse_text(full_path, rel_path, ext)
        elif doc_type == 'image':
            return parse_image(full_path, rel_path, device=device)
    except (PermissionError, OSError):
        return []
    except Exception:
        return []

    return []
