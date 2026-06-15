# HireMe AI

> **HireMe AI analyzes job circulars to extract your ideal job title, role, and company name, then automatically converts your tailored resume into a PDF.**

A standalone Windows desktop application that uses your choice of AI (**Claude, Gemini, GPT-4o, Grok, or Llama**) to extract job details from a pasted job circular, fill in your resume and CV templates automatically, and export professional PDFs — all with a single click.

---

## Features

| Feature | Details |
|---|---|
| 🤖 AI Extraction | Sends job circular to Claude claude-sonnet-4-5; returns Job Title, Company Name, Role |
| ✏️ Editable Fields | All extracted values are editable before generating PDFs |
| 📄 PDF Generation | LibreOffice headless converts DOCX → PDF automatically |
| 🔒 Safe Editing | Only the exact placeholders are replaced; all other content is untouched |
| ⚙️ Persistent Config | All paths and API key stored in `config.json`; survive app restarts |
| 📦 Standalone EXE | Single `.exe` — no Python needed on the target PC |

---

## Folder Structure

```
JobApplicationAI/
├── main.py              # Tkinter UI
├── ai_engine.py         # Claude API integration
├── doc_editor.py        # DOCX placeholder replacement
├── pdf_converter.py     # LibreOffice headless PDF conversion
├── settings_window.py   # Settings / config window
├── setup_templates.py   # One-time template generator helper
├── config.json          # Runtime configuration (paths + API key)
├── requirements.txt     # Python dependencies
├── build.bat            # One-click PyInstaller build script
├── templates/
│   ├── resume.docx      # Your resume (must contain {{JOB_TITLE}})
│   └── cv.docx          # Your cover letter (must contain {{COMPANY_NAME}} and {{ROLE}})
└── output/              # Generated PDFs land here
```

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **Python 3.10+** | Only needed to build the EXE; not required on the target PC |
| **LibreOffice 7+** | Must be installed on the PC that runs the app |
| **Claude API Key** | Free at [console.anthropic.com](https://console.anthropic.com/) |

---

## Quick Start

### 1. Install Python dependencies

```bash
pip install python-docx anthropic pyinstaller
```

Or install from the requirements file:

```bash
pip install -r requirements.txt
```

### 2. Configure `config.json`

Open `config.json` and set your paths:

```json
{
  "template_folder": "C:\\Users\\Faysal\\Resume",
  "output_folder":   "C:\\Users\\Faysal\\Resume\\output",
  "claude_api_key":  "",
  "libreoffice_path": "C:\\Program Files\\LibreOffice\\program\\soffice.exe"
}
```

> You can also set all values from inside the app via **Settings**.

### 3. Prepare your templates

**Option A — Generate sample templates (recommended for first time)**

```bash
python setup_templates.py
```

This creates `resume.docx` and `cv.docx` in your template folder with the correct placeholders already in place. Open the files and replace the sample content with your real information.

**Option B — Edit your own existing DOCX files**

Add the following placeholders exactly (case-sensitive, including braces):

| File | Placeholder | Purpose |
|---|---|---|
| `resume.docx` | `{{JOB_TITLE}}` | Professional headline / resume title |
| `cv.docx` | `{{COMPANY_NAME}}` | Employer name in the cover letter |
| `cv.docx` | `{{ROLE}}` | Job role in the subject line / body |

> ⚠️ **Important**: Only these exact strings are replaced. All other content — fonts, bold, tables, spacing — is 100% preserved.

### 4. Install LibreOffice

Download from [libreoffice.org](https://www.libreoffice.org/). The app auto-detects the default installation path.

### 5. Run the app (development mode)

```bash
python main.py
```

### 6. Enter your API key

Click **Settings → Claude API Key**, paste your key, then click **Save**.

Use **Test AI Connection** to verify the key works before generating PDFs.

---

## Building the Standalone EXE

### Option A — Double-click build script

Double-click `build.bat`. It will:
1. Install dependencies
2. Clean old build artefacts
3. Run PyInstaller

### Option B — Manual PyInstaller command

```bash
pyinstaller --onefile --windowed --name JobApplicationAI --add-data "config.json;." main.py
```

The finished EXE will be at:

```
dist\JobApplicationAI.exe
```

### Distributing the EXE

Copy these files alongside `JobApplicationAI.exe`:

```
dist/
├── JobApplicationAI.exe   ← the app
└── config.json            ← required — contains paths and API key
```

> `config.json` must sit in the **same folder** as the EXE so the app can read and write settings.

---

## Usage Walkthrough

1. **Launch** `JobApplicationAI.exe`
2. **Paste** the full job circular text into the top text area
3. Click **🔍 Analyze with Claude** — the three fields are filled automatically
4. **Edit** Job Title / Company Name / Role if needed
5. Click **📄 Generate PDFs** — LibreOffice converts and saves to the output folder
6. Click **📁 Open Output Folder** to see your files:
   - `Resume_<CompanyName>.pdf`
   - `CV_<CompanyName>.pdf`

---

## DOCX Placeholder Rules

| Rule | Detail |
|---|---|
| Case-sensitive | `{{JOB_TITLE}}` works; `{{job_title}}` does not |
| Exact match | No spaces inside the braces |
| One occurrence each | Each placeholder should appear once in its template |
| Formatting preserved | The run that contains the placeholder keeps its font, size, and colour after replacement |

---

## Error Reference

| Error | Cause | Fix |
|---|---|---|
| *API Key not set* | `claude_api_key` is empty | Open Settings → enter API key |
| *resume.docx not found* | Template folder path wrong or file missing | Open Settings → check Template Folder |
| *Placeholder not found* | Template doesn't contain `{{JOB_TITLE}}` etc. | Add placeholder to the DOCX |
| *LibreOffice not found* | soffice.exe not installed or path wrong | Install LibreOffice or set path in Settings |
| *Invalid JSON from Claude* | Rare API glitch | Try again; check internet connection |
| *Conversion timed out* | Very large file or hung LibreOffice process | Restart app and try again |

---

## License

MIT — free for personal and commercial use.
