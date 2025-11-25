import re

def normalize_text(text: str) -> str:
    t = text.replace("\r\n", "\n")
    t = re.sub(r"[ \t]+$", "", t, flags=re.MULTILINE)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()
