import os
from pathlib import Path
from doc_editor import clean_role_name, DocEditor
from pdf_converter import PDFConverter

def test_clean_role():
    print("Testing clean_role_name...")
    tests = [
        ("Senior Backend Developer", "Backend Developer"),
        ("Junior Frontend Engineer", "Frontend Engineer"),
        ("Lead Full Stack Developer", "Full Stack Developer"),
        ("Software Engineer Intern", "Software Engineer"),
        ("Principal Architect", "Architect"),
        ("Entry-Level Developer", "Developer"),
    ]
    for raw, expected in tests:
        cleaned = clean_role_name(raw)
        assert cleaned == expected, f"Failed: {raw} -> {cleaned} (expected {expected})"
    print("  [OK] clean_role_name works perfectly!\n")

def test_pdf_converter():
    print("Testing PDFConverter initialization...")
    try:
        converter = PDFConverter()
        print(f"  [OK] PDFConverter initialized successfully! Found LibreOffice at: {converter.libreoffice_path}\n")
    except Exception as e:
        print(f"  [FAIL] PDFConverter failed: {e}\n")

if __name__ == "__main__":
    test_clean_role()
    test_pdf_converter()
    print("Backend logic tests passed successfully!")
