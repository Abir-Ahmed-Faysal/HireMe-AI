# Deployment Guide - HireMe AI

Guide for developers to package and distribute the .exe to end users.

## Building for Distribution

### Prerequisites for Builder
- [ ] Python 3.10+ installed
- [ ] All dependencies: `pip install -r requirements.txt`
- [ ] LibreOffice installed (for testing)
- [ ] Valid Claude API key (for testing)

### Build Steps

1. **Update Version (Optional)**
   Edit `main.py`, line with window title to add version:
   ```python
   self.root.title("HireMe AI v1.0")
   ```

2. **Clean Previous Build**
   ```bash
   rmdir /s /q dist
   rmdir /s /q build
   del JobApplicationAI.spec
   ```

3. **Build Executable**
   ```bash
   build.bat
   ```
   Or manually:
   ```bash
   pyinstaller --onefile --windowed --name JobApplicationAI main.py
   ```

4. **Test the Build**
   - Navigate to `dist/` folder
   - Double-click `JobApplicationAI.exe`
   - Verify all functionality works
   - Run through test checklist

### Build Verification
- [ ] `dist/JobApplicationAI.exe` exists
- [ ] File size 50-100 MB (reasonable)
- [ ] Runs without errors
- [ ] Can access Settings
- [ ] Can run test job analysis
- [ ] Can generate PDFs

---

## Creating Distribution Package

### Option 1: Standalone EXE Only

**For:** Users who just want the executable

**Package Contents:**
```
JobApplicationAI.exe
```

**Recipient Setup:**
1. Download JobApplicationAI.exe
2. Install LibreOffice
3. Get Claude API key
4. Run .exe and configure settings

**Pros**: Minimal file, fast download
**Cons**: User must install LibreOffice

### Option 2: Complete Package (Recommended)

**For:** Complete setup with templates and guides

**Create folder:**
```bash
mkdir JobApplicationAI_Distribution
```

**Copy files:**
```
JobApplicationAI_Distribution/
├── JobApplicationAI.exe          (from dist/)
├── README.md                     (quick reference)
├── QUICK_START.md               (for first use)
├── SETUP_GUIDE.md               (detailed setup)
├── FIRST_RUN.md                 (new file - see below)
└── templates/
    ├── resume.docx              (sample template)
    └── cv.docx                  (sample template)
```

**Compress for distribution:**
```bash
# Create zip file
PowerShell Compress-Archive -Path JobApplicationAI_Distribution -DestinationPath JobApplicationAI_v1.0.zip
```

---

## Creating First-Run Guide

Create `FIRST_RUN.md` for distribution:

```markdown
# First Time Setup

## What You Received
- JobApplicationAI.exe - The application
- Sample resume.docx and cv.docx templates
- Documentation files

## What You Need to Install
1. **LibreOffice** (FREE)
   - Download: https://www.libreoffice.org/
   - Install full suite
   - Takes ~5-10 minutes

2. **Claude API Key** (FREE tier available)
   - Go: https://console.anthropic.com/
   - Sign up
   - Create API key
   - Free tier: $5 credit

## Quick Setup (5 minutes)

1. Install LibreOffice
2. Get Claude API key
3. Run JobApplicationAI.exe
4. Click Settings:
   - Set Template Folder: folder with resume.docx and cv.docx
   - Set Output Folder: where you want PDFs saved
   - Set LibreOffice Path: C:\Program Files\LibreOffice\program\soffice.exe
   - Paste Claude API Key
5. Click "Test AI Connection" → Success!
6. Click Save

## First Use (2 minutes)

1. Find a job posting online
2. Copy the job posting text
3. Paste into application
4. Click "Analyze Job Circular"
5. Review the 3 fields
6. Click "Generate PDFs"
7. PDFs appear in Output Folder!

That's it! You now have customized Resume and CV PDFs ready to submit.

## Customizing Templates

1. Open templates/resume.docx in Word
2. Replace with YOUR actual resume content
3. Keep the `{{JOB_TITLE}}` placeholder
4. Save

Repeat for templates/cv.docx with `{{COMPANY_NAME}}` and `{{ROLE}}`

## Support

See included documentation:
- README.md - Overview and features
- QUICK_START.md - Common tasks
- SETUP_GUIDE.md - Detailed setup help
```

---

## Distribution Methods

### Method 1: Email/File Transfer

**Package:**
```
JobApplicationAI_v1.0.zip (50-100 MB)
```

**Recipients:**
1. Extract zip file
2. Read FIRST_RUN.md
3. Run JobApplicationAI.exe

### Method 2: Cloud Storage

**Upload to:**
- Google Drive
- OneDrive
- Dropbox
- GitHub Releases

**Share link with:**
```
Hey! I built an app that generates customized resume PDFs automatically using AI.

Download: [link to zip]

It takes 5 minutes to set up and 2 minutes per job to generate PDFs.

Just install LibreOffice and add your Claude API key (free tier available).

Let me know if you need help!
```

### Method 3: GitHub Release

**Steps:**
1. Create GitHub repo
2. Push all source code
3. Create Release
4. Attach `JobApplicationAI.exe` as binary
5. Add release notes with FIRST_RUN instructions

**Benefits:**
- Version control
- Easy to update
- Users can see all code
- Get feedback through Issues

### Method 4: USB/Physical Media

**Copy to USB:**
```
USB Drive/
├── JobApplicationAI.exe
├── FIRST_RUN.md
└── templates/
    ├── resume.docx
    └── cv.docx
```

