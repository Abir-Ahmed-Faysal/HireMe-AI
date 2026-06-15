# HireMe AI - Complete Setup Guide

This guide walks you through setting up and building the HireMe AI desktop application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step-by-Step Installation](#step-by-step-installation)
3. [Configuration](#configuration)
4. [Building the EXE](#building-the-exe)
5. [First Run](#first-run)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

### 1. **Python 3.10 or Higher**
- Download from: https://www.python.org/downloads/
- **Important**: During installation, check ✓ "Add Python to PATH"
- Verify installation:
  ```bash
  python --version
  ```

### 2. **LibreOffice**
- Download from: https://www.libreoffice.org/
- Install the full suite
- **Default Windows installation path**: `C:\Program Files\LibreOffice\program\soffice.exe`
- Verify installation by checking that the above file exists

### 3. **Claude API Key**
- Go to: https://console.anthropic.com/
- Sign up or log in
- Create a new API key
- Keep it safe (starts with `sk-ant-`)

### 4. **Text Editor (Optional)**
- VS Code: https://code.visualstudio.com/
- Or any text editor

---

## Step-by-Step Installation

### Step 1: Clone or Download the Project

Navigate to the project directory:
```bash
cd C:\WorkSpace\Pdf_updater\JobApplicationAI
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `python-docx` - For editing Word documents
- `anthropic` - For Claude API integration
- `pyinstaller` - For building the .exe

**Expected output**: Something like:
```
Successfully installed python-docx anthropic pyinstaller
```

### Step 3: Create Template Documents

Run the setup script to generate resume and CV templates:

```bash
python setup_templates.py
```

This creates:
- `templates/resume.docx` - With `{{JOB_TITLE}}` placeholder
- `templates/cv.docx` - With `{{COMPANY_NAME}}` and `{{ROLE}}` placeholders

**Your next step**: 
1. Open both files in Microsoft Word or LibreOffice
2. Replace generic content with YOUR actual resume/CV content
3. **Keep the placeholders** - they're essential for the app to work
4. Save and close

### Step 4: Run the Application (First Time)

Start the application:

```bash
python main.py
```

You should see the Tkinter window with:
- A text area for pasting job circulars
- An "Analyze" button
- An "Edit Fields" section
- A "Generate PDFs" button
- A "Settings" button

### Step 5: Configure Settings

1. Click the **Settings** button
2. Configure all fields:

| Field | Example Value |
|-------|---------------|
| **Template Folder** | `C:\WorkSpace\Pdf_updater\JobApplicationAI\templates` |
| **Output Folder** | `C:\WorkSpace\Pdf_updater\JobApplicationAI\output` |
| **LibreOffice Path** | `C:\Program Files\LibreOffice\program\soffice.exe` |
| **Claude API Key** | `sk-ant-...` (your actual key) |

3. Click **Test AI Connection**
   - Should show: "Connection successful!"
   - If fails: Check your API key

4. Click **Save**

The configuration is saved to `config.json` and will persist for future runs.

---

## Configuration

### config.json Structure

The file looks like:
```json
{
  "template_folder": "C:\\Users\\YourName\\JobApplicationAI\\templates",
  "output_folder": "C:\\Users\\YourName\\JobApplicationAI\\output",
  "claude_api_key": "sk-ant-...",
  "libreoffice_path": "C:\\Program Files\\LibreOffice\\program\\soffice.exe"
}
```

### Finding LibreOffice Path on Your System

**Windows 64-bit (Most Common):**
```
C:\Program Files\LibreOffice\program\soffice.exe
```

**Windows 32-bit:**
```
C:\Program Files (x86)\LibreOffice\program\soffice.exe
```

**To verify**: Open File Explorer and navigate to the path. If you see `soffice.exe`, you have the right path.

---

## Building the EXE

### Option 1: Use Build Script (Recommended on Windows)

```bash
build.bat
```

This will:
1. Verify dependencies
2. Build the executable
3. Show the success message with output location

### Option 2: Manual Build

```bash
pyinstaller --onefile --windowed --name JobApplicationAI main.py
```

### Build Output

After successful build:
- **Executable location**: `dist/JobApplicationAI.exe`
- **Size**: ~50-100 MB (includes Python runtime)
- **Requirements**: Only needs LibreOffice installed on target PC

### Testing the EXE

1. Navigate to `dist/` folder
2. Double-click `JobApplicationAI.exe`
3. Should launch the application window
4. Configure Settings (same as Step 5 above)
5. Test with sample job circular

### Distributing the EXE

To share with others:
1. Copy `dist/JobApplicationAI.exe` to their computer
2. Ensure they have:
   - LibreOffice installed
   - Valid Claude API key
3. They run the .exe and configure settings on first run

---

## First Run

### Complete Workflow Test

1. **Start the app**:
   ```bash
   python main.py
   # or double-click JobApplicationAI.exe
   ```

2. **Paste a job posting**:
   - Find a job posting online
   - Copy the entire text
   - Paste into the text area

3. **Click Analyze**:
   - Wait for Claude to process
   - Should see three fields filled:
     - Job Title
     - Company Name
     - Role

4. **Review and edit** (optional):
   - Fields are editable
   - Make adjustments if needed

5. **Generate PDFs**:
   - Click "Generate PDFs"
   - Wait for processing
   - Success message appears

6. **Check output**:
   - Click "Open Output Folder"
   - Two PDFs should appear:
     - `Resume_[CompanyName].pdf`
     - `CV_[CompanyName].pdf`

---

## Troubleshooting

### Python Not Found

**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Go to: https://www.python.org/downloads/
2. Download Python 3.10+
3. **During installation**: ✓ Check "Add Python to PATH"
4. Restart command prompt
5. Try again: `python --version`

### LibreOffice Not Found

**Error**: `LibreOffice not found. Please install LibreOffice`

**Solution**:
1. Download: https://www.libreoffice.org/
2. Install full suite
3. Verify path exists: `C:\Program Files\LibreOffice\program\soffice.exe`
4. In Settings, set correct path and click Save

### Invalid Claude API Key

**Error**: `Invalid or missing Claude API key`

**Solution**:
1. Go to: https://console.anthropic.com/
2. Create/copy your API key (starts with `sk-ant-`)
3. In Settings, paste the key exactly
4. Click "Test AI Connection"

### Templates Not Found

**Error**: `Resume template not found` or `CV template not found`

**Solution**:
1. Verify `templates/` folder exists
2. Check `resume.docx` and `cv.docx` are in it
3. Run: `python setup_templates.py` to recreate
4. In Settings, verify Template Folder path is correct

### Placeholders Not Found

**Error**: `Placeholder '{{JOB_TITLE}}' not found`

**Solution**:
1. Open `templates/resume.docx` in Word
2. Search for `{{JOB_TITLE}}` (Ctrl+H)
3. If not found, add it back
4. Do same for `cv.docx` with `{{COMPANY_NAME}}` and `{{ROLE}}`
5. Save and try again

### PDF Generation Fails

**Error**: `LibreOffice conversion failed`

**Possible causes**:
1. LibreOffice path incorrect → Update in Settings
2. Template files corrupt → Recreate with `python setup_templates.py`
3. Output folder doesn't exist → Check permissions or create manually
4. LibreOffice already running → Close all LibreOffice windows

**Solution**:
1. Verify LibreOffice path in Settings
2. Test: `Test AI Connection` button shows success
3. Check output folder has write permissions
4. Try generating PDFs again

### Application Crashes on Startup

**Solution**:
1. Delete or rename `config.json`
2. Restart application
3. Reconfigure settings
4. Verify all paths are correct

---

## Advanced Usage

### Customizing Templates

1. Open `templates/resume.docx` in Word
2. Keep `{{JOB_TITLE}}` placeholder
3. Customize everything else:
   - Change fonts, colors
   - Adjust layout
   - Add more sections
4. Save (keep placeholder!)
5. Restart app

### Batch Processing

Currently, the app processes one job at a time. To process multiple:
1. Generate PDFs for Job 1
2. Paste next job circular
3. Analyze and generate
4. Repeat

PDFs are automatically named with company names, so no conflicts.

### Updating Claude Model

To use a newer Claude model:
1. Edit `ai_engine.py`
2. Change this line:
   ```python
   self.model = "claude-sonnet-4-20250514"
   ```
   to the desired model name
3. Save and rebuild

---

## File Structure Reference

```
JobApplicationAI/
├── main.py                    # Main application
├── ai_engine.py              # Claude integration
├── doc_editor.py             # Document editing
├── pdf_converter.py          # PDF conversion
├── settings_window.py        # Settings UI
├── config.json               # Configuration (created on first run)
├── requirements.txt          # Python dependencies
├── build.bat                 # Windows build script
├── setup_templates.py        # Template generator
├── templates/
│   ├── resume.docx          # Your resume with {{JOB_TITLE}}
│   └── cv.docx              # Your CV with {{COMPANY_NAME}} {{ROLE}}
├── output/                  # Generated PDFs go here
├── README.md                # Quick reference
└── SETUP_GUIDE.md          # This file
```

---

## Quick Reference Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Generate templates
python setup_templates.py

# Run application
python main.py

# Build executable
python setup_templates.py
build.bat

# Run built executable
dist/JobApplicationAI.exe
```

---

## Next Steps

1. ✓ Install Python and LibreOffice
2. ✓ Get Claude API key
3. ✓ Run `pip install -r requirements.txt`
4. ✓ Run `python setup_templates.py`
5. ✓ Edit templates with your content
6. ✓ Run `python main.py`
7. ✓ Configure settings
8. ✓ Build with `build.bat`
9. ✓ Share `dist/JobApplicationAI.exe` with others

---

## Support & FAQ

**Q: Do users need Python installed to run the .exe?**
A: No! The .exe includes everything needed except LibreOffice.

**Q: Can I edit the settings after building?**
A: Yes! Settings are saved in `config.json` in the same directory as the .exe.

**Q: How do I update the application?**
A: Edit the Python files and rebuild with `build.bat`.

**Q: Is the API key secure?**
A: It's stored locally in `config.json`. Never share this file with others.

**Q: Can I use a different document format?**
A: Currently supports DOCX only. We can extend to add support for other formats.

---

**Version**: 1.0  
**Last Updated**: 2026-06-15  
**Python Version Required**: 3.10+
