import os

def parse_text(file_path, rel_path, file_ext):
    """
    Parses plain text, production logs (.log), and source code (.py).
    Robust against encoding errors and permission exceptions.
    """
    chunks = []
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc, errors='replace') as f:
                content = f.read().strip()
            
            if not content:
                return []
            
            chunks.append({
                "file_path": rel_path,
                "source_type": file_ext.lstrip('.'),
                "text": content
            })
            return chunks
        except (PermissionError, OSError):
            # Trap 3: File with no permission (chmod 000)
            return []
        except Exception:
            continue
            
    return []
