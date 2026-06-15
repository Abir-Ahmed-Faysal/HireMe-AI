"""
main.py
HireMe AI — Main Tkinter window.

Workflow:
  1. Paste a job circular into the text area.
  2. Click "Analyze" → Claude extracts Job Title / Company Name / Role.
  3. Edit the three fields as needed.
  4. Click "Generate PDFs" → doc_editor fills placeholders, LibreOffice
     converts to PDF, files land in the output folder.
  5. Click "Open Output Folder" to view results in Windows Explorer.
  6. Click "Settings" to manage paths and API key.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

from ai_engine import AIEngine, PROVIDERS, PROVIDER_ORDER
from doc_editor import DocEditor
from pdf_converter import PDFConverter
from settings_window import SettingsWindow


# ──────────────────────────────────────────────────────────────────────────────
# Palette
# ──────────────────────────────────────────────────────────────────────────────
BG        = "#1e2433"   # dark navy background
SURFACE   = "#252d3d"   # card / panel surface
SURFACE2  = "#2e3a52"   # slightly lighter surface (inputs)
ACCENT    = "#4f8ef7"   # primary blue accent
ACCENT2   = "#6ba3ff"   # hover / lighter accent
SUCCESS   = "#4caf7d"   # green for success
ERROR     = "#e05c5c"   # red for errors
WARNING   = "#f0a500"   # amber for warnings
TEXT      = "#e8eaf0"   # primary text
SUBTEXT   = "#8b93a8"   # secondary / label text
BORDER    = "#3a4560"   # subtle border
HEADER_H  = 56          # header bar height px


# ──────────────────────────────────────────────────────────────────────────────
# Config helpers
# ──────────────────────────────────────────────────────────────────────────────

def _config_path() -> Path:
    """Return the absolute path to config.json next to main.py / the EXE."""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent
    return base / "config.json"


def _load_config(path: Path) -> dict:
    """Load and return the config dict; returns {} on any error."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        messagebox.showerror("Config Error", f"config.json is malformed:\n{exc}")
        return {}
    except Exception as exc:
        messagebox.showerror("Config Error", f"Could not read config.json:\n{exc}")
        return {}


def _sanitize_filename(name: str) -> str:
    """Strip characters that are illegal in Windows filenames."""
    return "".join(
        c for c in name if c.isalnum() or c in (" ", "-", "_", ".")
    ).strip() or "Application"


# ──────────────────────────────────────────────────────────────────────────────
# Main Application
# ──────────────────────────────────────────────────────────────────────────────

