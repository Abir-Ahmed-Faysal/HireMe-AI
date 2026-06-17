# 🎯 HireMe AI - Smart Job Application Assistant

> **Paste a job circular → Get your custom resume & CV PDFs in seconds with AI-powered extraction**

HireMe AI is a **Windows desktop application** that automates job application workflow. It uses AI to analyze job circulars, intelligently extracts job details (title, company, role, skills), fills your resume/CV templates with relevant information, and generates professional PDFs—all with one click.

**No more manual copy-pasting. No more generic applications. Just smart, personalized job applications.**

---

## 🌟 Key Features

| Feature | What It Does |
|---------|-------------|
| 🤖 **Smart AI Extraction** | Analyzes job circulars and extracts: Job Title, Company Name, Role, Location, Tech Stack, Skills |
| 🔄 **Multi-Provider AI** | Choose from Claude, Gemini, GPT-4o, Grok, or Llama — use any provider with your API key |
| 🛠️ **Skills Detection** | AI identifies technical skills from job circular; you manually select which ones to add to your resume |
| ✏️ **Editable Fields** | All extracted values are fully editable before PDF generation |
| 📄 **Automatic PDF Generation** | LibreOffice headless conversion: DOCX → PDF instantly |
| 🔒 **Template Safety** | Only placeholders are replaced; formatting, fonts, styles 100% preserved |
| 📁 **Timestamped Organization** | Each application saved in unique folders with millisecond precision: `Company_Role_YYYY-MM-DD_HH-MM-SS-mmm` |
| 🎯 **Smart Role Cleaning** | Removes seniority qualifiers (Senior/Junior/Intern) from filenames for clean, professional organization |
| ⚙️ **Persistent Config** | All settings (paths, API keys) stored in `config.json` — survive app restarts |
| 💾 **Autosave & Recovery** | Automatically saves draft every 30 seconds and recovers if closed accidentally |
| 🕒 **Job History** | Keeps history of the last 20 analyzed jobs for quick reloading |
| 📝 **Comprehensive Logging** | Application activity logged for easy auditing and debugging |
| 📦 **Standalone EXE** | Single executable — no Python required on user's PC |
| 🌍 **Multi-language** | Handles job circulars in English, Bengali, or any language with AI translation

---

## 📋 Table of Contents

