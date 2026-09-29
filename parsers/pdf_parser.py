import os
import pypdf

def parse_pdf(file_path, rel_path):
    """
    Parses PDF documents.
    Safely handles:
    - Encrypted / password-protected files (skips without raising)
    - Multi-page documents
    - Corrupt or invalid stream errors
    """
    chunks = []
    try:
        reader = pypdf.PdfReader(file_path)
        if reader.is_encrypted:
            # Trap 4: Encrypted file that cannot be opened without password
            return []
        
        for idx, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text() or ""
                page_text = page_text.strip()
                if page_text:
                    chunks.append({
                        "file_path": rel_path,
                        "source_type": "pdf",
                        "page": idx + 1,
                        "text": page_text
                    })
            except Exception:
                continue
    except (pypdf.errors.FileEncryptedError, pypdf.errors.PdfReadError):
        return []
    except Exception:
        return []
    
    return chunks
