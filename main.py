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
import traceback

from ai_engine import AIEngine, PROVIDERS, PROVIDER_ORDER
from doc_editor import DocEditor
from pdf_converter import PDFConverter
from settings_window import SettingsWindow
from history_manager import HistoryManager
from logger_manager import LoggerManager


# ──────────────────────────────────────────────────────────────────────────────
# Palette - Professional Dark Theme
# ──────────────────────────────────────────────────────────────────────────────
BG        = "#0f1419"   # deep dark background (more professional)
SURFACE   = "#1a1f2e"   # card / panel surface
SURFACE2  = "#242d3f"   # slightly lighter surface (inputs)
ACCENT    = "#5b9fff"   # vibrant blue accent (more visible)
ACCENT2   = "#7aadff"   # hover / lighter accent
SUCCESS   = "#50d76e"   # bright green for success
ERROR     = "#ff6b6b"   # bright red for errors
WARNING   = "#ffa500"   # bright amber for warnings
TEXT      = "#e8eaf0"   # primary text (high contrast)
SUBTEXT   = "#9ba5b8"   # secondary / label text
BORDER    = "#2a3447"   # subtle border
HEADER_H  = 60          # header bar height px


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
        self.root.title("HireMe AI — Smart Job Application Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(900, 650)
        self.root.configure(bg=BG)
        
        # Improve window appearance
        self.root.option_add("*Font", "{Segoe UI} 9")
        self.root.option_add("*Background", BG)
        self.root.option_add("*Foreground", TEXT)

        # Try to set a window icon (silently skip if unavailable)
        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except Exception:
                pass

        self.config_path: Path = _config_path()
        self.config: dict = _load_config(self.config_path)

        # Initialize history and logging managers
        self.history_manager = HistoryManager()
        self.logger_manager = LoggerManager()
        self.logger_manager.info("Application started")

        # Engine handles — initialised after UI so status bar is available
        self.ai_engine: AIEngine | None = None
        self.doc_editor: DocEditor | None = None
        self.pdf_converter: PDFConverter | None = None

        self._build_ui()
        self._load_draft_on_startup()
        self._setup_autosave()
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
    # Draft and history management
    # ──────────────────────────────────────────────────────────────────

    def _load_draft_on_startup(self) -> None:
        """Load last saved draft if available (data recovery feature)."""
        draft = self.history_manager.load_draft()
        if draft and any(draft.values()):
            # Check if form fields exist (they're created during _build_ui)
            if hasattr(self, "job_title_var"):
                self.job_title_var.set(draft.get("job_title", ""))
                self.company_name_var.set(draft.get("company", ""))
                self.role_var.set(draft.get("role", ""))
                if draft.get("job_circular"):
                    self.circular_text.delete("1.0", tk.END)
                    self.circular_text.insert("1.0", draft.get("job_circular", ""))
                    self.circular_text.config(fg=TEXT)
                self.logger_manager.info("Draft recovered from previous session")

    def _setup_autosave(self) -> None:
        """Setup auto-save of form data every 30 seconds."""
        def _autosave():
            try:
                if hasattr(self, "job_title_var"):
                    self.history_manager.save_draft(
                        job_title=self.job_title_var.get(),
                        company=self.company_name_var.get(),
                        role=self.role_var.get(),
                        job_circular=self.circular_text.get("1.0", tk.END).strip()
                    )
            except Exception as exc:
                self.logger_manager.debug(f"Autosave failed: {exc}")
            finally:
                # Schedule next autosave in 30 seconds
                self.root.after(30000, _autosave)
        
        # Start autosave loop
        self.root.after(30000, _autosave)

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

        # Left side: App name
        left_frame = tk.Frame(bar, bg=ACCENT)
        left_frame.pack(side=tk.LEFT, padx=24, fill=tk.Y)
        
        tk.Label(
            left_frame,
            text="HireMe AI",
            bg=ACCENT,
            fg="white",
            font=("Segoe UI", 16, "bold"),
            anchor="w",
        ).pack(side=tk.LEFT, pady=8)
        
        tk.Label(
            left_frame,
            text="Smart Job Application Assistant",
            bg=ACCENT,
            fg="#b8d0ff",
            font=("Segoe UI", 7),
            anchor="w",
        ).pack(side=tk.LEFT, padx=(12, 0), pady=8)

        # Right side: Powered by
        self.header_ai_lbl = tk.Label(
            bar,
            text="Powered by AI",
            bg=ACCENT,
            fg="#d0e0ff",
            font=("Segoe UI", 9),
        )
        self.header_ai_lbl.pack(side=tk.RIGHT, padx=24, pady=8)

    def _build_body(self) -> None:
        """Main content area with responsive layout."""
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

        # ── Left column (job circular + analyze) ────────────────────────
        left = tk.Frame(outer, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 16))

        self._build_circular_section(left)

        # ── Right column (details + actions) — scrollable ───────────────
        right_outer = tk.Frame(outer, bg=BG, width=360)
        right_outer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(16, 0))
        right_outer.pack_propagate(False)

        # Scrollable canvas for right panel content
        right_canvas = tk.Canvas(
            right_outer, bg=BG, bd=0, highlightthickness=0
        )
        right_scroll = tk.Scrollbar(
            right_outer, orient=tk.VERTICAL, command=right_canvas.yview,
            bg=BG, activebackground=BORDER
        )
        right_canvas.configure(yscrollcommand=right_scroll.set)

        right_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = tk.Frame(right_canvas, bg=BG)
        right_window = right_canvas.create_window((0, 0), window=right, anchor="nw")

        def _on_right_configure(event):
            right_canvas.configure(scrollregion=right_canvas.bbox("all"))
            right_canvas.itemconfig(right_window, width=right_canvas.winfo_width())

        def _on_canvas_resize(event):
            right_canvas.itemconfig(right_window, width=event.width)

        right.bind("<Configure>", _on_right_configure)
        right_canvas.bind("<Configure>", _on_canvas_resize)

        # Mouse-wheel scrolling
        def _on_mousewheel(event):
            right_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        right_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self._build_details_section(right)
        self._build_skills_section(right)
        self._build_action_buttons(right)

    # ── Job circular panel ─────────────────────────────────────────────

    def _build_circular_section(self, parent: tk.Frame) -> None:
        card = self._make_card(parent, "📋  Job Posting")
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        self.circular_text = scrolledtext.ScrolledText(
            card,
            wrap=tk.WORD,
            bg=SURFACE2,
            fg=TEXT,
            insertbackground=ACCENT,
            selectbackground=ACCENT,
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            padx=12,
            pady=10,
        )
        self.circular_text.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

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

        # Analyze button row with AI selector
        btn_row = tk.Frame(card, bg=SURFACE)
        btn_row.pack(fill=tk.X, padx=16, pady=(0, 16))

        self.analyze_btn = self._make_button(
            btn_row,
            "🔍  Analyze",
            self._on_analyze,
            primary=True,
        )
        self.analyze_btn.pack(side=tk.LEFT, expand=False)

        # Spacing
        tk.Frame(btn_row, bg=SURFACE, width=8).pack(side=tk.LEFT)

        # AI Switcher Label
        tk.Label(
            btn_row,
            text="AI:",
            bg=SURFACE,
            fg=SUBTEXT,
            font=("Segoe UI", 8, "bold"),
        ).pack(side=tk.LEFT, padx=(4, 4))

        # AI Switcher Combobox
        self.active_ai_var = tk.StringVar(value=self.config.get("active_ai", PROVIDER_ORDER[0]))
        
        def _on_ai_changed(*args):
            new_ai = self.active_ai_var.get()
            if self.config.get("active_ai") == new_ai: return
            self.config["active_ai"] = new_ai
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
            width=11,
            font=("Segoe UI", 8)
        )
        ai_combo.pack(side=tk.LEFT, padx=(0, 8))

        # Progress indicator
        self._analyze_progress = tk.Label(
            btn_row,
            text="",
            bg=SURFACE,
            fg=ACCENT,
            font=("Segoe UI", 8, "italic"),
        )
        self._analyze_progress.pack(side=tk.LEFT, padx=0)

    # ── Details panel ──────────────────────────────────────────────────

    def _build_details_section(self, parent: tk.Frame) -> None:
        card = self._make_card(parent, "📝  Job Details")
        card.pack(fill=tk.X, pady=(0, 12))

        self.job_title_var    = tk.StringVar()
        self.tech_stack_var   = tk.StringVar()
        self.company_name_var = tk.StringVar()
        self.role_var         = tk.StringVar()
        self.location_var     = tk.StringVar()

        fields = [
            ("Job Title",    self.job_title_var,    "e.g., Full Stack Developer"),
            ("Company",      self.company_name_var, "Company name"),
            ("Role",         self.role_var,         "Position title"),
            ("Tech Stack",   self.tech_stack_var,   "e.g., React · Node.js · PostgreSQL"),
            ("Location",     self.location_var,     "City or Remote"),
        ]

        body = tk.Frame(card, bg=SURFACE)
        body.pack(fill=tk.X, padx=16, pady=(0, 16))

        for label_text, var, hint in fields:
            tk.Label(
                body,
                text=label_text.upper(),
                bg=SURFACE,
                fg=ACCENT,
                font=("Segoe UI", 7, "bold"),
                anchor="w",
            ).pack(fill=tk.X, pady=(8, 3))

            entry = tk.Entry(
                body,
                textvariable=var,
                bg=SURFACE2,
                fg=TEXT,
                insertbackground=ACCENT,
                selectbackground=ACCENT,
                relief=tk.FLAT,
                font=("Segoe UI", 9),
                highlightthickness=1,
                highlightbackground=BORDER,
                highlightcolor=ACCENT,
            )
            entry.pack(fill=tk.X, ipady=6)

            tk.Label(
                body,
                text=hint,
                bg=SURFACE,
                fg=SUBTEXT,
                font=("Segoe UI", 7),
                anchor="w",
            ).pack(fill=tk.X, pady=(1, 0))

        # Live preview of the formatted headline
        preview_frame = tk.Frame(body, bg=SURFACE)
        preview_frame.pack(fill=tk.X, pady=(12, 0))

        tk.Label(
            preview_frame,
            text="HEADLINE PREVIEW",
            bg=SURFACE,
            fg=ACCENT,
            font=("Segoe UI", 7, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 4))

        self._headline_preview = tk.Label(
            preview_frame,
            text="—",
            bg=SURFACE2,
            fg=SUCCESS,
            font=("Segoe UI", 8),
            anchor="w",
            padx=10,
            pady=7,
            wraplength=280,
            justify=tk.LEFT,
        )
        self._headline_preview.pack(fill=tk.X)

        # Update preview whenever job_title or tech_stack changes
        def _update_preview(*_):
            title = self.job_title_var.get().strip()
            stack = self.tech_stack_var.get().strip()
            title_lower = title.lower()
            use_stack = any(r in title_lower for r in self._TECH_STACK_ROLES)
            if title and stack and use_stack:
                preview = f"{title}  |  {stack}"
            elif title:
                preview = title
            else:
                preview = "—"
            self._headline_preview.config(text=preview)

        self.job_title_var.trace_add("write", _update_preview)
        self.tech_stack_var.trace_add("write", _update_preview)

    # ── Skills section ─────────────────────────────────────────────────

    def _build_skills_section(self, parent: tk.Frame) -> None:
        """Skills section with checkboxes for missing skills from job circular."""
        card = self._make_card(parent, "🔧  Missing Skills")
        card.pack(fill=tk.X, pady=(0, 12))

        body = tk.Frame(card, bg=SURFACE)
        body.pack(fill=tk.X, padx=16, pady=(0, 16))

        # ── Scrollable skills list ───────────────────────────────────────
        list_canvas = tk.Canvas(body, bg=SURFACE, highlightthickness=0, height=160)
        list_scroll = tk.Scrollbar(body, orient=tk.VERTICAL, command=list_canvas.yview,
                                   bg=SURFACE, activebackground=BORDER)
        list_canvas.configure(yscrollcommand=list_scroll.set)

        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.skills_container = tk.Frame(list_canvas, bg=SURFACE)
        skills_win = list_canvas.create_window((0, 0), window=self.skills_container, anchor="nw")

        def _on_skills_configure(event):
            list_canvas.configure(scrollregion=list_canvas.bbox("all"))
            list_canvas.itemconfig(skills_win, width=list_canvas.winfo_width())
        def _on_list_canvas_resize(event):
            list_canvas.itemconfig(skills_win, width=event.width)
        self.skills_container.bind("<Configure>", _on_skills_configure)
        list_canvas.bind("<Configure>", _on_list_canvas_resize)

        def _mousewheel_skills(event):
            list_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        list_canvas.bind("<MouseWheel>", _mousewheel_skills)
        self.skills_container.bind("<MouseWheel>", _mousewheel_skills)

        # Initially empty message
        self.skills_empty_msg = tk.Label(
            self.skills_container,
            text="Analyze a job posting to see missing skills",
            bg=SURFACE,
            fg=SUBTEXT,
            font=("Segoe UI", 8, "italic"),
        )
        self.skills_empty_msg.pack(fill=tk.X, pady=8)

        # ── Manual add row ───────────────────────────────────────────────
        add_frame = tk.Frame(card, bg=SURFACE)
        add_frame.pack(fill=tk.X, padx=16, pady=(4, 12))

        tk.Label(
            add_frame,
            text="ADD SKILL MANUALLY",
            bg=SURFACE, fg=ACCENT,
            font=("Segoe UI", 7, "bold"),
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 4))

        entry_row = tk.Frame(add_frame, bg=SURFACE)
        entry_row.pack(fill=tk.X)

        self._manual_skill_var = tk.StringVar()
        manual_entry = tk.Entry(
            entry_row,
            textvariable=self._manual_skill_var,
            bg=SURFACE2, fg=TEXT,
            insertbackground=ACCENT,
            relief=tk.FLAT,
            font=("Segoe UI", 9),
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        manual_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 6))

        def _add_manual_skill(event=None):
            skill = self._manual_skill_var.get().strip()
            if not skill:
                return
            if skill in self.skills_data:
                self._manual_skill_var.set("")
                return
            # Remove empty-state message if still there
            for w in self.skills_container.winfo_children():
                if isinstance(w, tk.Label):
                    w.destroy()
            self._add_skill_checkbox(skill, checked=True)
            self._manual_skill_var.set("")

        manual_entry.bind("<Return>", _add_manual_skill)

        tk.Button(
            entry_row,
            text="＋ Add",
            command=_add_manual_skill,
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT2,
            activeforeground="white",
            relief=tk.FLAT,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=10, pady=4,
        ).pack(side=tk.LEFT)

        # Store checkbox variables and skills data
        self.skills_data = {}  # {skill_name: tk.BooleanVar}

    def _add_skill_checkbox(self, skill: str, checked: bool = False) -> None:
        """Add a single skill checkbox row to the skills container."""
        var = tk.BooleanVar(value=checked)
        self.skills_data[skill] = var

        row = tk.Frame(self.skills_container, bg=SURFACE)
        row.pack(fill=tk.X, pady=1)

        cb = tk.Checkbutton(
            row,
            text=skill,
            variable=var,
            bg=SURFACE,
            fg=TEXT,
            selectcolor=SURFACE2,
            activebackground=SURFACE,
            activeforeground=ACCENT,
            font=("Segoe UI", 9),
            highlightthickness=0,
            anchor="w",
        )
        cb.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ✕ remove button
        def _remove(s=skill, r=row):
            del self.skills_data[s]
            r.destroy()
        tk.Button(
            row,
            text="✕",
            command=_remove,
            bg=SURFACE,
            fg=SUBTEXT,
            activebackground=SURFACE,
            activeforeground="#e05c5c",
            relief=tk.FLAT,
            font=("Segoe UI", 8),
            cursor="hand2",
            bd=0, padx=4,
        ).pack(side=tk.RIGHT)

    def _populate_skills_section(self, missing_skills: list[str]) -> None:
        """
        Populate skills section with checkboxes for missing skills.
        
        Args:
            missing_skills: List of skills missing from the resume (AI-determined)
        """
        # Clear previous checkboxes
        for widget in self.skills_container.winfo_children():
            widget.destroy()
        self.skills_data.clear()

        if not missing_skills:
            tk.Label(
                self.skills_container,
                text="✅ You already have all the skills from this job!",
                bg=SURFACE,
                fg=SUCCESS,
                font=("Segoe UI", 8, "italic"),
            ).pack(fill=tk.X, pady=8)
            return

        # Header hint
        tk.Label(
            self.skills_container,
            text=f"☑ Tick skills to add to your resume  ({len(missing_skills)} missing)",
            bg=SURFACE, fg=SUBTEXT,
            font=("Segoe UI", 7, "italic"),
            anchor="w",
        ).pack(fill=tk.X, pady=(4, 6))

        for skill in missing_skills:
            self._add_skill_checkbox(skill, checked=False)

    def _get_selected_skills(self) -> list[str]:
        """Return list of skills that are checked."""
        return [skill for skill, var in self.skills_data.items() if var.get()]

    # ── Action buttons ─────────────────────────────────────────────────

    def _build_action_buttons(self, parent: tk.Frame) -> None:
        card = self._make_card(parent, "⚡  Actions")
        card.pack(fill=tk.X, pady=(0, 0))

        body = tk.Frame(card, bg=SURFACE)
        body.pack(fill=tk.X, padx=16, pady=(0, 16))

        self.generate_btn = self._make_button(
            body,
            "📄  Generate PDFs",
            self._on_generate_pdfs,
            primary=True,
        )
        self.generate_btn.pack(fill=tk.X, pady=(0, 10), ipady=2)

        self._make_button(
            body,
            "📁  Open Output Folder",
            self._on_open_output_folder,
        ).pack(fill=tk.X, pady=(0, 10), ipady=2)

        self._make_button(
            body,
            "⚙️  Settings",
            self._on_settings,
        ).pack(fill=tk.X, ipady=2)

    # ── Status bar ─────────────────────────────────────────────────────

    def _build_status_bar(self) -> None:
        bar = tk.Frame(self.root, bg=SURFACE, height=36)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        # Coloured indicator dot
        self._status_dot = tk.Label(bar, text="●", bg=SURFACE, fg=SUBTEXT, font=("Segoe UI", 10))
        self._status_dot.pack(side=tk.LEFT, padx=(16, 8), pady=8)

        self._status_var = tk.StringVar(value="Initialising…")
        tk.Label(
            bar,
            textvariable=self._status_var,
            bg=SURFACE,
            fg=TEXT,
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 16), pady=8)

    # ──────────────────────────────────────────────────────────────────
    # Widget factory helpers
    # ──────────────────────────────────────────────────────────────────

    def _make_card(self, parent: tk.Misc, title: str) -> tk.Frame:
        """Create a titled card frame (header label + content frame)."""
        wrapper = tk.Frame(parent, bg=SURFACE, bd=0, highlightthickness=1,
                           highlightbackground=BORDER)
        wrapper.pack_propagate(True)

        # Card title
        title_frame = tk.Frame(wrapper, bg=SURFACE)
        title_frame.pack(fill=tk.X, padx=16, pady=(14, 8))
        
        tk.Label(
            title_frame,
            text=title,
            bg=SURFACE,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(side=tk.LEFT)

        # Thin accent underline
        tk.Frame(wrapper, bg=ACCENT, height=1).pack(fill=tk.X, padx=16, pady=(0, 8))

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
        active = ACCENT2  if primary else ACCENT

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
            padx=12,
            pady=10,
            bd=0,
            highlightthickness=0,
        )

        # Hover effect with smooth transition
        def _on_enter(event):
            btn.config(bg=active)
        
        def _on_leave(event):
            btn.config(bg=bg)

        btn.bind("<Enter>", _on_enter)
        btn.bind("<Leave>", _on_leave)

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
        """Analyze the pasted job circular with comprehensive error handling."""
        raw = self.circular_text.get("1.0", tk.END).strip()
        placeholder = "Paste the full job description / advertisement here…"

        if not raw or raw == placeholder:
            messagebox.showwarning(
                "HireMe AI",
                "Please paste a job posting into the text area first.\n\n"
                "Copy a job description from a website (LinkedIn, job boards, etc.) "
                "and paste it here.",
            )
            return
        
        if len(raw) < 50:
            messagebox.showwarning(
                "HireMe AI",
                "Job posting is too short. Please paste a complete job description "
                "(at least a few sentences).",
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
                # Extract job details with error handling
                try:
                    details = self.ai_engine.extract_job_details(raw)
                    self.root.after(0, lambda: self._populate_fields(details))
                except Exception as exc:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Analysis Failed",
                        f"Could not extract job details:\n\n{exc}",
                    ))
                    self.root.after(0, lambda: self._set_status(
                        f"Analysis failed", color=ERROR
                    ))
                    return
                
                # Extract skills (non-blocking failure)
                try:
                    resume_text = ""
                    if self.doc_editor and hasattr(self.doc_editor, 'get_resume_text'):
                        resume_text = self.doc_editor.get_resume_text()
                        
                    skills = self.ai_engine.extract_skills(raw, resume_text=resume_text)
                    self.root.after(0, lambda s=skills: self._populate_skills_section(s))
                except Exception as e:
                    # Log but don't show error - skills are optional
                    print(f"[INFO] Skills extraction skipped: {e}")
                
                self.root.after(0, lambda: self._set_status(
                    "✓ Analysis complete — review and edit fields below",
                    color=SUCCESS,
                ))
            except Exception as exc:
                error_msg = str(exc)
                self.root.after(0, lambda: messagebox.showerror(
                    "Analysis Error",
                    f"Unexpected error during analysis:\n\n{error_msg}",
                ))
                self.root.after(0, lambda: self._set_status(
                    "Analysis error", color=ERROR
                ))
                # Log the error
                company = self.company_name_var.get() if hasattr(self, "company_name_var") else "Unknown"
                role = self.role_var.get() if hasattr(self, "role_var") else "Unknown"
                self.logger_manager.log_analysis(company, role, p_name, False)
            finally:
                self.root.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self._analyze_progress.config(text=""))

        threading.Thread(target=_worker, daemon=True).start()

    # Roles where "Title  |  Tech Stack" headline format is used.
    # All other roles get a plain title without the tech stack suffix.
    _TECH_STACK_ROLES = {
        "full stack developer",
        "full-stack developer",
        "fullstack developer",
        "frontend developer",
        "front end developer",
        "front-end developer",
    }

    def _populate_fields(self, details: dict) -> None:
        """Fill the editable fields from the extracted details dict.

        For Full Stack Developer and Frontend Developer roles the headline is:
            <job_title>  |  <tech_stack>
        For all other roles (Software Engineer, Backend Dev, MERN Stack, etc.)
        the plain job title is used without a tech stack suffix.
        """
        raw_title = details.get("job_title", "").strip()
        tech      = details.get("tech_stack", "").strip()

        # Only append tech stack for the two supported role types
        title_lower = raw_title.lower()
        use_stack = any(role in title_lower for role in self._TECH_STACK_ROLES)

        formatted_title = f"{raw_title}  |  {tech}" if (use_stack and tech) else raw_title

        self.job_title_var.set(formatted_title)
        self.tech_stack_var.set(tech)
        company = details.get("company_name", "")
        self.company_name_var.set(company)
        role = details.get("role", "")
        self.role_var.set(role)
        self.location_var.set(details.get("location", ""))
        
        # Save to history and log successful analysis
        job_circular = self.circular_text.get("1.0", tk.END).strip()
        self.history_manager.add_to_history(formatted_title, company, role, job_circular)
        self.logger_manager.log_analysis(company, role, self.ai_engine.provider["name"], True)

    def _on_generate_pdfs(self) -> None:
        """Edit DOCX templates and convert to PDF with comprehensive validation."""
        job_title    = self.job_title_var.get().strip()
        company_name = self.company_name_var.get().strip()
        role         = self.role_var.get().strip()
        location     = self.location_var.get().strip()

        # Validate minimum required fields
        if not job_title:
            messagebox.showwarning(
                "Missing Information",
                "Job Title is required. Please enter a job title or analyze a job posting first.",
            )
            return
        
        if not company_name:
            messagebox.showwarning(
                "Missing Information",
                "Company Name is required. Please enter a company name.",
            )
            return
        
        if not role:
            messagebox.showwarning(
                "Missing Information",
                "Role is required. Please enter the job role.",
            )
            return

        # Check engines are ready
        if self.doc_editor is None:
            messagebox.showerror(
                "Configuration Error",
                "Document templates are not ready.\n\n"
                "Make sure:\n"
                "• resume.docx and cv.docx exist in your template folder\n"
                "• Template folder path is set in Settings\n\n"
                "Run 'python setup_templates.py' if templates are missing.",
            )
            return

        if self.pdf_converter is None:
            messagebox.showerror(
                "Configuration Error",
                "PDF converter (LibreOffice) is not ready.\n\n"
                "Make sure:\n"
                "• LibreOffice is installed\n"
                "• LibreOffice path is correct in Settings\n\n"
                "Download from: https://www.libreoffice.org/",
            )
            return

        output_folder = self.config.get("output_folder", "").strip()
        if not output_folder:
            messagebox.showerror(
                "Configuration Error",
                "Output folder is not configured.\n\n"
                "Open Settings and set an output folder for generated PDFs.",
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
                try:
                    self.root.after(0, lambda: self._set_status(
                        "Step 1/3 — Editing templates…", color=ACCENT
                    ))
                    selected_skills = self._get_selected_skills()
                    self.doc_editor.edit_resume(job_title, str(resume_tmp), role=role)
                    self.doc_editor.edit_cv(company_name, role, location, str(cv_tmp), job_title=job_title)
                    
                    # ── Add selected skills to resume ──
                    if selected_skills:
                        self.doc_editor.add_skills_to_resume(str(resume_tmp), selected_skills)
                except Exception as e:
                    self.root.after(0, lambda e=e: messagebox.showerror(
                        "Template Error",
                        f"Could not edit templates:\n\n{e}",
                    ))
                    return
                
                # Step 2 — Convert to PDF
                try:
                    self.root.after(0, lambda: self._set_status(
                        "Step 2/3 — Converting to PDF…", color=ACCENT
                    ))
                    resume_pdf, cv_pdf = self.pdf_converter.generate_pdfs(
                        str(resume_tmp),
                        str(cv_tmp),
                        safe_company,
                        output_folder,
                        role=role,
                        applicant_name=self.config.get("applicant_name", "Applicant"),
                    )
                    # ── Skills automatically added ────────────────────────
                    if selected_skills:
                        skills_list = "\n".join(f"  ✓ {s}" for s in selected_skills)
                        self.root.after(0, lambda sl=skills_list: messagebox.showinfo(
                            "✅ Skills Added Successfully",
                            "Great! The following skills have been automatically added to your resume:\n\n"
                            + sl +
                            "\n\nThey're now in the relevant subsections (Frontend, Backend, Auth, Tools).",
                        ))
                except Exception as e:
                    self.root.after(0, lambda e=e: messagebox.showerror(
                        "PDF Conversion Error",
                        f"Could not convert to PDF:\n\n{e}",
                    ))
                    return

                # Step 3 — Done
                subfolder_name = resume_pdf.parent.name
                self.root.after(0, lambda: self._set_status(
                    f"✓ PDFs created successfully",
                    color=SUCCESS,
                ))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success!",
                    f"Your PDFs are ready:\n\n"
                    f"  • {resume_pdf.name}\n"
                    f"  • {cv_pdf.name}\n\n"
                    f"Location:\n{subfolder_name}\n\n"
                    f"Click 'Open Output Folder' to view.",
                ))
                
                # Log successful generation and clear draft
                self.logger_manager.log_generation(company_name, role, 2, True)
                self.history_manager.clear_draft()
            except Exception as exc:
                error_trace = traceback.format_exc()
                print(f"[ERROR] PDF generation failed:\n{error_trace}")
                self.root.after(0, lambda e=exc: messagebox.showerror(
                    "Unexpected Error",
                    f"Something went wrong:\n\n{e}",
                ))
                self.root.after(0, lambda: self._set_status(
                    "PDF generation failed", color=ERROR
                ))
                # Log failed generation
                self.logger_manager.log_generation(company_name, role, 0, False)
            finally:
                # Clean up temp directory
                if tmp_dir and tmp_dir.exists():
                    try:
                        shutil.rmtree(tmp_dir, ignore_errors=True)
                    except Exception:
                        pass  # Ignore cleanup errors
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
