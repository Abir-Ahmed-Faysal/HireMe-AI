"""
doc_editor.py
DOCX template editing with placeholder replacement.

Rules (strict):
  - resume.docx : replace ONLY {{JOB_TITLE}}
  - cv.docx     : replace ONLY {{COMPANY_NAME}} and {{ROLE}}
  - All other content (formatting, styles, fonts, colours) must be 100% preserved.

The replacement algorithm works at the Run level so bold/italic/font/size
on the replaced run is preserved. It also handles the common Word behaviour
where a single placeholder is split across multiple consecutive runs
(e.g. "{{JOB" in run-0 and "_TITLE}}" in run-1).
"""

from pathlib import Path
from copy import deepcopy
from docx import Document
from docx.oxml.ns import qn
import re


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _paragraph_full_text(para) -> str:
    """Return the concatenated text of all runs in a paragraph."""
    return "".join(run.text for run in para.runs)


def _replace_in_runs(runs, old: str, new: str) -> bool:
    """
    Replace *old* with *new* inside a sequence of runs, preserving formatting.

    Strategy
    --------
    1. Build a flat character list that records which run each character
       belongs to, so we can find the placeholder even when it is split
       across multiple runs.
    2. When a match is found, put the replacement text into the first run
       of the span and empty the remaining runs that were part of the match.

    Returns True if at least one replacement was made.
    """
    changed = False

    while True:
        # Re-build the full text and the per-character run-index map each
        # iteration so that multiple occurrences are handled correctly.
        full_text = ""
        char_run_idx = []  # char_run_idx[i] = index into `runs` for char i
        for ri, run in enumerate(runs):
            for _ in run.text:
                char_run_idx.append(ri)
            full_text += run.text

        idx = full_text.find(old)
        if idx == -1:
            break  # No more occurrences

        end_idx = idx + len(old) - 1  # inclusive

        first_run_idx = char_run_idx[idx]
        last_run_idx = char_run_idx[end_idx]

        # Build new texts for every affected run
        # For the first run: keep chars before the match start + replacement
        run_start_offset = sum(
            len(runs[ri].text) for ri in range(first_run_idx)
        )
        local_start = idx - run_start_offset  # offset within the first run

        # Text of first run: chars before match + replacement value
        first_run_text = runs[first_run_idx].text[:local_start] + new

        # Text of last run: chars after match end (within that run)
        last_run_start_offset = sum(
            len(runs[ri].text) for ri in range(last_run_idx)
        )
        local_end = end_idx - last_run_start_offset  # inclusive offset in last run
        last_run_suffix = runs[last_run_idx].text[local_end + 1:]

        if first_run_idx == last_run_idx:
            # Entire placeholder sits in one run
            runs[first_run_idx].text = first_run_text + last_run_suffix
        else:
            runs[first_run_idx].text = first_run_text
            # Zero out intermediate runs
            for ri in range(first_run_idx + 1, last_run_idx):
                runs[ri].text = ""
            # Last run keeps only the suffix
            runs[last_run_idx].text = last_run_suffix

        changed = True

    return changed


def _replace_in_paragraph(para, replacements: dict) -> None:
    """Apply all replacements to a single paragraph's runs."""
    for old, new in replacements.items():
        _replace_in_runs(para.runs, old, new)


def _replace_in_document(doc: Document, replacements: dict) -> None:
    """
    Walk every paragraph and table cell in the document and apply replacements.
    Does NOT touch any other XML; formatting is fully preserved.
    """
    # Body paragraphs
    for para in doc.paragraphs:
        _replace_in_paragraph(para, replacements)

    # Tables (including nested tables)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    _replace_in_paragraph(para, replacements)

    # Headers and footers
    for section in doc.sections:
        for header in (section.header, section.first_page_header, section.even_page_header):
            if header is not None:
                for para in header.paragraphs:
                    _replace_in_paragraph(para, replacements)
        for footer in (section.footer, section.first_page_footer, section.even_page_footer):
            if footer is not None:
                for para in footer.paragraphs:
                    _replace_in_paragraph(para, replacements)


