import re

def read_cv_text(path: str) -> str:
    # Very basic text reader. Extend with PDF/DOCX handling if you like.
    # (If you want real PDF/DOCX extraction, add pypdf/pdfplumber/python-docx to requirements)
    try:
        with open(path, "rb") as f:
            b = f.read()
        # naive decode
        try:
            return b.decode("utf-8", errors="ignore")
        except:
            return b.decode("latin-1", errors="ignore")
    except Exception:
        return ""
