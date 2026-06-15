"""
pdf_converter.py
Convert DOCX files to PDF using LibreOffice headless mode.

Output filenames:
  Resume_<CompanyName>.pdf
  CV_<CompanyName>.pdf

Temporary DOCX files are deleted after successful conversion.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# Common installation paths to probe (Windows)
_COMMON_LO_PATHS = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    r"C:\Program Files\LibreOffice 7\program\soffice.exe",
    r"C:\Program Files\LibreOffice 6\program\soffice.exe",
    r"C:\Program Files\LibreOffice 5\program\soffice.exe",
]


def _find_libreoffice() -> str | None:
    """
    Auto-detect LibreOffice soffice.exe on Windows.

    Checks (in order):
      1. Common installation directories.
      2. Windows Registry (HKLM\\SOFTWARE\\LibreOffice).

    Returns:
        Full path to soffice.exe, or None if not found.
    """
    # 1. Common paths
    for path in _COMMON_LO_PATHS:
        if os.path.isfile(path):
            return path

    # 2. Windows Registry (guarded — won't crash on non-Windows or missing key)
    if sys.platform == "win32":
        try:
            import winreg  # noqa: PLC0415 (local import is intentional)

            for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                for sub in (
                    r"SOFTWARE\LibreOffice\UNO\InstallPath",
                    r"SOFTWARE\WOW6432Node\LibreOffice\UNO\InstallPath",
                ):
                    try:
                        with winreg.OpenKey(hive, sub) as key:
                            install_path, _ = winreg.QueryValueEx(key, None)
                            candidate = os.path.join(
                                install_path, "program", "soffice.exe"
                            )
                            if os.path.isfile(candidate):
                                return candidate
                    except OSError:
                        continue
        except ImportError:
            pass

    return None


class PDFConverter:
    """Converts DOCX → PDF using LibreOffice in headless mode."""

    def __init__(self, libreoffice_path: str | None = None):
        """
        Args:
            libreoffice_path: Full path to soffice.exe.
                              If None or empty, auto-detection is attempted.

        Raises:
            FileNotFoundError: LibreOffice executable cannot be located.
        """
        resolved = (libreoffice_path or "").strip() or _find_libreoffice()

        if not resolved:
            raise FileNotFoundError(
                "LibreOffice (soffice.exe) was not found on this system.\n"
                "Please install LibreOffice from https://www.libreoffice.org/\n"
                "or set the correct path in Settings."
            )

        if not os.path.isfile(resolved):
            raise FileNotFoundError(
                f"LibreOffice not found at the configured path:\n{resolved}\n"
                "Please update the path in Settings."
            )

        self.libreoffice_path = resolved

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _convert_single(self, docx_path: Path, out_dir: Path) -> Path:
        """
        Run LibreOffice headless conversion for one DOCX file.

        Returns:
            Path to the generated PDF file.

        Raises:
            subprocess.TimeoutExpired: Conversion took too long.
            Exception: LibreOffice returned a non-zero exit code or the PDF
                       was not produced.
        """
        out_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.libreoffice_path,
            "--headless",
            "--convert-to", "pdf",
            str(docx_path),
            "--outdir", str(out_dir),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            raise Exception(
                "LibreOffice conversion timed out (120 s). "
                "The DOCX file may be too large or LibreOffice is hung."
            )

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            raise Exception(
                f"LibreOffice conversion failed (exit code {result.returncode}).\n"
                + (f"Details: {stderr}" if stderr else "")
            )

        # LibreOffice names the PDF after the stem of the source file
        pdf_path = out_dir / (docx_path.stem + ".pdf")
        if not pdf_path.exists():
            raise Exception(
                f"LibreOffice reported success, but the PDF was not found at:\n{pdf_path}\n"
                "Check LibreOffice installation and try again."
            )

        return pdf_path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_pdfs(
        self,
        resume_docx: str,
        cv_docx: str,
        company_name: str,
        output_folder: str,
    ) -> tuple[Path, Path]:
        """
        Convert both DOCX files to PDFs and rename them by company name.

        After successful conversion the temporary DOCX files are deleted.

        Args:
            resume_docx:   Path to the edited resume DOCX (temporary).
            cv_docx:       Path to the edited CV DOCX (temporary).
            company_name:  Used as part of the output filename.
            output_folder: Destination directory for the final PDFs.

        Returns:
            (resume_pdf_path, cv_pdf_path) as Path objects.

        Raises:
            FileNotFoundError: Input DOCX file not found.
            Exception: Conversion or rename failure.
        """
        resume_docx_path = Path(resume_docx)
        cv_docx_path = Path(cv_docx)
        out_dir = Path(output_folder)

        if not resume_docx_path.exists():
            raise FileNotFoundError(f"Resume DOCX not found: {resume_docx_path}")
        if not cv_docx_path.exists():
            raise FileNotFoundError(f"CV DOCX not found: {cv_docx_path}")

        out_dir.mkdir(parents=True, exist_ok=True)

        # ---- Clear previous files in output directory ----
        for item in out_dir.iterdir():
            if item.is_file():
                try:
                    item.unlink()
                except OSError:
                    pass

        # ---- Convert ----
        resume_pdf_tmp = self._convert_single(resume_docx_path, out_dir)
        cv_pdf_tmp = self._convert_single(cv_docx_path, out_dir)

        # ---- Rename to final names ----
        resume_final = out_dir / f"Resume_{company_name}.pdf"
        cv_final = out_dir / f"CV_{company_name}.pdf"

        # Remove stale files with the same name if they exist
        if resume_final.exists():
            resume_final.unlink()
        if cv_final.exists():
            cv_final.unlink()

        shutil.move(str(resume_pdf_tmp), str(resume_final))
        shutil.move(str(cv_pdf_tmp), str(cv_final))

        # ---- Clean up temporary DOCX files ----
        try:
            resume_docx_path.unlink(missing_ok=True)
        except OSError:
            pass
        try:
            cv_docx_path.unlink(missing_ok=True)
        except OSError:
            pass

        return resume_final, cv_final
