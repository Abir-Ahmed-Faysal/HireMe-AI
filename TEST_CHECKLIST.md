# Test Checklist - HireMe AI

Use this checklist to verify everything is working correctly.

## Pre-Build Testing (Development)

### Environment Setup
- [ ] Python 3.10+ installed (`python --version` shows 3.10+)
- [ ] LibreOffice installed and path verified
- [ ] Claude API key obtained
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] No permission errors on project folder

### Initial Run
- [ ] Can run `python main.py` without errors
- [ ] Main window opens with all UI elements
- [ ] No error messages in console

### Templates
- [ ] Run `python setup_templates.py` successfully
- [ ] `templates/resume.docx` created
- [ ] `templates/cv.docx` created
- [ ] Both files can be opened in Word

### Configuration
- [ ] Settings window opens
- [ ] All fields visible and editable
- [ ] Can select folders with Browse buttons
- [ ] API Key field shows masked input
- [ ] Test AI Connection returns success
- [ ] Settings save to `config.json`
- [ ] `config.json` contains correct values

### Core Functionality
- [ ] Can paste text into job circular area
- [ ] Analyze button processes text
- [ ] Job Title field auto-populates
- [ ] Company Name field auto-populates
- [ ] Role field auto-populates
- [ ] Fields are editable after analysis
- [ ] Can modify extracted values

### PDF Generation
- [ ] Generate PDFs button works
- [ ] No errors during PDF generation
- [ ] PDFs created in output folder
- [ ] PDF filename includes company name
- [ ] Both Resume and CV PDFs created
- [ ] PDFs can be opened and viewed
- [ ] Content includes customized values

### File Management
- [ ] Open Output Folder button opens Windows Explorer
- [ ] Output folder contains generated PDFs
- [ ] Temp files are cleaned up
- [ ] No orphaned docx files left behind

### Error Handling
- [ ] Missing API key shows error
- [ ] Missing templates shows error
- [ ] LibreOffice not found shows error
- [ ] Invalid JSON response shows error
- [ ] Network errors handled gracefully
- [ ] All error messages are user-friendly

---

## Post-Build Testing (.EXE)

### Build Process
- [ ] `build.bat` runs without errors
- [ ] No warnings during build
- [ ] Build completes successfully
- [ ] `dist/JobApplicationAI.exe` created (~50-100 MB)
- [ ] Build completes in under 2 minutes

### Standalone Execution
- [ ] Can double-click `JobApplicationAI.exe` to run
- [ ] Application launches without Python visible
- [ ] Main window appears identical to dev version
- [ ] No console window appears

### Configuration in EXE
- [ ] Settings window accessible
- [ ] Can set all configuration values
- [ ] Test AI Connection works
- [ ] Settings persist after restart
- [ ] `config.json` created next to .exe

### Full Workflow
- [ ] Paste job circular
- [ ] Click Analyze
- [ ] Fields populate correctly
- [ ] Edit fields (optional)
- [ ] Click Generate PDFs
- [ ] PDFs appear in output folder
- [ ] PDFs contain customized content

### PDF Quality
- [ ] Resume PDF readable
- [ ] CV PDF readable
- [ ] Text formatting preserved
- [ ] Job title appears in Resume
- [ ] Company name appears in CV
- [ ] Role appears in CV

---

## Batch Testing (Multiple Jobs)

- [ ] Can process Job 1 successfully
- [ ] Can clear fields and process Job 2
- [ ] Can process Job 3 without conflicts
- [ ] All PDFs have unique names (by company)
- [ ] No file overwrites occur
- [ ] Output folder contains all PDFs

---

## Document Template Testing

### Resume Template
- [ ] File exists at correct path
- [ ] Contains `{{JOB_TITLE}}` placeholder
- [ ] Placeholder is replaced correctly
- [ ] Other content remains unchanged
- [ ] Formatting preserved in PDF

### CV Template
- [ ] File exists at correct path
- [ ] Contains `{{COMPANY_NAME}}` placeholder
- [ ] Contains `{{ROLE}}` placeholder
- [ ] Both placeholders replaced correctly
- [ ] Other content remains unchanged
- [ ] Formatting preserved in PDF

### Placeholder Validation
- [ ] Error shown if `{{JOB_TITLE}}` missing from resume
- [ ] Error shown if `{{COMPANY_NAME}}` missing from CV
- [ ] Error shown if `{{ROLE}}` missing from CV
- [ ] Error message is clear and actionable

---

## LibreOffice Integration Testing