**Total size:** ~10-20 MB (fits on tiny USB)

---

## Version Management

### Versioning Strategy

Format: `MAJOR.MINOR.PATCH`

**Version 1.0.0**
- Initial release
- Basic functionality

**Version 1.1.0**
- Added new features
- Bug fixes
- Backward compatible

**Version 2.0.0**
- Major changes
- Possible breaking changes

### Updating Users

**When to update:**
- Security issues
- Critical bugs
- Useful new features

**How to update:**
1. Build new .exe
2. Create new Release
3. Notify users with changelog
4. Users replace old .exe with new one

**Changelog example:**
```
## Version 1.1.0

### New Features
- Support for Google Docs templates
- Batch job processing

### Bug Fixes
- Fixed PDF naming with special characters
- Improved LibreOffice path detection

### Updates
- Updated Claude model to latest version
```

---

## System Requirements

**Minimum:**
- Windows 7 or later (10 recommended)
- 500 MB free disk space
- 2 GB RAM
- Internet connection (for Claude API)

**Recommended:**
- Windows 10 or later
- 1 GB free disk space
- 4 GB RAM
- Good internet connection

**Required Software:**
- LibreOffice (free, 250 MB)
- Valid Claude API key (free tier available)

---

## Troubleshooting for Recipients

### Most Common Issues

**Issue:** "LibreOffice not found"
```
Solution: 
1. Verify LibreOffice installed
2. In Settings, set correct path
3. Default: C:\Program Files\LibreOffice\program\soffice.exe
```

**Issue:** "Invalid API Key"
```
Solution:
1. Go to console.anthropic.com
2. Create new API key (starts with sk-ant-)
3. Paste exactly into Settings
4. Click Test Connection
```

**Issue:** "Templates not found"
```
Solution:
1. Verify resume.docx and cv.docx exist
2. Edit them with YOUR content
3. Keep placeholders: {{JOB_TITLE}}, {{COMPANY_NAME}}, {{ROLE}}
4. In Settings, set correct Template Folder path
```

---

## Support Strategy

### Provide
- Clear documentation (included)
- Quick start guide
- Troubleshooting guide
- Sample templates

### Track
- Common issues
- User feedback
- Feature requests
- Bug reports

### Improve
- Fix bugs in next version
- Add requested features
- Improve documentation
- Update troubleshooting guide

---

## Security Considerations

### For Recipients
- [ ] Only download from trusted source
- [ ] Verify file size is ~50-100 MB
- [ ] Check for antivirus warnings
- [ ] API key is stored locally only
- [ ] Never share config.json

### For Distributors
- [ ] Don't include API key in build
- [ ] Sign executable (optional but recommended)
- [ ] Include clear documentation
- [ ] Provide support channel
- [ ] Keep contact info for updates

---

## Licensing & Attribution

If you built on this project:

**MIT License (Included):**
- You can distribute freely
- You can modify and redistribute
- Must include license notice

**Attribution:**
```
Built with HireMe AI
Original: [your GitHub repo link]
```

---

## Post-Distribution Checklist

- [ ] Recipients can download/access files
- [ ] Recipients can extract/unzip files
- [ ] Recipients can run .exe
- [ ] Settings window opens
- [ ] Can configure all paths
- [ ] Test AI Connection works
- [ ] Can analyze sample job posting
- [ ] Can generate sample PDFs
- [ ] Recipients report success

---

## Common Distribution Scenarios

### Scenario 1: Sharing with Friends
```
Package: Single .exe file
Method: Email or file transfer
Setup: Help them configure on call
Support: Available via text/call
```

### Scenario 2: Company Distribution
```
Package: Complete zip with documentation
Method: Internal portal or GitHub Enterprise
Setup: Email with FIRST_RUN.md
Support: IT help desk or email
```

### Scenario 3: Public Release
```
Package: GitHub Release with .zip
Method: GitHub + share link on social media
Setup: Users self-serve with docs
Support: GitHub Issues
```

---

## Quick Distribution Commands

```bash
# Clean old builds
rmdir /s /q dist build
del *.spec

# Build fresh
build.bat

# Create distribution folder
mkdir JobApplicationAI_Distribution

# Copy files
copy dist\JobApplicationAI.exe JobApplicationAI_Distribution\
copy README.md JobApplicationAI_Distribution\
copy QUICK_START.md JobApplicationAI_Distribution\
copy SETUP_GUIDE.md JobApplicationAI_Distribution\
copy templates\*.docx JobApplicationAI_Distribution\templates\

# Create zip
PowerShell Compress-Archive -Path JobApplicationAI_Distribution -DestinationPath JobApplicationAI_v1.0.zip

# Ready to distribute!
```

---

## Success Metrics

Track your distribution success:

| Metric | Target |
|--------|--------|
| Downloads | ? |
| Setup success rate | >90% |
| User satisfaction | >4/5 stars |
| Bug reports | <5 per 100 users |
| Support requests | <3 per 100 users |

---

## Next Steps for Distributors

1. ✓ Build and test .exe thoroughly
2. ✓ Create distribution package
3. ✓ Write clear documentation
4. ✓ Choose distribution method
5. ✓ Prepare support plan
6. ✓ Release to recipients
7. ✓ Monitor feedback
8. ✓ Plan updates/improvements

---

**Questions?** See the main README.md or SETUP_GUIDE.md for more details.

**Ready to share?** Your recipients will love it! 🚀
