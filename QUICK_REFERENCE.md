# HireMe AI - Quick Reference Card

Print this card or bookmark it for quick access!

---

## 🚀 Installation (First Time Only)

```bash
# 1. Navigate to project folder
cd C:\WorkSpace\Pdf_updater\JobApplicationAI

# 2. Install dependencies (once)
pip install -r requirements.txt

# 3. Generate templates (once)
python setup_templates.py

# 4. Edit templates with YOUR content
# Keep: {{JOB_TITLE}}, {{COMPANY_NAME}}, {{ROLE}}

# 5. Run application
python main.py
```

---

## ⚙️ First Configuration (First Run Only)

1. Click **Settings** button
2. Fill all fields:
   - **Template Folder**: Path to your templates
   - **Output Folder**: Where to save PDFs
   - **LibreOffice Path**: `C:\Program Files\LibreOffice\program\soffice.exe`
   - **Claude API Key**: Get from console.anthropic.com
3. Click **Test AI Connection** → Should show success
4. Click **Save**

---

## 💻 Building .exe (Once Per Version)

```bash
# Clean previous build
rmdir /s /q dist build
del *.spec

# Build
build.bat

# Result: dist/JobApplicationAI.exe (~50-100 MB)
```

---

## 📖 Using the Application (Every Job)

1. **Copy job posting** from website
2. **Paste** into text area
3. Click **Analyze Job Circular**
4. **Review** 3 fields (or edit if needed)
5. Click **Generate PDFs**
6. Done! PDFs are in Output Folder

**Total time**: ~1-2 minutes per job

---

## 📁 File Locations

| Item | Location |
|------|----------|
| Resume Template | `templates/resume.docx` |
| CV Template | `templates/cv.docx` |
| Generated PDFs | Output folder (set in Settings) |
| Configuration | `config.json` |
| Settings | Click Settings button in app |

---

## 🔑 API Key Setup

1. Go to: https://console.anthropic.com/
2. Sign up or login
3. Create API key (starts with `sk-ant-`)
4. Copy the key
5. Paste in Settings → Claude API Key
6. Click Test → Success!

---

## ⚠️ Common Issues

| Problem | Fix |
|---------|-----|
| "Python not found" | Install from python.org, check "Add to PATH" |
| "LibreOffice not found" | Install from libreoffice.org, verify path in Settings |
| "Invalid API Key" | Get new key from console.anthropic.com |
| "Template not found" | Run `python setup_templates.py` |
| "Placeholder not found" | Check templates have `{{PLACEHOLDER}}` |

---

## 📋 Folder Structure

```
JobApplicationAI/
├── main.py                  ← Run this
├── config.json              ← Auto-created
├── templates/
│   ├── resume.docx         ← Edit with YOUR content
│   └── cv.docx             ← Edit with YOUR content
└── output/                 ← PDF files appear here
```

---

## 🔗 Quick Links

- **Setup**: See SETUP_GUIDE.md (20 min walkthrough)
- **Usage**: See QUICK_START.md (2 min guide)
- **Deploy**: See DEPLOYMENT_GUIDE.md
- **Index**: See INDEX.md (complete navigation)
- **Testing**: See TEST_CHECKLIST.md
- **Overview**: See README.md

---

## 💡 Tips

✓ Always keep placeholders in templates: `{{JOB_TITLE}}`, `{{COMPANY_NAME}}`, `{{ROLE}}`

✓ AI fields are editable - adjust if needed

✓ PDF filenames include company name for organization

✓ Settings persist between sessions (in config.json)

✓ Use "Open Output Folder" button to see generated PDFs

---

## 🎯 Workflow Summary

```
START
  ↓
Paste job posting
  ↓
Click "Analyze"
  ↓
Review 3 fields
  (optional: edit)
  ↓
Click "Generate PDFs"
  ↓
Check output folder
  ↓
Submit PDFs!
  ↓
END (Repeat for next job)
```

---

## 📱 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+A` | Select all text in text area |
| `Ctrl+V` | Paste job posting |
| `Ctrl+Z` | Undo in fields |
| `Tab` | Move to next field |

