"""
settings_window.py
Settings / Configuration window for HireMe AI.

Loads from and saves to config.json.
Allows browsing for folders and the LibreOffice executable.
Provides a "Test AI Connection" button for all providers.
"""

import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ai_engine import AIEngine, PROVIDERS, PROVIDER_ORDER


class SettingsWindow(tk.Toplevel):
    """Modal settings window."""

    # ------------------------------------------------------------------ #
    # Construction                                                         #
    # ------------------------------------------------------------------ #

    def __init__(self, parent: tk.Misc, config_path: Path):
        super().__init__(parent)
        self.title("Settings — HireMe AI")
        self.resizable(False, False)

        # Colours (kept in sync with main window)
        self._BG       = "#1e2433"
        self._SURFACE  = "#252d3d"
        self._ACCENT   = "#4f8ef7"
        self._TEXT     = "#e8eaf0"
        self._SUBTEXT  = "#8b93a8"
        self._ENTRY_BG = "#2e3a52"
        self._BORDER   = "#3a4560"

        self.configure(bg=self._BG)
        self.config_path = Path(config_path)
        self._config: dict = self._load_config()

        self._build_ui()

        # Centre relative to parent
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{px}+{py}")

        # Block input to parent until this window is closed
        self.grab_set()
        self.focus_set()
        self.wait_window()

    # ------------------------------------------------------------------ #
    # Config I/O                                                           #
    # ------------------------------------------------------------------ #

    def _load_config(self) -> dict:
        """Return the parsed config dict (empty dict on any error)."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            return {}
        except Exception as exc:
            messagebox.showerror(
                "Settings — Load Error",
                f"Could not read config.json:\n{exc}",
                parent=self,
            )
            return {}

    def _save_config(self, data: dict) -> bool:
        """Write *data* to config.json. Returns True on success."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            return True
        except Exception as exc:
            messagebox.showerror(
                "Settings — Save Error",
                f"Could not write config.json:\n{exc}",
                parent=self,
            )
            return False

    # ------------------------------------------------------------------ #
    # UI construction                                                      #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        """Create all widgets."""
        W = 720

        # ── Header bar ──────────────────────────────────────────────────
        header = tk.Frame(self, bg=self._ACCENT, height=48)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⚙  Settings",
            bg=self._ACCENT,
            fg="white",
            font=("Segoe UI", 13, "bold"),
        ).pack(side=tk.LEFT, padx=18, pady=0)

        # ── Scrollable body wrapper ─────────────────────────────────────
        # (For simplicity in this app, we're not making it actually scrollable 
        # unless it overflows, but we will make it fit well within a normal screen)
        body = tk.Frame(self, bg=self._BG)
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

        # Helper: build one labelled field row with optional Browse button
        self._vars: dict[str, tk.StringVar] = {}
        self._current_row = 0

        def field(
            label: str,
            key: str,
            *,
            browse_type: str | None = None,  # "folder" | "exe" | None
            show: str = "",
            row_span: int = 1
        ) -> None:
            """Create a label + entry (+ optional browse button) at self._current_row."""
            r = self._current_row
            tk.Label(
                body,
                text=label,
                bg=self._BG,
                fg=self._SUBTEXT,
                font=("Segoe UI", 8, "bold"),
                anchor="w",
            ).grid(row=r, column=0, columnspan=3, sticky="w", pady=(12, 2))

            var = tk.StringVar(value=self._config.get(key, ""))
            self._vars[key] = var

            entry = tk.Entry(
                body,
                textvariable=var,
                bg=self._ENTRY_BG,
                fg=self._TEXT,
                insertbackground=self._TEXT,
                relief=tk.FLAT,
                font=("Segoe UI", 9),
                highlightthickness=1,
                highlightbackground=self._BORDER,
                highlightcolor=self._ACCENT,
                show=show,
            )
            entry.grid(
                row=r + 1,
                column=0,
                sticky="ew",
                ipady=6,
                padx=(0, 4 if browse_type else 0),
            )

            if browse_type:
                btn = tk.Button(
                    body,
                    text="Browse…",
                    bg=self._SURFACE,
                    fg=self._TEXT,
                    activebackground=self._ACCENT,
                    activeforeground="white",
                    relief=tk.FLAT,
                    font=("Segoe UI", 8),
                    cursor="hand2",
                    command=lambda bt=browse_type, v=var: self._browse(bt, v),
                )
                btn.grid(row=r + 1, column=1, sticky="ew", ipady=4)

            # Thin divider spacer
            tk.Frame(body, bg=self._BORDER, height=1).grid(
                row=r + 2, column=0, columnspan=3, sticky="ew", pady=(4, 0)
            )
            self._current_row += 3

        field("TEMPLATE FOLDER", "template_folder", browse_type="folder")
        field("OUTPUT FOLDER",   "output_folder",   browse_type="folder")
        field("LIBREOFFICE PATH (soffice.exe)", "libreoffice_path", browse_type="exe")

        # Add fields for all AI Providers
        for p_id in PROVIDER_ORDER:
            p_info = PROVIDERS[p_id]
            label_text = f"{p_info['label'].upper()} API KEY"
            field(label_text, p_info['config_key'], show="•")

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, minsize=90)

        # ── Status label (for test-connection result) ────────────────────
        self._status_var = tk.StringVar(value="")
        self._status_lbl = tk.Label(
            body,
            textvariable=self._status_var,
            bg=self._BG,
            fg=self._SUBTEXT,
            font=("Segoe UI", 8, "italic"),
            anchor="w",
            wraplength=W - 48,
        )
        self._status_lbl.grid(row=self._current_row, column=0, columnspan=2, sticky="w", pady=(14, 0))

        # ── Test Connection Panel ────────────────────────────────────────
        test_panel = tk.Frame(self, bg=self._BG)
        test_panel.pack(fill=tk.X, padx=24, pady=(0, 18))
        
        tk.Label(
            test_panel, 
            text="Test Provider:", 
            bg=self._BG, 
            fg=self._SUBTEXT,
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.test_provider_var = tk.StringVar()
        if PROVIDER_ORDER:
            self.test_provider_var.set(PROVIDER_ORDER[0])
            
        provider_options = {p_id: f"{PROVIDERS[p_id]['emoji']} {PROVIDERS[p_id]['name']}" for p_id in PROVIDER_ORDER}
        
        self.test_combo = ttk.Combobox(
            test_panel, 
            textvariable=self.test_provider_var,
            values=list(PROVIDER_ORDER),
            state="readonly",
            width=15
        )
        self.test_combo.pack(side=tk.LEFT, padx=(0, 10))
        # Format the dropdown items slightly if possible
        
        # Helper to map var to readable name
        def _on_test_btn():
            self._on_test_connection(self.test_provider_var.get())

        tk.Button(
            test_panel,
            text="⚡ Test Connection",
            command=_on_test_btn,
            bg=self._SURFACE,
            fg=self._TEXT,
            activebackground="#3a4560",
            activeforeground="white",
            relief=tk.FLAT,
            font=("Segoe UI", 9),
            cursor="hand2",
            padx=12,
            pady=4,
        ).pack(side=tk.LEFT)

        # ── Button row ───────────────────────────────────────────────────
        btn_row = tk.Frame(self, bg=self._BG)
        btn_row.pack(fill=tk.X, padx=24, pady=(0, 18))

        def mk_btn(parent, text, cmd, *, primary=False):
            bg = self._ACCENT if primary else self._SURFACE
            return tk.Button(
                parent,
                text=text,
                command=cmd,
                bg=bg,
                fg="white",
                activebackground="#6ba3ff" if primary else "#3a4560",
                activeforeground="white",
                relief=tk.FLAT,
                font=("Segoe UI", 9, "bold" if primary else "normal"),
                cursor="hand2",
                padx=16,
                pady=7,
            )

        mk_btn(btn_row, "✓  Save",           self._on_save,    primary=True).pack(side=tk.RIGHT, padx=(6, 0))
        mk_btn(btn_row, "✕  Cancel",          self.destroy                 ).pack(side=tk.RIGHT)

    # ------------------------------------------------------------------ #
    # Browse helpers                                                       #
    # ------------------------------------------------------------------ #

    def _browse(self, browse_type: str, var: tk.StringVar) -> None:
        if browse_type == "folder":
            path = filedialog.askdirectory(
                title="Select Folder",
                parent=self,
            )
        else:  # "exe"
            path = filedialog.askopenfilename(
                title="Select LibreOffice soffice.exe",
                filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
                parent=self,
            )
        if path:
            var.set(path)

    # ------------------------------------------------------------------ #
    # Actions                                                              #
    # ------------------------------------------------------------------ #

    def _on_save(self) -> None:
        """Validate and persist settings to config.json."""
        template_folder = self._vars["template_folder"].get().strip()
        output_folder   = self._vars["output_folder"].get().strip()
        libreoffice     = self._vars["libreoffice_path"].get().strip()

        # Mandatory fields
        errors = []
        if not template_folder:
            errors.append("• Template Folder is required.")
        if not output_folder:
            errors.append("• Output Folder is required.")

        # Check if at least one API key is provided
        has_api_key = any(self._vars[p["config_key"]].get().strip() for p in PROVIDERS.values())
        if not has_api_key:
            errors.append("• At least one AI Provider API Key is required.")

        if errors:
            messagebox.showerror(
                "Settings — Validation",
                "Please fix the following:\n\n" + "\n".join(errors),
                parent=self,
            )
            return

        data = {
            "template_folder": template_folder,
            "output_folder":   output_folder,
            "libreoffice_path": libreoffice,
        }
        # Save all API keys
        for p_id, p_info in PROVIDERS.items():
            data[p_info["config_key"]] = self._vars[p_info["config_key"]].get().strip()
            
        # Keep existing "active_ai" if it exists in current config
        if "active_ai" in self._config:
            data["active_ai"] = self._config["active_ai"]

        if self._save_config(data):
            messagebox.showinfo(
                "Settings — Saved",
                "Settings saved successfully.",
                parent=self,
            )
            self.destroy()

    def _on_test_connection(self, provider_id: str) -> None:
        """Test API connectivity for a specific provider without saving."""
        p_info = PROVIDERS[provider_id]
        api_key = self._vars[p_info["config_key"]].get().strip()
        if not api_key:
            messagebox.showerror(
                "Test Connection",
                f"Please enter your {p_info['name']} API Key before testing.",
                parent=self,
            )
            return

        self._status_var.set(f"⏳  Testing connection to {p_info['name']}…")
        self._status_lbl.config(fg=self._SUBTEXT)
        self.update_idletasks()

        def _run():
            try:
                engine = AIEngine(provider_id, api_key)
                ok, msg = engine.test_connection()
            except Exception as exc:
                ok, msg = False, str(exc)

            def _update():
                if ok:
                    self._status_var.set(f"✅  {msg}")
                    self._status_lbl.config(fg="#4caf7d")
                else:
                    self._status_var.set(f"❌  {msg}")
                    self._status_lbl.config(fg="#e05c5c")

            self.after(0, _update)

        threading.Thread(target=_run, daemon=True).start()
