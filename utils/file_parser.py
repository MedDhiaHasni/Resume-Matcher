"""
Extract text from uploaded files: PDF and TXT.
"""
import io
import pdfplumber


def extract_text(uploaded_file) -> str:
    """
    Extract plain text from a Streamlit UploadedFile.
    Supports PDF and TXT. Returns empty string on failure.
    """
    if uploaded_file is None:
        return ""

    name = uploaded_file.name.lower()

    try:
        if name.endswith(".pdf"):
            return _extract_pdf(uploaded_file)
        elif name.endswith(".txt"):
            return uploaded_file.read().decode("utf-8", errors="ignore")
        else:
            return ""
    except Exception as e:
        return f"[Error parsing file: {e}]"


def _extract_pdf(uploaded_file) -> str:
    """Extract text from all pages of a PDF."""
    text_parts = []
    pdf_bytes = uploaded_file.read()
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n\n".join(text_parts).strip()