### Path Detection
- [ ] Auto-detects LibreOffice if standard path
- [ ] Uses config path if provided
- [ ] Shows error if path incorrect
- [ ] Shows error if soffice.exe not found

### Conversion Process
- [ ] Headless mode works without UI
- [ ] PDF generation completes in <30 seconds per file
- [ ] No LibreOffice windows appear
- [ ] PDF quality is good
- [ ] All pages converted correctly

### Error Handling
- [ ] Timeout handled gracefully
- [ ] Corrupted docx shows error
- [ ] Missing output folder creates it automatically
- [ ] Permission denied on output folder shows error

---

## Claude API Integration Testing

### Connection Test
- [ ] Test connection button works
- [ ] Success message on valid key
- [ ] Error message on invalid key
- [ ] Handles network timeouts
- [ ] Works with multiple attempts

### Job Analysis
- [ ] Extracts job title correctly
- [ ] Extracts company name correctly
- [ ] Extracts role correctly
- [ ] Handles various job posting formats
- [ ] Returns valid JSON
- [ ] Validates all required fields

### Error Cases
- [ ] Handles empty job circular
- [ ] Handles very long job postings (>5000 chars)
- [ ] Handles special characters properly
- [ ] Invalid API key shows error
- [ ] Network error shows user-friendly message

---

## UI/UX Testing

### Main Window
- [ ] Window resizable
- [ ] All buttons visible
- [ ] Text area scrollable
- [ ] Fields properly labeled
- [ ] Status bar shows messages
- [ ] Status bar updates correctly

### Settings Window
- [ ] Opens as modal
- [ ] Cannot interact with main window while open
- [ ] Browse buttons work
- [ ] All fields editable
- [ ] Save button saves changes
- [ ] Cancel button discards changes

### User Feedback
- [ ] Status messages clear
- [ ] Success/error dialogs informative
- [ ] Buttons disable during processing
- [ ] Progress visible to user

---

## Performance Testing

### Load Time
- [ ] Application starts in <3 seconds
- [ ] Settings window opens instantly
- [ ] No lag when typing in fields

### Analysis Time
- [ ] Job analysis completes in <15 seconds
- [ ] PDF generation completes in <60 seconds total
- [ ] No UI freezing during processing

### File Operations
- [ ] Handles large documents (>10 MB)
- [ ] Creates output folder quickly
- [ ] Moves/renames files without delay
- [ ] Cleanup completes without delay

---

## Cross-Platform Testing (if applicable)

- [ ] Windows 10 compatibility ✓
- [ ] Windows 11 compatibility ✓
- [ ] 64-bit systems ✓
- [ ] 32-bit systems (if applicable)
- [ ] Non-English Windows installations

---

## Security Testing

### API Key Protection
- [ ] Key not logged to console
- [ ] Key shown masked in UI
- [ ] Key stored only in config.json
- [ ] Key not included in build
- [ ] Key requires explicit entry

### File Permissions
- [ ] Can write to output folder
- [ ] Temp files have correct permissions
- [ ] Generated PDFs accessible to user
- [ ] No security warnings from antivirus

---

## Real-World Testing

### Sample Job Postings
Test with actual job postings from:
- [ ] LinkedIn
- [ ] Indeed
- [ ] LinkedIn
- [ ] Company websites
- [ ] Job boards

### Accuracy Verification
For each test job posting:
- [ ] Job title extracted accurately
- [ ] Company name extracted accurately
- [ ] Role extracted accurately
- [ ] Generated PDFs suitable for submission

### Multiple Jobs
- [ ] Process 5+ different jobs
- [ ] No degradation in quality
- [ ] No memory leaks
- [ ] All PDFs unique and correct

---

## Documentation Verification

- [ ] README.md is accurate
- [ ] SETUP_GUIDE.md step-by-step works
- [ ] QUICK_START.md is clear
- [ ] All paths in docs are correct
- [ ] All commands actually work
- [ ] No broken references

---

## Final Sign-Off

| Item | Status | Notes |
|------|--------|-------|
| All tests passed | ☐ | Date: _______ |
| Ready for production | ☐ | Date: _______ |
| Ready to distribute | ☐ | Date: _______ |

---

## Rollback Plan

If tests fail:
1. [ ] Document the issue
2. [ ] Identify root cause
3. [ ] Fix in source code
4. [ ] Delete old build: `rmdir /s dist`
5. [ ] Rebuild: `build.bat`
6. [ ] Re-test specific area
7. [ ] Document resolution

---

## Notes

Space for test notes:
```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

---

**Test Date**: ___________  
**Tester Name**: ___________  
**Result**: ✓ PASS  ☐ FAIL
