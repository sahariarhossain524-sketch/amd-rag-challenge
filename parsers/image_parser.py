import os
import cv2
import numpy as np
from PIL import Image

_READER = None

def get_ocr_reader(device='cpu'):
    global _READER
    if _READER is None:
        try:
            import easyocr
            gpu_enabled = (device == 'cuda')
            
            # Prioritize local or system baked models
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            local_models = os.path.join(base_dir, "models")
            if os.path.exists(local_models) and os.path.exists(os.path.join(local_models, "craft_mlt_25k.pth")):
                model_dir = local_models
                download_needed = False
            elif os.path.exists("/models") and os.path.exists("/models/craft_mlt_25k.pth"):
                model_dir = "/models"
                download_needed = False
            else:
                model_dir = os.path.expanduser("~/.EasyOCR/model")
                download_needed = True

            _READER = easyocr.Reader(
                ['en'],
                gpu=gpu_enabled,
                model_storage_directory=model_dir,
                download_enabled=download_needed,
                verbose=False
            )
        except Exception:
            _READER = None
    return _READER

def parse_image(file_path, rel_path, device='cpu'):
    """
    Parses image diagrams, pinouts, and labels using OCR.
    Extracts text tokens and positional groupings.
    Falls back gracefully to embedded metadata or sidecars if OCR engine is unavailable in dev environment.
    """
    chunks = []
    try:
        reader = get_ocr_reader(device=device)
        if reader is not None:
            # Production path inside AMD ROCm container
            img = cv2.imread(file_path)
            if img is None:
                pil_img = Image.open(file_path).convert('RGB')
                img = np.array(pil_img)[:, :, ::-1]

            # Auto-upscale small images for accurate pinout/label text detection
            h, w = img.shape[:2]
            if h < 600 or w < 800:
                scale = max(2.0, min(1200.0 / max(h, 1), 1600.0 / max(w, 1)))
                scale = min(scale, 3.5)
                img = cv2.resize(img, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

            results = reader.readtext(img, detail=1)
            if results:
                # Sort reading order: top-to-bottom, left-to-right
                def get_sort_key(item):
                    bbox = item[0]
                    y_mid = (bbox[0][1] + bbox[2][1]) / 2.0
                    x_mid = (bbox[0][0] + bbox[2][0]) / 2.0
                    band = int(y_mid // 25)
                    return (band, x_mid)

                sorted_results = sorted(results, key=get_sort_key)
                lines = [item[1].strip() for item in sorted_results if item[1].strip()]
                full_text = "\n".join(lines).strip()
                if full_text:
                    chunks.append({
                        "file_path": rel_path,
                        "source_type": "image",
                        "text": full_text,
                        "ocr_tokens": lines
                    })
                    return chunks

        # Fallback path for host/dev environment when PyTorch/EasyOCR is not installed
        pil_img = Image.open(file_path)
        meta_text = []
        if hasattr(pil_img, "info"):
            for k, v in pil_img.info.items():
                if isinstance(v, (bytes, bytearray)):
                    v = v.decode('utf-8', errors='ignore')
                if isinstance(v, str) and len(v) > 2:
                    meta_text.append(v)
        
        # Check sidecar for dev verification
        sidecar = file_path + ".txt"
        if os.path.exists(sidecar):
            with open(sidecar, "r", encoding="utf-8") as sf:
                meta_text.append(sf.read())

        combined = "\n".join(meta_text).strip()
        if combined:
            chunks.append({
                "file_path": rel_path,
                "source_type": "image",
                "text": combined,
                "ocr_tokens": combined.splitlines()
            })
    except Exception:
        return []

    return chunks
