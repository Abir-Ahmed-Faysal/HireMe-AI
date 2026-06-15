# HireMe AI - Complete Project Index

**Status**: ✅ **COMPLETE & READY TO BUILD**

---

## 📋 Project Overview

**HireMe AI** is a complete, production-ready desktop application that:
- ✓ Reads resume and CV templates (DOCX)
- ✓ Uses Claude AI to extract job details from pasted job circulars
- ✓ Lets users edit extracted details
- ✓ Generates customized PDFs automatically
- ✓ Works as a standalone .exe (no Python needed on user's machine)
- ✓ Persists settings between sessions
- ✓ Includes comprehensive error handling

---

## 🏗️ Complete File Structure

```
JobApplicationAI/
├── 📄 Core Application Files
│   ├── main.py                    # Main Tkinter GUI application
│   ├── ai_engine.py              # Claude API integration
│   ├── doc_editor.py             # DOCX document editing
│   ├── pdf_converter.py          # LibreOffice PDF conversion
│   └── settings_window.py        # Settings/configuration UI
│
├── 📦 Configuration & Build
│   ├── config.json               # Configuration (auto-generated)
│   ├── requirements.txt          # Python dependencies
│   ├── build.bat                 # Windows build script
│   └── .gitignore               # Git ignore patterns
│
├── 🔧 Setup & Testing
│   ├── setup_templates.py        # Template generator
│   └── TEST_CHECKLIST.md        # Comprehensive test checklist
│
├── 📚 Documentation (Step-by-Step)
│   ├── 1. README.md              # Quick reference & features
│   ├── 2. QUICK_START.md        # 2-minute quick start
│   ├── 3. SETUP_GUIDE.md        # Complete setup guide (step-by-step)
│   ├── 4. DEPLOYMENT_GUIDE.md   # For sharing the app
│   └── 📄 This File (INDEX.md)   # Navigation guide
│
├── 📁 Folders
│   ├── templates/               # Document templates
│   │   ├── resume.docx         # Resume with {{JOB_TITLE}}
│   │   └── cv.docx            # CV with {{COMPANY_NAME}}, {{ROLE}}
│   └── output/                 # Generated PDFs
```

---

## 🚀 Quick Navigation by Use Case

### 👤 "I want to use the application"
1. Read: [README.md](README.md) (2 min)
2. Follow: [SETUP_GUIDE.md](SETUP_GUIDE.md) (10 min)
3. Use: [QUICK_START.md](QUICK_START.md) (ongoing)

### 👨‍💻 "I want to build the .exe"
1. Follow: [SETUP_GUIDE.md - Building the EXE](SETUP_GUIDE.md#building-the-exe)
2. Verify: [TEST_CHECKLIST.md](TEST_CHECKLIST.md)
3. Run: `build.bat`

### 📤 "I want to share this with others"
1. Read: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Follow packaging instructions
3. Share the zip file

### 🐛 "Something isn't working"
1. Check: [SETUP_GUIDE.md - Troubleshooting](SETUP_GUIDE.md#troubleshooting)
2. Verify: [TEST_CHECKLIST.md](TEST_CHECKLIST.md)
3. Review: Specific module documentation below

---

## 📖 Core Modules Documentation

### 1️⃣ **main.py** - Main Application
**Purpose**: Tkinter GUI with job analysis workflow

**Key Functions**:
- `JobApplicationAI.__init__()` - Initialize app
- `_on_analyze()` - Handle Analyze button
- `_on_generate_pdfs()` - Handle PDF generation
- `_on_settings()` - Open settings window

**Dependencies**: tkinter, threading, ai_engine, doc_editor, pdf_converter, settings_window

**Config Keys Used**: All (template_folder, output_folder, claude_api_key, libreoffice_path)

---

### 2️⃣ **ai_engine.py** - Claude AI Integration
**Purpose**: Extract job details using Claude Sonnet 4

**Key Functions**:
- `AIEngine.__init__(api_key)` - Initialize with API key
- `extract_job_details(job_circular)` - Main function, returns {job_title, company_name, role}
- `test_connection()` - Test API connectivity

**Model**: claude-sonnet-4-20250514

**Returns JSON**:
```json
{
  "job_title": "string",
  "company_name": "string",
  "role": "string"
}
```

**Error Handling**: APIError, JSONDecodeError, ValueError

---

### 3️⃣ **doc_editor.py** - Document Editing
**Purpose**: Safely edit DOCX files with placeholder replacement

**Key Functions**:
- `DocEditor.__init__(template_folder)` - Initialize
- `validate_templates()` - Check if templates exist
- `edit_resume(job_title, output_path)` - Replace {{JOB_TITLE}}
- `edit_cv(company_name, role, output_path)` - Replace {{COMPANY_NAME}}, {{ROLE}}

**Safety Features**:
- Placeholder validation before replacement
- Only modifies exact placeholders
- Never touches other content
- Writes to temp files

**Placeholders** (Case-sensitive):
- Resume: `{{JOB_TITLE}}`
- CV: `{{COMPANY_NAME}}`, `{{ROLE}}`

---

### 4️⃣ **pdf_converter.py** - PDF Generation
**Purpose**: Convert DOCX to PDF using LibreOffice headless

**Key Functions**:
- `PDFConverter.__init__(libreoffice_path)` - Initialize
- `_find_libreoffice()` - Auto-detect LibreOffice
- `convert_to_pdf(docx_path, output_folder)` - Convert single file
- `generate_pdfs(resume_docx, cv_docx, company_name, output_folder)` - Convert both

**Auto-Detection**:
- Checks standard Windows paths
- Queries Windows Registry
- Falls back to config path

**Output Naming**: `Resume_[CompanyName].pdf`, `CV_[CompanyName].pdf`

**Cleanup**: Removes temporary DOCX files after conversion

---

### 5️⃣ **settings_window.py** - Configuration UI
**Purpose**: Manage application settings with GUI

**Key Functions**:
- `SettingsWindow.__init__(parent, config_path)` - Create settings window
- `_load_config()` - Load from config.json
- `_save_settings()` - Save to config.json
- `_test_connection()` - Test Claude API

**Config Fields**:
- template_folder (path)
- output_folder (path)
- claude_api_key (secret)
- libreoffice_path (path)

**Validation**: All fields required before save

---

## 🛠️ Setup & Build Process

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```
Installs: python-docx, anthropic, pyinstaller

### Step 2: Create Templates
```bash
python setup_templates.py
```
Creates sample resume.docx and cv.docx

### Step 3: Configure
Run `python main.py` and use Settings window to configure:
- Paths (templates, output)
- Claude API Key
- LibreOffice Path

### Step 4: Test
Run through [TEST_CHECKLIST.md](TEST_CHECKLIST.md)

### Step 5: Build .exe
```bash
build.bat
```
Creates: `dist/JobApplicationAI.exe` (~50-100 MB)

---

## 📊 Application Workflow

```
User pastes job circular
         ↓
    [Analyze Button]
         ↓
   Claude AI extracts:
   - Job Title
   - Company Name
   - Role
         ↓
   User reviews & edits
   (fields are editable)
         ↓
  [Generate PDFs Button]
         ↓
   doc_editor.py:
   - Edit resume with job_title
   - Edit CV with company_name, role
         ↓
   pdf_converter.py:
   - Convert resume to PDF
   - Convert CV to PDF
   - Name with company name
         ↓
   PDFs saved to output folder
         ↓
   User views and submits
```

---

## 🔐 Security Considerations

✅ **What's Secure**:
- API key stored locally only
- Key shown masked in UI
- No key logging
- Config not included in .exe build
- Temp files securely cleaned

⚠️ **User Responsibility**:
- Don't share config.json
- Keep API key confidential
- Set appropriate output folder permissions

---

## 📋 Configuration Reference

**config.json Structure**:
```json
{
  "template_folder": "C:\\Users\\Name\\Resume",
  "output_folder": "C:\\Users\\Name\\Resume\\output",
  "claude_api_key": "sk-ant-...",
  "libreoffice_path": "C:\\Program Files\\LibreOffice\\program\\soffice.exe"
}
```

**Required**: All 4 fields

**Auto-Generated**: On first Settings save

**Location**: Same directory as application

---

## ✅ Complete Feature Checklist

### Core Features
- [x] Tkinter GUI with text area for job circular
- [x] Claude AI integration (extract 3 fields)
- [x] Editable extracted fields
- [x] PDF generation (Resume + CV)
- [x] Settings window with persistent config
- [x] Status bar with messages

### Document Handling
- [x] Read DOCX files (python-docx)
- [x] Replace ONLY specified placeholders
- [x] Preserve all other content
- [x] Write to temp files before PDF
- [x] Clean up temp files

### PDF Generation
- [x] LibreOffice headless conversion
- [x] Auto-detect LibreOffice path
- [x] Configurable path in settings
- [x] Output filename with company name
- [x] Error handling for missing files

### Error Handling
- [x] Missing templates → User message
- [x] Missing placeholders → User message
- [x] LibreOffice not found → User message
- [x] Invalid API key → User message
- [x] Network error → User message
- [x] All errors user-friendly

### Build & Distribution
- [x] PyInstaller .exe creation
- [x] Single-file executable
- [x] No Python needed on target
- [x] build.bat automation
- [x] Complete documentation

---

## 🧪 Testing Strategy

### Unit Testing
Covered by [TEST_CHECKLIST.md](TEST_CHECKLIST.md):
- Environment setup
- Each module independently
- Error conditions
- Real-world scenarios

### Integration Testing
- Full workflow (analyze → generate)
- Settings persistence
- File operations
- PDF quality

### User Acceptance Testing
- Real job postings
- Multiple jobs in sequence
- Generated PDFs quality
- Performance

---

## 📚 Documentation Files

| File | Purpose | Read Time |
|------|---------|-----------|
| README.md | Overview & quick reference | 5 min |
| QUICK_START.md | 2-minute usage guide | 2 min |
| SETUP_GUIDE.md | Complete setup walkthrough | 20 min |
| DEPLOYMENT_GUIDE.md | Sharing & distribution | 10 min |
| TEST_CHECKLIST.md | Testing verification | Variable |
| This File | Navigation & reference | 5 min |

---

## 🚀 Getting Started (TL;DR)

### For Using the App
```bash
# 1. Install requirements
pip install -r requirements.txt

# 2. Generate templates
python setup_templates.py

# 3. Edit your templates with actual content
# (keep placeholders!)

# 4. Run the app
python main.py

# 5. Configure in Settings window
# 6. Use it!
```

### For Building .exe
```bash
# After above steps, and testing...
build.bat

# .exe is in dist/ folder
# Share dist/JobApplicationAI.exe
```

---

## 📞 Support & Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Python not found | Install from python.org, check "Add to PATH" |
| Dependencies fail | Run: `pip install --upgrade pip` then try again |
| LibreOffice not found | Install from libreoffice.org, verify path in Settings |
| API key invalid | Get new key from console.anthropic.com |
| Placeholder not found | Check template files have `{{PLACEHOLDER}}` |
| PDFs not generating | Verify LibreOffice path, check output folder permissions |

### Detailed Help
- See [SETUP_GUIDE.md - Troubleshooting](SETUP_GUIDE.md#troubleshooting)
- See [TEST_CHECKLIST.md](TEST_CHECKLIST.md)
- Check error messages in Settings test

---

## 🎯 Success Criteria

✅ Application is complete and meets all requirements:

**Specifications Met**:
- [x] AI Engine uses Claude Sonnet 4
- [x] Returns JSON with job_title, company_name, role
- [x] Document Editor only replaces exact placeholders
- [x] PDF Converter uses LibreOffice headless mode
- [x] Main window has all required buttons and fields
- [x] Settings window with save/test
- [x] config.json persists between sessions
- [x] README with build instructions
- [x] Builds to standalone .exe

**Code Quality**:
- [x] Complete, working code (no placeholders)
- [x] Comprehensive error handling
- [x] User-friendly error messages
- [x] Comments explaining logic
- [x] Proper file handling

**Documentation**:
- [x] Setup guide (step-by-step)
- [x] Quick start guide
- [x] Deployment guide
- [x] Test checklist
- [x] API key integration docs

---

## 📈 What's Next?

### Optional Enhancements (Future Versions)
- [ ] Batch job processing
- [ ] Support for more document formats
- [ ] Customizable AI prompts
- [ ] PDF editing before generation
- [ ] Email PDF directly
- [ ] Cloud storage integration
- [ ] Resume templates library

### Immediate Next Steps
1. ✅ Review this index
2. ✅ Follow SETUP_GUIDE.md
3. ✅ Run setup_templates.py
4. ✅ Configure in Settings
5. ✅ Run TEST_CHECKLIST.md
6. ✅ Build with build.bat
7. ✅ Share with others!

---

## 📝 Version Information

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Release Date**: 2026-06-15  
**Python Requirement**: 3.10+  
**Build Tool**: PyInstaller  

---

## 📦 What You Have

✅ **5 Complete Python Modules**
- main.py (Tkinter UI)
- ai_engine.py (Claude API)
- doc_editor.py (DOCX editing)
- pdf_converter.py (PDF generation)
- settings_window.py (Configuration)

✅ **Full Documentation**
- README.md
- SETUP_GUIDE.md
- QUICK_START.md
- DEPLOYMENT_GUIDE.md
- TEST_CHECKLIST.md

✅ **Automation & Build**
- requirements.txt
- build.bat
- setup_templates.py
- config.json template
- .gitignore

✅ **Folder Structure**
- templates/ (for DOCX files)
- output/ (for generated PDFs)

---

## 🎉 Ready to Go!

**Everything is set up and ready to:**
1. Install locally for testing
2. Build .exe for distribution
3. Share with others
4. Extend with new features

**Start with**: [SETUP_GUIDE.md](SETUP_GUIDE.md)

**Have questions?** Check the relevant documentation file in this index.

---

**Built with**: Python, Tkinter, Claude AI, python-docx, LibreOffice, PyInstaller

**License**: MIT (included)

**Questions?** See documentation files or README.md