class JobApplicationAI:
    """Main application controller and Tkinter window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HireMe AI")
        self.root.geometry("1020x720")
        self.root.minsize(800, 600)
        self.root.configure(bg=BG)

        # Try to set a window icon (silently skip if unavailable)
        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except Exception:
                pass

        self.config_path: Path = _config_path()
        self.config: dict = _load_config(self.config_path)

        # Engine handles — initialised after UI so status bar is available
        self.ai_engine: AIEngine | None = None
        self.doc_editor: DocEditor | None = None
        self.pdf_converter: PDFConverter | None = None

        self._build_ui()
        self._reinitialise_engines()

    # ──────────────────────────────────────────────────────────────────
    # Engine initialisation
    # ──────────────────────────────────────────────────────────────────

    def _reinitialise_engines(self) -> None:
        """Create / recreate AI, DocEditor and PDFConverter from config."""
        self.ai_engine     = None
        self.doc_editor    = None
        self.pdf_converter = None

        template_folder = self.config.get("template_folder", "").strip()
        output_folder   = self.config.get("output_folder", "").strip()
        lo_path         = self.config.get("libreoffice_path", "").strip()

        issues = []

        # ── AI Engine ──
        active_ai = self.config.get("active_ai", PROVIDER_ORDER[0])
        p_info = PROVIDERS.get(active_ai)
        if not p_info:
            active_ai = PROVIDER_ORDER[0]
            p_info = PROVIDERS[active_ai]
            
        api_key = self.config.get(p_info["config_key"], "").strip()

        if hasattr(self, "active_ai_var"):
            self.active_ai_var.set(active_ai)
            self._update_ui_for_ai(active_ai)

        if not api_key:
            issues.append(f"{p_info['name']} API Key not set — open Settings")
        else:
            try:
                self.ai_engine = AIEngine(active_ai, api_key)
            except Exception as exc:
                issues.append(f"AI Engine error: {exc}")

        # ── Doc Editor ──
        if not template_folder:
            issues.append("Template Folder not set — open Settings")
        else:
            try:
                self.doc_editor = DocEditor(template_folder)
                errs = self.doc_editor.validate_templates()
                if errs:
                    for e in errs:
                        issues.append(e)
                    self.doc_editor = None
            except Exception as exc:
                issues.append(f"Template error: {exc}")

        # ── PDF Converter ──
        if not output_folder:
            issues.append("Output Folder not set — open Settings")
        else:
            try:
                self.pdf_converter = PDFConverter(lo_path or None)
            except FileNotFoundError as exc:
                issues.append(str(exc))
            except Exception as exc:
                issues.append(f"LibreOffice error: {exc}")

        if issues:
            self._set_status(" | ".join(issues[:2]), color=WARNING)
        else:
            self._set_status("Ready — paste a job circular and click Analyze", color=SUCCESS)

    # ──────────────────────────────────────────────────────────────────
    # UI construction
    # ──────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        """Construct the entire main window."""
        self._build_header()
        self._build_body()
        self._build_status_bar()

    def _update_ui_for_ai(self, provider_id: str) -> None:
        """Update header and button text for active AI."""
        if not hasattr(self, "header_ai_lbl"): return
        p_info = PROVIDERS.get(provider_id)
        if not p_info: return
        self.header_ai_lbl.config(text=f"Powered by {p_info['name']}")
        self.analyze_btn.config(text=f"🔍  Analyze with {p_info['name']}")

    def _build_header(self) -> None:
        """Top accent bar with app name."""
        bar = tk.Frame(self.root, bg=ACCENT, height=HEADER_H)
        bar.pack(fill=tk.X, side=tk.TOP)
        bar.pack_propagate(False)

        tk.Label(
            bar,
            text="  ✦  HireMe AI",
            bg=ACCENT,
            fg="white",
            font=("Segoe UI", 15, "bold"),
            anchor="w",
        ).pack(side=tk.LEFT, padx=20, fill=tk.Y)

        self.header_ai_lbl = tk.Label(
            bar,
            text="Powered by AI",
            bg=ACCENT,
            fg="#c8d8ff",
            font=("Segoe UI", 9),
        )
        self.header_ai_lbl.pack(side=tk.RIGHT, padx=20)

    def _build_body(self) -> None:
        """Main content area."""
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # ── Left column (job circular + analyze) ────────────────────────
        left = tk.Frame(outer, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self._build_circular_section(left)

        # ── Right column (details + actions) ────────────────────────────
        right = tk.Frame(outer, bg=BG, width=320)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        self._build_details_section(right)
        self._build_action_buttons(right)

    # ── Job circular panel ─────────────────────────────────────────────

    def _build_circular_section(self, parent: tk.Frame) -> None:
        card = self._make_card(parent, "📋  Paste Job Circular Here")
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.circular_text = scrolledtext.ScrolledText(
            card,
            wrap=tk.WORD,
            bg=SURFACE2,
            fg=TEXT,
            insertbackground=TEXT,
            selectbackground=ACCENT,
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            padx=10,
            pady=8,
        )
        self.circular_text.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))

        # Placeholder hint text
        _placeholder = "Paste the full job description / advertisement here…"
        self.circular_text.insert("1.0", _placeholder)
        self.circular_text.config(fg=SUBTEXT)

        def _on_focus_in(event):
            if self.circular_text.get("1.0", tk.END).strip() == _placeholder:
                self.circular_text.delete("1.0", tk.END)
                self.circular_text.config(fg=TEXT)

        def _on_focus_out(event):
            if not self.circular_text.get("1.0", tk.END).strip():
                self.circular_text.insert("1.0", _placeholder)
                self.circular_text.config(fg=SUBTEXT)

        self.circular_text.bind("<FocusIn>",  _on_focus_in)
        self.circular_text.bind("<FocusOut>", _on_focus_out)

        # Analyze button row
        btn_row = tk.Frame(card, bg=SURFACE)
        btn_row.pack(fill=tk.X, padx=14, pady=(0, 14))

        self.analyze_btn = self._make_button(
            btn_row,
            "🔍  Analyze with AI",
            self._on_analyze,
            primary=True,
        )
        self.analyze_btn.pack(side=tk.LEFT)

        # AI Switcher Combobox
        self.active_ai_var = tk.StringVar(value=self.config.get("active_ai", PROVIDER_ORDER[0]))
        
        def _on_ai_changed(*args):
            new_ai = self.active_ai_var.get()
            if self.config.get("active_ai") == new_ai: return
            self.config["active_ai"] = new_ai
            # Save to file
            try:
                with open(self.config_path, "w", encoding="utf-8") as fh:
                    json.dump(self.config, fh, indent=2)
            except Exception:
                pass
            self._reinitialise_engines()

        self.active_ai_var.trace_add("write", _on_ai_changed)
        
        ai_combo = ttk.Combobox(
            btn_row, 
            textvariable=self.active_ai_var,
            values=list(PROVIDER_ORDER),
            state="readonly",
            width=10,
            font=("Segoe UI", 9)
        )
        ai_combo.pack(side=tk.LEFT, padx=(12, 0))

        self._analyze_progress = tk.Label(
            btn_row,
            text="",
            bg=SURFACE,
            fg=SUBTEXT,
            font=("Segoe UI", 8, "italic"),
        )
        self._analyze_progress.pack(side=tk.LEFT, padx=12)

    # ── Details panel ──────────────────────────────────────────────────

    def _build_details_section(self, parent: tk.Frame) -> None:
        card = self._make_card(parent, "📝  Extracted Job Details")
        card.pack(fill=tk.X, pady=(0, 10))

        self.job_title_var   = tk.StringVar()
        self.company_name_var = tk.StringVar()
        self.role_var         = tk.StringVar()
        self.location_var     = tk.StringVar()

        fields = [
            ("Job Title",    self.job_title_var,    "Suitable heading for your resume"),
            ("Company Name", self.company_name_var, "Employer / organisation name"),
            ("Role",         self.role_var,         "Exact position being applied for"),
            ("Location",     self.location_var,     "Job location or 'Remote'"),
        ]

        body = tk.Frame(card, bg=SURFACE)
        body.pack(fill=tk.X, padx=14, pady=(0, 14))

        for label_text, var, hint in fields:
            tk.Label(
                body,
                text=label_text.upper(),
                bg=SURFACE,
                fg=SUBTEXT,
                font=("Segoe UI", 7, "bold"),
                anchor="w",
            ).pack(fill=tk.X, pady=(10, 2))

            entry = tk.Entry(
                body,
                textvariable=var,
                bg=SURFACE2,
                fg=TEXT,
                insertbackground=TEXT,
                selectbackground=ACCENT,
                relief=tk.FLAT,
                font=("Segoe UI", 10),
                highlightthickness=1,
                highlightbackground=BORDER,
                highlightcolor=ACCENT,
            )
            entry.pack(fill=tk.X, ipady=7)

            tk.Label(
                body,
                text=hint,
                bg=SURFACE,
                fg=SUBTEXT,
                font=("Segoe UI", 7, "italic"),
                anchor="w",
            ).pack(fill=tk.X, pady=(2, 0))

    # ── Action buttons ─────────────────────────────────────────────────

    def _build_action_buttons(self, parent: tk.Frame) -> None:
        card = self._make_card(parent, "⚡  Actions")
        card.pack(fill=tk.X, pady=(0, 0))

        body = tk.Frame(card, bg=SURFACE)
        body.pack(fill=tk.X, padx=14, pady=(0, 14))

        self.generate_btn = self._make_button(
            body,
            "📄  Generate PDFs",
            self._on_generate_pdfs,
            primary=True,
        )
        self.generate_btn.pack(fill=tk.X, pady=(0, 8))

        self._make_button(
            body,
            "📁  Open Output Folder",
            self._on_open_output_folder,
        ).pack(fill=tk.X, pady=(0, 8))

        self._make_button(
            body,
            "⚙  Settings",
            self._on_settings,
        ).pack(fill=tk.X)

    # ── Status bar ─────────────────────────────────────────────────────

    def _build_status_bar(self) -> None:
        bar = tk.Frame(self.root, bg=SURFACE, height=30)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        # Coloured indicator dot
        self._status_dot = tk.Label(bar, text="●", bg=SURFACE, fg=SUBTEXT, font=("Segoe UI", 10))
        self._status_dot.pack(side=tk.LEFT, padx=(10, 4))

        self._status_var = tk.StringVar(value="Initialising…")
        tk.Label(
            bar,
            textvariable=self._status_var,
            bg=SURFACE,
            fg=SUBTEXT,
            font=("Segoe UI", 8),
            anchor="w",
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

    # ──────────────────────────────────────────────────────────────────
    # Widget factory helpers
    # ──────────────────────────────────────────────────────────────────

    def _make_card(self, parent: tk.Misc, title: str) -> tk.Frame:
        """Create a titled card frame (header label + content frame)."""
        wrapper = tk.Frame(parent, bg=SURFACE, bd=0, highlightthickness=1,
                           highlightbackground=BORDER)
        wrapper.pack_propagate(True)

        # Card title
        tk.Label(
            wrapper,
            text=title,
            bg=SURFACE,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill=tk.X, padx=14, pady=(12, 6))

        # Thin accent underline
        tk.Frame(wrapper, bg=ACCENT, height=2).pack(fill=tk.X, padx=14, pady=(0, 8))

        return wrapper

    def _make_button(
        self,
        parent: tk.Misc,
        text: str,
        command,
        *,
        primary: bool = False,
    ) -> tk.Button:
        bg     = ACCENT   if primary else SURFACE2
        fg     = "white"
        active = ACCENT2  if primary else BORDER

        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active,
            activeforeground="white",
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold" if primary else "normal"),
            cursor="hand2",
            padx=14,
            pady=8,
            bd=0,
        )

        # Hover effect
        btn.bind("<Enter>", lambda _e, b=btn, a=active: b.config(bg=a))
        btn.bind("<Leave>", lambda _e, b=btn, orig=bg: b.config(bg=orig))

        return btn

    # ──────────────────────────────────────────────────────────────────
    # Status bar helpers
    # ──────────────────────────────────────────────────────────────────

    def _set_status(self, message: str, *, color: str = SUBTEXT) -> None:
        """Update the status bar (thread-safe via after())."""
        def _update():
            self._status_var.set(message)
            self._status_dot.config(fg=color)

        self.root.after(0, _update)

    # ──────────────────────────────────────────────────────────────────
    # Event handlers
    # ──────────────────────────────────────────────────────────────────

    def _on_analyze(self) -> None:
        """Analyze the pasted job circular with Claude."""
        raw = self.circular_text.get("1.0", tk.END).strip()
        placeholder = "Paste the full job description / advertisement here…"

        if not raw or raw == placeholder:
            messagebox.showwarning(
                "HireMe AI",
                "Please paste a job circular into the text area first.",
            )
            return

        if self.ai_engine is None:
            active_ai = self.config.get("active_ai", PROVIDER_ORDER[0])
            p_info = PROVIDERS.get(active_ai, PROVIDERS[PROVIDER_ORDER[0]])
            messagebox.showerror(
                "HireMe AI",
                f"{p_info['name']} API is not configured.\n\nOpen Settings and enter your API key.",
            )
            return

        # Disable button, show spinner text
        self.analyze_btn.config(state=tk.DISABLED)
        self._analyze_progress.config(text="Analysing…")
        
        p_name = self.ai_engine.provider["name"]
        self._set_status(f"Sending job circular to {p_name}…", color=ACCENT)

        def _worker():
            try:
                details = self.ai_engine.extract_job_details(raw)
                # Update UI on the main thread
                self.root.after(0, lambda: self._populate_fields(details))
                self.root.after(0, lambda: self._set_status(
                    f"Analysis complete — review and edit the fields below",
                    color=SUCCESS,
                ))
            except Exception as exc:
                self.root.after(0, lambda e=exc: messagebox.showerror(
                    "Analysis Failed", str(e)
                ))
                self.root.after(0, lambda: self._set_status(
                    f"Analysis failed — {exc}", color=ERROR
                ))
            finally:
                self.root.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self._analyze_progress.config(text=""))

        threading.Thread(target=_worker, daemon=True).start()

    def _populate_fields(self, details: dict) -> None:
        """Fill the three editable fields from the extracted details dict."""
        self.job_title_var.set(details.get("job_title", ""))
        self.company_name_var.set(details.get("company_name", ""))
        self.role_var.set(details.get("role", ""))
        self.location_var.set(details.get("location", ""))

    def _on_generate_pdfs(self) -> None:
        """Edit DOCX templates and convert to PDF."""
        job_title    = self.job_title_var.get().strip()
        company_name = self.company_name_var.get().strip()
        role         = self.role_var.get().strip()
        location     = self.location_var.get().strip()

        # Handle missing fields with fallbacks
        if not job_title:
            job_title = "the position"
            self.job_title_var.set(job_title)
        if not company_name:
            company_name = "your company"
            self.company_name_var.set(company_name)
        if not role:
            role = "the role"
            self.role_var.set(role)
        if not location:
            location = "Remote"
            self.location_var.set(location)

        if self.doc_editor is None:
            messagebox.showerror(
                "HireMe AI",
                "Document editor is not ready.\n\n"
                "Check that resume.docx and cv.docx exist in the template folder "
                "(Settings → Template Folder).",
            )
            return

        if self.pdf_converter is None:
            messagebox.showerror(
                "HireMe AI",
                "PDF converter is not ready.\n\n"
                "Check the LibreOffice path in Settings.",
            )
            return

        output_folder = self.config.get("output_folder", "").strip()
        if not output_folder:
            messagebox.showerror(
                "HireMe AI",
                "Output folder is not configured.\n\nOpen Settings and set an output folder.",
            )
            return

        safe_company = _sanitize_filename(company_name)

        self.generate_btn.config(state=tk.DISABLED)
        self._set_status("Generating PDFs — please wait…", color=ACCENT)

        def _worker():
            tmp_dir = None
            try:
                tmp_dir = Path(tempfile.mkdtemp())

                resume_tmp = tmp_dir / "resume_temp.docx"
                cv_tmp     = tmp_dir / "cv_temp.docx"

                # Step 1 — Edit DOCX templates
                self.root.after(0, lambda: self._set_status(
                    "Step 1 / 3 — Editing DOCX templates…", color=ACCENT
                ))
                self.doc_editor.edit_resume(job_title, str(resume_tmp))
                self.doc_editor.edit_cv(company_name, role, location, str(cv_tmp))

                # Step 2 — Convert to PDF
                self.root.after(0, lambda: self._set_status(
                    "Step 2 / 3 — Converting to PDF via LibreOffice…", color=ACCENT
                ))
                resume_pdf, cv_pdf = self.pdf_converter.generate_pdfs(
                    str(resume_tmp),
                    str(cv_tmp),
                    safe_company,
                    output_folder,
                )

                # Step 3 — Done
                self.root.after(0, lambda: self._set_status(
                    f"✅  PDFs created: {resume_pdf.name}  &  {cv_pdf.name}",
                    color=SUCCESS,
                ))
                self.root.after(0, lambda: messagebox.showinfo(
                    "PDFs Created Successfully",
                    f"Your application documents are ready:\n\n"
                    f"  📄  {resume_pdf.name}\n"
                    f"  📄  {cv_pdf.name}\n\n"
                    f"Saved to:\n  {output_folder}",
                ))

            except Exception as exc:
                self.root.after(0, lambda e=exc: messagebox.showerror(
                    "PDF Generation Failed", str(e)
                ))
                self.root.after(0, lambda e=exc: self._set_status(
                    f"Error: {e}", color=ERROR
                ))
            finally:
                # Clean up temp directory (DOCX files already deleted by pdf_converter)
                if tmp_dir and tmp_dir.exists():
                    shutil.rmtree(tmp_dir, ignore_errors=True)
                self.root.after(0, lambda: self.generate_btn.config(state=tk.NORMAL))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_open_output_folder(self) -> None:
        """Open the output folder in Windows Explorer."""
        output_folder = self.config.get("output_folder", "").strip()

        if not output_folder:
            messagebox.showerror(
                "HireMe AI",
                "Output folder is not configured.\n\nOpen Settings to set one.",
            )
            return

        folder = Path(output_folder)
        if not folder.exists():
            try:
                folder.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                messagebox.showerror(
                    "HireMe AI",
                    f"Could not create the output folder:\n{exc}",
                )
                return

        try:
            os.startfile(folder)
        except AttributeError:
            # Non-Windows fallback (e.g. running in a POSIX test environment)
            subprocess.Popen(["xdg-open", str(folder)])
        except Exception as exc:
            messagebox.showerror(
                "HireMe AI",
                f"Could not open folder:\n{exc}",
            )

    def _on_settings(self) -> None:
        """Open the settings window (modal); reload config and engines on return."""
        SettingsWindow(self.root, self.config_path)
        # SettingsWindow uses wait_window(), so execution resumes here after close
        self.config = _load_config(self.config_path)
        self._reinitialise_engines()


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    root = tk.Tk()
    JobApplicationAI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