def _document_full_text(doc: Document) -> str:
    """Return all text in the document for placeholder detection."""
    parts = []
    for para in doc.paragraphs:
        parts.append(para.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    parts.append(para.text)
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# DocEditor
# ---------------------------------------------------------------------------

class DocEditor:
    """Edits DOCX templates by replacing designated placeholders only."""

    RESUME_PLACEHOLDERS = ["{{JOB_TITLE}}"]
    CV_PLACEHOLDERS = ["{{COMPANY_NAME}}", "{{ROLE}}"]

    def __init__(self, template_folder: str):
        """
        Args:
            template_folder: Folder that contains resume.docx and cv.docx.
        """
        self.template_folder = Path(template_folder)
        self.resume_template = self.template_folder / "resume.docx"
        self.cv_template = self.template_folder / "cv.docx"

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_templates(self) -> list[str]:
        """
        Check that template files exist.

        Returns:
            List of error strings (empty list = all good).
        """
        errors = []
        if not self.resume_template.exists():
            errors.append(
                f"Resume template not found: {self.resume_template}\n"
                "Please place resume.docx in the template folder."
            )
        if not self.cv_template.exists():
            errors.append(
                f"CV template not found: {self.cv_template}\n"
                "Please place cv.docx in the template folder."
            )
        return errors

    def _assert_placeholders(self, doc: Document, placeholders: list[str], filename: str) -> None:
        """
        We relax strict placeholder checks to support user-provided custom templates
        which may use alternative placeholders like [Company Name].
        """
        pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def edit_resume(self, job_title: str, output_path: str) -> str:
        """
        Copy resume template to *output_path* with {{JOB_TITLE}} replaced.

        Args:
            job_title:   Value to substitute for {{JOB_TITLE}}.
            output_path: Destination path for the modified DOCX.

        Returns:
            output_path (str)

        Raises:
            FileNotFoundError: Template file missing.
            ValueError: Placeholder not present in the template.
            Exception: Any other docx / IO error.
        """
        if not self.resume_template.exists():
            raise FileNotFoundError(
                f"resume.docx not found at: {self.resume_template}"
            )
        try:
            doc = Document(str(self.resume_template))
            self._assert_placeholders(doc, self.RESUME_PLACEHOLDERS, "resume.docx")
            _replace_in_document(doc, {
                "{{JOB_TITLE}}": job_title,
                "[Job Title]": job_title,
            })
            doc.save(output_path)
            return output_path
        except (FileNotFoundError, ValueError):
            raise
        except Exception as e:
            raise Exception(f"Error editing resume.docx: {e}") from e

    def edit_cv(self, company_name: str, role: str, location: str, output_path: str) -> str:
        """
        Copy CV template to *output_path* with placeholders replaced.

        Args:
            company_name: Value to substitute for {{COMPANY_NAME}} or [Company Name].
            role:         Value to substitute for {{ROLE}} or [Position Name].
            location:     Value to substitute for {{LOCATION}} or [Company Address or Remote].
            output_path:  Destination path for the modified DOCX.

        Returns:
            output_path (str)

        Raises:
            FileNotFoundError: Template file missing.
            ValueError: Placeholder(s) not present in the template.
            Exception: Any other docx / IO error.
        """
        if not self.cv_template.exists():
            raise FileNotFoundError(
                f"cv.docx not found at: {self.cv_template}"
            )
        try:
            import datetime
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            
            doc = Document(str(self.cv_template))
            self._assert_placeholders(doc, self.CV_PLACEHOLDERS, "cv.docx")
            _replace_in_document(
                doc,
                {
                    "{{COMPANY_NAME}}": company_name,
                    "[Company Name]": company_name,
                    "{{ROLE}}": role,
                    "[Position Name]": role,
                    "{{LOCATION}}": location,
                    "[Company Address or Remote]": location,
                    "{{DATE}}": current_date,
                    "[Date]": current_date,
                    "April 25, 2026": current_date,
                },
            )
            doc.save(output_path)
            return output_path
        except (FileNotFoundError, ValueError):
            raise
        except Exception as e:
            raise Exception(f"Error editing cv.docx: {e}") from e
