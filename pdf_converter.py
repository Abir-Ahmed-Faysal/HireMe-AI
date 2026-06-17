"""pdf_converter.py
Convert DOCX files to PDF using LibreOffice headless mode.

Output structure (timestamped subfolders for organization):
  output_folder/
  ├── TechCorp_Backend_Developer_2026-06-17_14-30-05-123/
  │   ├── Faysal_Ahmed_Resume_Backend_Developer.pdf
  │   └── Faysal_Ahmed's_CoverLetter_Backend_Developer.pdf
  └── Google_Software_Engineer_2026-06-17_14-30-35-456/
      ├── Faysal_Ahmed_Resume_Software_Engineer.pdf
      └── Faysal_Ahmed's_CoverLetter_Software_Engineer.pdf

Each generation creates a new timestamped folder (CompanyName_CleanedRole_YYYY-MM-DD_HH-MM-SS-mmm)
with milliseconds for guaranteed uniqueness. Level qualifiers (Senior/Junior/Intern) are removed
from role names in filenames and folder names. No files are deleted.

Temporary DOCX files are deleted after successful conversion.
"""

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
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
        role: str = "",
        applicant_name: str = "Applicant",
    ) -> tuple[Path, Path]:
        """
        Convert both DOCX files to PDFs with comprehensive validation.
        
        Validates:
        - Input files exist and are readable
        - Output folder exists and is writable
        - Company name is not empty
        
        Raises:
            FileNotFoundError: If inputs don't exist or outputs can't be written
            Exception: If conversion fails
        """
        # Validate inputs
        resume_path = Path(resume_docx)
        cv_path = Path(cv_docx)
        
        if not resume_path.exists():
            raise FileNotFoundError(f"Resume DOCX file not found: {resume_docx}")
        if not cv_path.exists():
            raise FileNotFoundError(f"CV DOCX file not found: {cv_docx}")
        
        if not resume_path.is_file() or not cv_path.is_file():
            raise FileNotFoundError("Resume or CV path is not a valid file")
        
        # Validate output folder
        out_folder = Path(output_folder)
        try:
            out_folder.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            raise Exception(
                f"Cannot create or access output folder:\n{output_folder}\n"
                f"Error: {e}"
            )
        
        # Validate company name
        if not company_name or not company_name.strip():
            raise ValueError("Company name cannot be empty")
        
        if len(company_name) > 100:
            raise ValueError("Company name is too long (max 100 characters)")
        """
        Convert both DOCX files to PDFs and rename them using the personal
        name + role convention. Each generation creates a timestamped subfolder
        with milliseconds to guarantee uniqueness even when multiple PDFs are
        generated within the same second:

            output_folder/
              ├── TechCorp_FullStackDeveloper_2026-06-17_14-30-05-123/
              │   ├── Faysal's_Ahmed_Resume_FullStackDeveloper.pdf
              │   └── Faysal_Ahmed's_CoverLetter_FullStackDeveloper.pdf
              └── Google_SoftwareEngineer_2026-06-17_14-30-35-456/
                  ├── Faysal's_Ahmed_Resume_SoftwareEngineer.pdf
                  └── Faysal_Ahmed's_CoverLetter_SoftwareEngineer.pdf

        After successful conversion the temporary DOCX files are deleted.

        Args:
            resume_docx:   Path to the edited resume DOCX (temporary).
            cv_docx:       Path to the edited CV DOCX (temporary).
            company_name:  Company name for folder organization.
            output_folder: Parent directory for generated timestamped subfolders.
            role:          The applied-for role (e.g. "Full Stack Developer").
            applicant_name: The name of the applicant to use in filenames.

        Returns:
            (resume_pdf_path, cv_pdf_path) as Path objects.

        Raises:
            FileNotFoundError: Input DOCX file not found.
            Exception: Conversion or rename failure.
        """
        resume_docx_path = Path(resume_docx)
        cv_docx_path = Path(cv_docx)
        base_out_dir = Path(output_folder)

        if not resume_docx_path.exists():
            raise FileNotFoundError(f"Resume DOCX not found: {resume_docx_path}")
        if not cv_docx_path.exists():
            raise FileNotFoundError(f"CV DOCX not found: {cv_docx_path}")

        base_out_dir.mkdir(parents=True, exist_ok=True)

        # ---- Build role slug for folder and filename ----
        # Use the role field; fall back to company_name if role is empty.
        raw_role = role.strip() if role.strip() else company_name
        # Replace spaces with underscores; strip characters illegal in filenames.
        role_slug = re.sub(r"[^\w\s-]", "", raw_role).strip()
        role_slug = re.sub(r"[\s]+", "_", role_slug)
        role_slug = role_slug or "Application"

        # Sanitize company name for folder
        clean_company = re.sub(r"[^\w\s-]", "", company_name.strip())
        clean_company = re.sub(r"[\s]+", "_", clean_company)
        clean_company = clean_company or "Company"

        # ---- Create timestamped subfolder ----
        # Format: CompanyName_RoleSlug_YYYY-MM-DD_HH-MM-SS-mmm (with milliseconds for uniqueness)
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S") + f"-{now.microsecond // 1000:03d}"
        subfolder_name = f"{clean_company}_{role_slug}_{timestamp}"
        out_dir = base_out_dir / subfolder_name

        out_dir.mkdir(parents=True, exist_ok=True)

        # ---- Convert ----
        resume_pdf_tmp = self._convert_single(resume_docx_path, out_dir)
        cv_pdf_tmp = self._convert_single(cv_docx_path, out_dir)

        # ---- Clean role (remove Junior/Senior/Intern etc.) for filenames ----
        from doc_editor import clean_role_name
        clean_role = clean_role_name(raw_role)
        # Replace spaces with underscores for filename
        clean_role_slug = re.sub(r"[^\w\s-]", "", clean_role).strip()
        clean_role_slug = re.sub(r"[\s]+", "_", clean_role_slug)
        clean_role_slug = clean_role_slug or "Application"
        
        # Clean applicant name for filename
        clean_applicant = re.sub(r"[^\w\s-]", "", applicant_name.strip())
        clean_applicant = re.sub(r"[\s]+", "_", clean_applicant)
        clean_applicant = clean_applicant or "Applicant"
        
        # ---- Rename to final names ----
        resume_final = out_dir / f"{clean_applicant}_Resume_{clean_role_slug}.pdf"
        cv_final     = out_dir / f"{clean_applicant}_CoverLetter_{clean_role_slug}.pdf"

        # Rename LibreOffice-generated PDFs to final names
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
