# Quick Start Guide - HireMe AI

## For First-Time Users

### After Installation & Configuration

1. **Open the Application**
   - Double-click `JobApplicationAI.exe` or run `python main.py`

2. **Paste Job Posting**
   - Copy a job posting/circular from a website
   - Paste into the text area at the top

3. **Click "Analyze Job Circular"**
   - Wait for Claude AI to extract details
   - Three fields will auto-populate:
     - Job Title
     - Company Name
     - Role

4. **Review Fields (Optional)**
   - Fields are editable if you want to adjust
   - Make any changes directly

5. **Click "Generate PDFs"**
   - Application creates:
     - Resume_[CompanyName].pdf
     - CV_[CompanyName].pdf

6. **Check Output**
   - Click "Open Output Folder" to see PDFs
   - PDFs are ready to submit!

---

## One Job Per Minute!

### Workflow Example

| Action | Time |
|--------|------|
| Paste job posting | 10 seconds |
| Click Analyze | 5 seconds |
| Claude processes | 5-10 seconds |
| Review fields | 10 seconds |
| Click Generate | 3 seconds |
| PDFs created | 20-30 seconds |
| **Total** | **~1 minute** |

---

## Common Scenarios

### Scenario 1: You're Happy with AI Results
```
Paste → Analyze → Generate PDFs → Done
```

### Scenario 2: You Want to Tweak Details
```
Paste → Analyze → Edit Fields → Generate PDFs → Done
```

### Scenario 3: Apply to Multiple Jobs
```
Job 1: Paste → Analyze → Generate
Job 2: Clear → Paste → Analyze → Generate
Job 3: Clear → Paste → Analyze → Generate
```

---

## Tips & Tricks

### To Speed Up Processing
- Copy entire job posting with all details
- Claude does better with more context

### For Better Job Titles
- If AI generates a generic title, edit it yourself
- Use specific job titles that match your resume

### Organizing Output
- PDFs are named with company name
- Move them to a folder per company
- Use "Open Output Folder" button

### Customizing Your Templates
1. Close the application
2. Edit `templates/resume.docx` and `templates/cv.docx`
3. Keep the placeholders: `{{JOB_TITLE}}`, `{{COMPANY_NAME}}`, `{{ROLE}}`
4. Save and restart application

---

## Settings Reference

| Setting | Default | Example |
|---------|---------|---------|
| Template Folder | Templates directory | `C:\...\templates` |
| Output Folder | Output directory | `C:\...\output` |
| LibreOffice Path | Auto-detected | `C:\Program Files\...\soffice.exe` |
| Claude API Key | Empty | `sk-ant-...` |

**To Change Settings:**
1. Click "Settings" button
2. Update any field
3. Click "Test AI Connection" (optional)
4. Click "Save"

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+A` in text area | Select all text |
| `Ctrl+V` | Paste job circular |
| `Tab` | Move to next field |
| `Ctrl+Z` | Undo (in document fields) |

---

## Error Messages & Solutions

| Error | Solution |
|-------|----------|
| "API Key not configured" | Click Settings → Enter Claude API Key → Save |
| "Template files not found" | Run `python setup_templates.py` |
| "LibreOffice not found" | Click Settings → Set correct path → Save |
| "Conversion failed" | Ensure LibreOffice path is correct and LibreOffice is installed |

---

## FAQ

**Q: How many jobs can I apply to?**
A: Unlimited! Generate PDFs for as many jobs as you want.

**Q: Can I use without the internet?**
A: No, Claude API requires internet connection. LibreOffice conversion is local.

**Q: Where are my PDFs saved?**
A: In the Output Folder (click "Open Output Folder" button to see).

**Q: Can I change templates?**
A: Yes! Edit the DOCX files in `templates/` folder (keep placeholders).

**Q: How is my API key stored?**
A: In `config.json` locally on your computer (never sent anywhere except to Claude).

**Q: Can I use on Mac/Linux?**
A: With modifications - LibreOffice works on all systems, but some paths differ.

**Q: What if I mess up a template?**
A: Delete the templates and run `python setup_templates.py` to regenerate.

---

## Workflow Tips

### Best Practices
✓ Read job posting thoroughly before pasting
✓ Let Claude do the analysis (usually accurate)
✓ Review extracted details before generating
✓ Check generated PDFs before submitting
✓ Keep both PDF copies for your records

### What NOT to Do
✗ Don't paste irrelevant text as job posting
✗ Don't generate PDFs with empty fields
✗ Don't edit templates while app is open
✗ Don't share `config.json` (has API key)

---

## Getting Help

1. **Application won't start?**
   - Check Python and LibreOffice installed
   - Run with `python main.py` for error messages

2. **Settings not saving?**
   - Check file permissions on config.json
   - Ensure paths are valid and accessible

3. **PDFs not generating?**
   - Verify LibreOffice path
   - Check output folder write permissions
   - Ensure templates have required placeholders

4. **AI not working?**
   - Test connection in Settings
   - Verify Claude API key is valid
   - Check internet connection

---

## Advanced: Bulk Job Applications

Process multiple job postings:

1. Collect all job postings into text files
2. Open application
3. For each job:
   ```
   Paste job posting text
   Click "Analyze"
   Verify fields
   Click "Generate PDFs"
   ```
4. PDFs are automatically saved with company names
5. View all in Output Folder

---

**Questions?** See `README.md` for detailed documentation or `SETUP_GUIDE.md` for setup help.

**Ready to apply?** Let's go! 🚀
