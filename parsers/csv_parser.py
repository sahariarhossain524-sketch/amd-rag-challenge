import csv

def parse_csv(file_path, rel_path):
    """
    Parses CSV tables (e.g., bug databases, ticketing systems).
    Formats each row with its column headers.
    """
    chunks = []
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc, errors='replace') as f:
                reader = csv.reader(f)
                rows = [r for r in reader if any(field.strip() for field in r)]
            
            if not rows:
                return []

            headers = [h.strip() for h in rows[0]]
            formatted_lines = [f"Columns: {', '.join(headers)}"]
            
            for row in rows[1:]:
                row_items = []
                for h, val in zip(headers, row):
                    if val.strip():
                        row_items.append(f"{h}: {val.strip()}")
                if row_items:
                    formatted_lines.append(" | ".join(row_items))
            
            content = "\n".join(formatted_lines).strip()
            if content:
                chunks.append({
                    "file_path": rel_path,
                    "source_type": "csv",
                    "text": content
                })
            return chunks
        except Exception:
            continue

    return []