---

## ✅ Pre-Launch Checklist

Before using:
- [ ] Python installed (`python --version` works)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] LibreOffice installed
- [ ] Templates created and edited
- [ ] Claude API key obtained
- [ ] Settings configured
- [ ] Test connection successful

---

## 🆘 Getting Help

1. Check relevant documentation file
   - Setup issues → SETUP_GUIDE.md
   - Usage issues → QUICK_START.md
   - Build issues → build.bat or INDEX.md

2. Run TEST_CHECKLIST.md to verify setup

3. Check error messages in Settings "Test AI Connection"

---

## 📞 Configuration Reference

**config.json locations:**
- Dev: `JobApplicationAI/config.json`
- Built: Next to `JobApplicationAI.exe`

**What's in config.json:**
```json
{
  "template_folder": "C:\\...",
  "output_folder": "C:\\...",
  "claude_api_key": "sk-ant-...",
  "libreoffice_path": "C:\\...\soffice.exe"
}
```

⚠️ Never share config.json (has API key!)

---

## 🔄 Build Workflow

```
Source Code (main.py, etc)
     ↓
python setup_templates.py
(Create templates)
     ↓
Test with: python main.py
(Verify everything works)
     ↓
build.bat
(Create .exe)
     ↓
dist/JobApplicationAI.exe
(Ready to use/share!)
```

---

## 📦 Sharing the Application

To share with others:

1. Build: `build.bat`
2. Create zip with:
   - `dist/JobApplicationAI.exe`
   - `templates/` (with your templates)
   - `README.md`
   - `QUICK_START.md`
3. Share zip file
4. Recipients:
   - Install LibreOffice
   - Extract zip
   - Run .exe
   - Configure in Settings

---

## 🎮 Example: Using the App

```
Job posting found on LinkedIn
↓
Copy entire job description
↓
Open JobApplicationAI.exe
↓
Paste into text area
↓
Click "Analyze Job Circular"
↓
Wait 5-10 seconds...
↓
Fields populated:
  Job Title: Full Stack Developer
  Company Name: TechCorp Inc
  Role: Senior Engineer
↓
Review (looks good!)
↓
Click "Generate PDFs"
↓
Wait 20-30 seconds...
↓
Success message shows
↓
Click "Open Output Folder"
↓
See: Resume_TechCorp Inc.pdf, CV_TechCorp Inc.pdf
↓
Done! Ready to submit!
```

---

## 🔍 Troubleshooting Command Line

```bash
# Test Python installation
python --version

# Test dependencies
pip list | findstr "python-docx anthropic pyinstaller"

# Test templates generation
python setup_templates.py

# Test main application
python main.py

# Test build
build.bat
```

---

## 📊 System Requirements

| Component | Requirement |
|-----------|------------|
| OS | Windows 7+ (10+ recommended) |
| Python | 3.10+ (for building) |
| RAM | 2 GB minimum, 4 GB recommended |
| Disk | 500 MB for app, 1 GB for LibreOffice |
| Internet | Required for Claude API |
| LibreOffice | Must be installed |

---

## 🚨 Important Notes

1. **Never hardcode paths** - Always use config.json
2. **Keep templates safe** - Make backups
3. **Protect API key** - Don't share config.json
4. **Placeholders required** - Don't remove them
5. **Update regularly** - Check for new versions
6. **Test before sharing** - Run TEST_CHECKLIST.md

---

## 📅 Timeline

| Task | Time |
|------|------|
| Install deps | 2 min |
| Setup templates | 1 min |
| Configure app | 5 min |
| Per job usage | 1-2 min |
| Build .exe | 1 min |

---

## ✨ Features Summary

✓ AI-powered job analysis (Claude)
✓ Customizable fields (edit before PDF)
✓ Automated PDF generation
✓ Standalone .exe (no Python needed for users)
✓ Persistent configuration
✓ Windows integration (Open folder in Explorer)
✓ Error handling & validation
✓ Complete documentation

---

**Last Updated**: 2026-06-15  
**Version**: 1.0  
**Status**: ✅ Production Ready

**Print this card and keep it handy!** 📌