- [What You Need](#what-you-need)
- [Installation](#installation)
- [First-Time Setup](#first-time-setup)
- [How to Use](#how-to-use)
- [How It Works](#how-it-works)
- [File Organization](#file-organization)
- [Configuration](#configuration)
- [API Providers](#api-providers)
- [Building EXE](#building-standalone-exe)
- [Template Requirements](#template-requirements)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

---

## 🔧 What You Need

### **Minimum Requirements**

| Requirement | Version | Notes |
|---|---|---|
| **Windows OS** | 7 or later | Linux/Mac not currently supported |
| **LibreOffice** | 7.0+ | For PDF conversion ([download](https://www.libreoffice.org/)) |
| **API Key** | Any provider | Claude (recommended), Gemini, GPT-4o, Grok, or Llama |

### **To Develop / Modify Code**

| Requirement | Version | Notes |
|---|---|---|
| **Python** | 3.10+ | Only needed if building from source |
| **pip** | Latest | Package manager (comes with Python) |

### **To Build Standalone EXE**

| Requirement | Notes |
|---|---|
| **PyInstaller** | Included in requirements.txt |
| **build.bat** | One-click build script (included) |

---

## 📥 Installation

### **Option A: Use Pre-Built EXE (Easiest)**

1. Download `HireMe_AI.exe` from the releases page
2. Copy `config.json` to the same folder
3. Double-click `HireMe_AI.exe`
4. Add your API key in Settings

### **Option B: Run from Source (for Development)**

#### **Step 1: Clone or Download**
```bash
git clone https://github.com/yourusername/JobApplicationAI.git
cd JobApplicationAI
```

#### **Step 2: Install Python Dependencies**
```bash
pip install -r requirements.txt
```

This installs:
- `python-docx` — for editing Word documents
- `anthropic` — for Claude API
- `httpx` — for OpenAI-compatible REST calls
- `pyinstaller` — for building EXE

#### **Step 3: Verify LibreOffice Installation**

Check if LibreOffice is installed:
```bash
# Windows - check default path
dir "C:\Program Files\LibreOffice\program\soffice.exe"
```

If not found, [download LibreOffice](https://www.libreoffice.org/) and install it.

#### **Step 4: Run the App**
```bash
python main.py
```

---

## ⚙️ First-Time Setup

### **1. Launch the App**

**From source:**
```bash
python main.py
```

**From EXE:**
Double-click `HireMe_AI.exe`

### **2. Generate Template Files**

Click **Settings** → **Generate Sample Templates**

This creates:
- `resume.docx` with placeholder `{{JOB_TITLE}}`
- `cv.docx` with placeholders `{{COMPANY_NAME}}`, `{{ROLE}}`, `{{LOCATION}}`

**Or use command line:**
```bash
python setup_templates.py
```

### **3. Edit Your Templates**

Open the generated DOCX files and:
1. Replace sample content with **your real resume/CV content**
2. **Keep all placeholders** (they'll be replaced automatically)
3. Save and close

**Example resume.docx:**
```
────────────────────────────────
FAYSAL AHMED
your.email@example.com | +1234567890

PROFESSIONAL HEADLINE
{{JOB_TITLE}}                    ← Keep this

EXPERIENCE
[Your experience here...]

SKILLS
[Your skills here...]
────────────────────────────────
```

### **4. Configure Settings**

Click **Settings** and enter:

| Setting | Example | Notes |
|---------|---------|-------|
| **Template Folder** | `C:\Users\YourName\Resume` | Where resume.docx & cv.docx are |
| **Output Folder** | `C:\Users\YourName\Resume\output` | Where PDFs will be saved |
| **Active AI Provider** | Claude (recommended) | Dropdown to choose provider |
| **API Key** | (your key) | Get from provider's console |

**Optional: Test API Connection**
Click **Test AI Connection** to verify your API key works.

### **5. You're Ready!**

Close Settings. The app is now configured.

---

## 🚀 How to Use

### **Step-by-Step Workflow**

```
1. Find a job you want to apply for
   ↓
2. Copy the entire job circular (posting text)
   ↓
3. Launch HireMe AI
   ↓
4. Paste job circular into the text area
   ↓
5. Click "🔍 Analyze with AI"
   ↓
6. Review extracted details (editable)
   ↓
7. Review missing skills (select which to add)
   ↓
8. Click "📄 Generate PDFs"
   ↓
9. Your customized PDFs are ready!
   ↓
10. Click "📁 Open Output Folder" to access them
```

### **Detailed Steps**

#### **Step 1: Paste Job Circular**

```
Job Circular Example:
───────────────────
Company: TechCorp Inc.
Position: Senior Backend Developer
Location: New York, USA

We are looking for an experienced Senior Backend Developer...
Requirements:
- 5+ years of experience
- Node.js, Express, MongoDB
- Docker, Kubernetes
- AWS or GCP
...
───────────────────
```

Copy everything and paste into the app's text area.

#### **Step 2: Click "Analyze with AI"**

The AI will extract:
- **Job Title**: Full job title (e.g., "Senior Backend Developer")
- **Company Name**: Employer name
- **Role**: Position (e.g., "Backend Developer")
- **Location**: Where the job is
- **Tech Stack**: Key technologies required

**Plus:** AI identifies all technical skills mentioned

#### **Step 3: Review & Edit (Optional)**

All fields are editable. You can:
- Change "Senior Backend Developer" → "Backend Developer" (if you prefer)
- Fix company name if AI misread it
- Add missing details

#### **Step 4: Select Skills to Add**

See a section: **"🔧 Skills to Add (Optional)"**

- Shows skills from job that aren't in your current resume
- **Checkboxes** let you manually select which ones to add
- Only skills YOU check will be added (safe, honest approach)

✅ Example:
```
☑ Docker       ← I have this skill
☐ Kubernetes   ← I don't have this
☑ MongoDB      ← I have this
```

#### **Step 5: Click "Generate PDFs"**

The app will:
1. Create temporary copies of your resume & CV
2. Replace placeholders with extracted job details
3. Add selected skills to your resume
4. Convert DOCX → PDF via LibreOffice
5. Save with clean filenames
6. Show success message

#### **Step 6: Access Your PDFs**

Click **"📁 Open Output Folder"** to see your files:

```
output/
└── TechCorp_Backend_Developer_2026-06-17_14-30-05-123/
    ├── Faysal_Ahmed_Resume_Backend_Developer.pdf
    └── Faysal_Ahmed's_CoverLetter_Backend_Developer.pdf
```

---

## 🏗️ How It Works

### **System Architecture**

```
┌─────────────────────────────────────────────────────┐
│         HireMe AI Application                       │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ Tkinter GUI (main.py)                        │  │
│  │  • User interface with dark theme            │  │
│  │  • Text area for job circular paste          │  │
│  │  • Edit fields for extracted data            │  │
│  │  • Skills checkboxes                         │  │
│  │  • Settings dialog                           │  │
│  └──────────────────────────────────────────────┘  │
│           ↕                                         │
│  ┌──────────────────────────────────────────────┐  │
│  │ AI Engine (ai_engine.py)                     │  │
│  │  • Sends job circular to Claude/Gemini/etc   │  │
│  │  • Extracts: title, company, role, skills   │  │
│  │  • Parses JSON response                      │  │
│  │  • Multi-provider support                    │  │
│  └──────────────────────────────────────────────┘  │
│           ↕                                         │
│  ┌──────────────────────────────────────────────┐  │
│  │ Doc Editor (doc_editor.py)                   │  │
│  │  • Reads resume.docx & cv.docx templates     │  │
│  │  • Replaces {{JOB_TITLE}}, {{ROLE}}, etc    │  │
│  │  • Extracts existing skills from resume      │  │
│  │  • Adds selected skills                      │  │
│  │  • Preserves all formatting                  │  │
│  └──────────────────────────────────────────────┘  │
│           ↕                                         │
│  ┌──────────────────────────────────────────────┐  │
│  │ PDF Converter (pdf_converter.py)              │  │
│  │  • Calls LibreOffice headless                │  │
│  │  • Converts DOCX → PDF                       │  │
│  │  • Cleans role names (removes Senior/Junior) │  │
│  │  • Generates timestamped folders             │  │
│  │  • Creates professional filenames            │  │
│  └──────────────────────────────────────────────┘  │
│           ↕                                         │
│  ┌──────────────────────────────────────────────┐  │
│  │ File System                                  │  │
│  │  └─ output/                                  │  │
│  │      └─ CompanyName_Role_Timestamp/          │  │
│  │          ├─ Resume_Role.pdf                  │  │
│  │          └─ CoverLetter_Role.pdf             │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘

        ↓ config.json (settings)
        • Template folder path
        • Output folder path
        • API keys for all providers
        • LibreOffice path
```

### **Data Flow**

```
Job Circular Text
       ↓
    [AI Engine]
    Claude API
       ↓
  JSON Response
  {
    "job_title": "Senior Backend Developer",
    "company_name": "TechCorp",
    "role": "Backend Developer",
    "location": "New York",
    "tech_stack": "Node.js · MongoDB · Docker",
    "skills": ["Node.js", "MongoDB", "Docker", "AWS", ...]
  }
       ↓
  [User Edits Fields]
  [Selects Skills]
       ↓
  [Doc Editor]
  • Read resume.docx
  • Replace {{JOB_TITLE}} → "Backend Developer"
  • Replace {{COMPANY_NAME}} → "TechCorp"
  • Add selected skills
  • Save temporary copy
       ↓
  [PDF Converter]
  • LibreOffice converts DOCX → PDF
  • Cleans role names
  • Renames files professionally
  • Creates timestamp folder
       ↓
  Final PDFs
  ├── Faysal_Ahmed_Resume_Backend_Developer.pdf
  └── Faysal_Ahmed's_CoverLetter_Backend_Developer.pdf
```

---

## 📁 File Organization

### **Folder Structure**

```
JobApplicationAI/
│
├── 📄 main.py                    # Main application (Tkinter GUI)
├── 📄 ai_engine.py               # AI integration (Claude/Gemini/etc)
├── 📄 doc_editor.py              # DOCX template editing
├── 📄 pdf_converter.py           # LibreOffice PDF conversion
├── 📄 settings_window.py         # Settings dialog
├── 📄 setup_templates.py         # Generate sample templates
├── 📄 history_manager.py         # Auto-save and history tracking
├── 📄 logger_manager.py          # Application logging
│
├── 📋 config.json                # Configuration (paths, API keys)
├── 📋 .history.json              # Saved job analysis history
├── 📋 .draft.json                # Temporary autosave draft
├── 📁 app_logs/                  # Timestamped application logs
├── 📋 requirements.txt           # Python dependencies
├── 📋 README.md                  # This file
├── 🎨 HireMe_AI.spec             # PyInstaller config
├── 🔨 build.bat                  # Build script (one-click EXE)
│
├── 📁 templates/
│   ├── resume.docx               # Your resume template
│   ├── cv.docx                   # Your cover letter template
│   └── demo cv and resume/       # Examples (optional)
│
└── 📁 output/
    ├── TechCorp_Backend_Developer_2026-06-17_14-30-05-123/
    │   ├── Faysal_Ahmed_Resume_Backend_Developer.pdf
    │   └── Faysal_Ahmed's_CoverLetter_Backend_Developer.pdf
    │
    └── Google_Frontend_Developer_2026-06-17_14-31-12-456/
        ├── Faysal_Ahmed_Resume_Frontend_Developer.pdf
        └── Faysal_Ahmed's_CoverLetter_Frontend_Developer.pdf
```

### **File Naming Convention**

All generated PDFs follow this pattern:

```
Faysal_Ahmed_Resume_{CleanRole}.pdf
Faysal_Ahmed's_CoverLetter_{CleanRole}.pdf
```

**Where {CleanRole} is the job role with:**
- ✅ Seniority qualifiers removed (Senior, Junior, Intern removed)
- ✅ Spaces replaced with underscores
- ✅ Special characters removed

**Examples:**
```
Job: "Senior Backend Developer"
  → Faysal_Ahmed_Resume_Backend_Developer.pdf
  
Job: "Junior React Developer"
  → Faysal_Ahmed_Resume_React_Developer.pdf
  
Job: "Lead Full Stack Engineer"
  → Faysal_Ahmed_Resume_Full_Stack_Engineer.pdf
```

---

## ⚙️ Configuration

### **config.json Structure**

```json
{
  "template_folder": "C:\\Users\\YourName\\Resume",
  "output_folder": "C:\\Users\\YourName\\Resume\\output",
  "claude_api_key": "sk-ant-xxxxx",
  "gemini_api_key": "",
  "openai_api_key": "",
  "grok_api_key": "",
  "groq_api_key": "",
  "active_ai": "claude",
  "libreoffice_path": "C:\\Program Files\\LibreOffice\\program\\soffice.exe"
}
```

### **Configuration Options**

| Setting | Type | Example | Notes |
|---------|------|---------|-------|
| `template_folder` | String | `C:\Users\Faysal\Resume` | Folder containing resume.docx & cv.docx |
| `output_folder` | String | `C:\Users\Faysal\Resume\output` | Where PDFs are saved |
| `active_ai` | String | `claude` | Which provider to use (claude, gemini, gpt, grok, llama) |
| `claude_api_key` | String | `sk-ant-xxxxx` | Claude API key from Anthropic |
| `gemini_api_key` | String | `xxxxx` | Gemini API key from Google |
| `openai_api_key` | String | `sk-xxxxx` | OpenAI API key |
| `grok_api_key` | String | `xxxxx` | Grok API key from xAI |
| `groq_api_key` | String | `xxxxx` | Groq API key |
| `libreoffice_path` | String | Default auto-detected | Path to soffice.exe |

### **Setting Config from App**

1. Click **Settings**
2. Update any value
3. Click **Save**
4. Changes are written to `config.json` automatically

---

## 🤖 API Providers

### **Supported Providers**

You can use ANY of these AI providers:

| Provider | Model | Cost | Speed | Quality |
|----------|-------|------|-------|---------|
| **Claude (Recommended)** | claude-sonnet-4-5 | ~$0.003/call | Fast | Excellent |
| **Gemini** | gemini-2.0-flash | ~$0.0001/call | Fastest | Good |
| **GPT-4o** | gpt-4o-mini | ~$0.00015/call | Fast | Excellent |
| **Grok** | grok-3-mini | Cheap | Fast | Good |
| **Llama** | llama-3.3-70b | Cheap | Medium | Very Good |

### **Getting API Keys**

#### **Claude (Anthropic)**
1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up (free)
3. Click **API Keys**
4. Create new key
5. Copy and paste into app settings

#### **Gemini (Google)**
1. Go to [ai.google.dev](https://ai.google.dev/)
2. Click **Get API Key**
3. Create new project
4. Copy key

#### **GPT-4o (OpenAI)**
1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. **API Keys** → Create new key
4. Copy and paste

#### **Grok (xAI)**
1. Go to [x.ai/api](https://x.ai/api/)
2. Get API key
3. Copy and paste

#### **Llama (Groq)**
1. Go to [console.groq.com](https://console.groq.com/)
2. Get API key
3. Copy and paste

### **Switching Providers**

Click **Settings** → **Active AI Provider** → Select from dropdown

---

## 🔨 Building Standalone EXE

### **Option 1: One-Click Build (Easiest)**

```bash
build.bat
```

This script will:
1. Check Python version
2. Install dependencies
3. Clean old builds
4. Run PyInstaller
5. Create `dist\HireMe_AI.exe`

### **Option 2: Manual Build**

```bash
pyinstaller --onefile --windowed --name HireMe_AI --icon=icon.ico main.py
```

### **Distribution Package**

To share the app, copy:

```
dist/
├── HireMe_AI.exe          ← The application
└── config.json            ← Configuration file (REQUIRED)
```

> ⚠️ `config.json` MUST be in the same folder as the EXE

User receives both files and can run immediately.

---

## 📝 Template Requirements

### **Resume Template (resume.docx)**

**MUST contain:**
- Placeholder: `{{JOB_TITLE}}`

**Optional:**
- Placeholder: `{{SKILLS}}` (for auto-added skills)
- SKILLS section with existing skills (for detection)

**Content suggestion:**
```
[HEADER]
Your Name
Your Email | Your Phone

[PROFESSIONAL HEADLINE]
{{JOB_TITLE}}

[EXPERIENCE]
[Your work history]

[EDUCATION]
[Your education]

[SKILLS]
[Your existing skills]

[PROJECTS]
[Your projects]
```

### **CV Template (cv.docx)**

**MUST contain:**
- Placeholder: `{{COMPANY_NAME}}`
- Placeholder: `{{ROLE}}`

**Optional:**
- Placeholder: `{{LOCATION}}`
- Placeholder: `{{DATE}}`
- Placeholder: `{{JOB_TITLE}}` (for header)

**Content suggestion:**
```
[DATE]
{{DATE}}

[TO]
Dear Hiring Manager,

[BODY]
I am interested in the {{ROLE}} position at {{COMPANY_NAME}}...

[LOCATION MENTION]
{{LOCATION}}

[CLOSING]
Sincerely,
Your Name
```

### **Placeholder Rules**

| Rule | Details |
|------|---------|
| **Case-Sensitive** | `{{JOB_TITLE}}` works; `{{job_title}}` doesn't |
| **Exact Match** | No spaces: `{{ JOB_TITLE }}` won't work |
| **Formatting Preserved** | Bold/italic/font of placeholder run is kept |
| **Can Split Across Runs** | If placeholder splits across runs, app handles it |
| **One Per Template** | Each placeholder should appear once (or more if you want all occurrences replaced) |

---

## 🐛 Troubleshooting

### **"API Key not set" Error**

**Cause:** You haven't entered an API key

**Fix:**
1. Click Settings
2. Select your AI provider
3. Paste API key
4. Click "Test AI Connection"
5. If success, click Save

### **"resume.docx not found" Error**

**Cause:** Template folder path wrong or file missing

**Fix:**
1. Click Settings
2. Check **Template Folder** path
3. Verify folder contains `resume.docx` and `cv.docx`
4. Use file browser button to select folder
5. Click Save

### **"{{JOB_TITLE}} not found" Error**

**Cause:** Placeholder is missing from template

**Fix:**
1. Open resume.docx
2. Find the job title line
3. Add `{{JOB_TITLE}}` exactly (copy-paste from error message)
4. Save file
5. Try again

### **"LibreOffice not found" Error**

**Cause:** LibreOffice not installed or path wrong

**Fix:**
1. Download [LibreOffice](https://www.libreoffice.org/) and install
2. If already installed, click Settings
3. Click **Browse** next to "LibreOffice Path"
4. Navigate to: `C:\Program Files\LibreOffice\program\soffice.exe`
5. Click Save

### **"Invalid JSON from Claude" Error**

**Cause:** AI returned unexpected format (rare)

**Fix:**
1. Check your internet connection
2. Verify API key works (use Test AI Connection)
3. Try again
4. If persists, switch to different AI provider

### **"Conversion timed out" Error**

**Cause:** LibreOffice taking too long (very large file)

**Fix:**
1. Restart the app
2. Try PDF generation again
3. If persistent, simplify DOCX (remove images, etc.)

### **App starts but shows blank window**

**Cause:** GUI initialization issue (rare)

**Fix:**
```bash
python main.py  # Run from terminal to see error messages
```

Look at error output to debug.

### **Filenames show strange characters**

**Cause:** Company or role name has special characters

**Fix:**
The app automatically removes special characters. This is normal behavior.

---

## 📚 Examples

### **Example 1: Full Workflow**

**Job Circular (you paste this):**
```
Company: TechCorp Inc.
Position: Senior Full Stack Developer
Location: San Francisco, CA

Requirements:
- 5+ years experience
- React, Node.js, MongoDB, Docker
- AWS, CI/CD pipelines
- Team leadership
```

**What App Extracts:**
- Job Title: `Senior Full Stack Developer`
- Company: `TechCorp`
- Role: `Full Stack Developer` (cleaned)
- Tech Stack: `React · Node.js · MongoDB · Docker`
- Skills: `[React, Node.js, MongoDB, Docker, AWS, CI/CD]`

**Files Generated:**
```
TechCorp_Full_Stack_Developer_2026-06-17_14-30-05-123/
├── Faysal_Ahmed_Resume_Full_Stack_Developer.pdf
└── Faysal_Ahmed's_CoverLetter_Full_Stack_Developer.pdf
```

**Resume Content:**
```
PROFESSIONAL HEADLINE
Full Stack Developer  ← (cleaned, without "Senior")

[Body shows full position]
Senior Full Stack Developer position at TechCorp Inc.
```

---

### **Example 2: Skills Selection**

**AI Found These Skills:**
- React
- Node.js
- MongoDB
- Docker
- AWS
- Jenkins

**Existing Skills in Your Resume:**
- React
- Node.js
- JavaScript
- SQL

**Skills UI Shows (Only Missing Ones):**
```
☐ MongoDB    ← Not in your resume
☑ Docker     ← I'm checking this (I have it)
☑ AWS        ← I'm checking this (I have it)
☐ Jenkins    ← I don't have this
```

**Added to Resume:**
```
Docker · AWS
```

---

### **Example 3: Role Cleaning**

| Job Circular Role | Filename Role | Reason |
|---|---|---|
| Senior Backend Developer | Backend Developer | "Senior" removed |
| Junior React Developer | React Developer | "Junior" removed |
| Intern DevOps Engineer | DevOps Engineer | "Intern" removed |
| Lead Full Stack Engineer | Full Stack Engineer | "Lead" removed |
| Principal Software Architect | Software Architect | "Principal" removed |

---

## 📄 Files Reference

### **Core Application Files**

| File | Purpose | What It Does |
|------|---------|-------------|
| `main.py` | **GUI Application** | Tkinter interface, coordinates workflow |
| `ai_engine.py` | **AI Integration** | Calls Claude/Gemini/GPT/Grok/Llama, parses responses |
| `doc_editor.py` | **Document Editing** | Reads/edits DOCX, replaces placeholders, adds skills |
| `pdf_converter.py` | **PDF Generation** | Calls LibreOffice, converts DOCX→PDF, renames files |
| `settings_window.py` | **Settings Dialog** | Config UI, saves to config.json |
| `setup_templates.py` | **Template Generator** | Creates sample resume.docx & cv.docx |
| `history_manager.py` | **History & Drafts** | Auto-saves form data, recovers drafts, tracks job history |
| `logger_manager.py` | **Logging System** | Writes application events to log files for debugging |

### **Configuration & Build**

| File | Purpose |
|------|---------|
| `config.json` | Settings (paths, API keys) |
| `requirements.txt` | Python dependencies |
| `build.bat` | One-click EXE builder |
| `HireMe_AI.spec` | PyInstaller configuration |

---

## 🎓 Tips & Best Practices

### **For Best Results**

1. **Customize Templates**
   - Edit resume.docx with YOUR actual content
   - Don't leave placeholder text in output PDF

2. **Keep Placeholders**
   - Don't remove `{{JOB_TITLE}}` etc. from templates
   - They're replaced automatically each time

3. **One-Line Job Circulars**
   - Full job posting text works best
   - Not just job title

4. **Test API Connection**
   - Before generating first PDF
   - Click Settings → Test AI Connection

5. **Review Before Submitting**
   - Always check generated PDF
   - Ensure formatting looks correct
   - Verify all details are accurate

6. **Keep Output Organized**
   - Timestamped folders help track applications
   - Easy to find old PDFs by company/date

### **Speeding Up**

- Use Gemini (fastest) instead of Claude
- Pre-write templates with your info
- Reuse edits if applying to similar roles

### **Cost Optimization**

- Claude costs ~$0.003 per job analysis
- Gemini ~$0.0001 per analysis (200x cheaper!)
- Llama very cheap, good quality

---

## 📧 Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Verify LibreOffice is installed
3. Check API key is valid
4. Run from terminal to see error messages
5. Review `config.json` for wrong paths

---

## 📜 License

MIT License — Free for personal and commercial use.

---

## 🙏 Credits

Built with:
- **Tkinter** - GUI
- **python-docx** - Word document editing
- **Anthropic Claude** - AI extraction
- **LibreOffice** - PDF conversion

---

**Made with ❤️ for smarter job applications**
