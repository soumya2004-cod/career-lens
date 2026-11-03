# CareerLens — Smart Resume Analyzer & Job Readiness Advisor

A complete local Flask web application with a polished responsive interface, resume upload, job-specific keyword skill coverage, skill-gap suggestions, interview practice prompts and Matplotlib charts. **No database, CSV, external API or account required.**

## Requirements
- Python 3.10+ recommended
- Internet only for the initial Python package installation

## Setup on Windows (VS Code)
1. Extract ZIP and open the `smart_resume_advisor` folder in VS Code.
2. Open Terminal → New Terminal.
3. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
4. Install packages using the virtual environment Python (activation not necessary):
   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
5. Run the app:
   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```
6. Open **http://127.0.0.1:5000** in your browser.

On macOS/Linux, use `python3 -m venv .venv`, `.venv/bin/pip install -r requirements.txt`, `.venv/bin/python app.py`.

## Demo
1. Use the included `sample_resume.txt` as a sample upload.
2. Click **Insert example** for a Python Developer job description.
3. Click **Analyze my resume**.
4. Explore the score, matched skills, gaps, graph, suggestions and practice questions.
5. Download the `.txt` analysis report. Change job description and analyze again to see how the score changes.

## Project structure
```
smart_resume_advisor/
├── app.py                 # Flask routes, resume extraction and chart generation
├── analyzer.py            # Rule-based matching and personalized feedback
├── requirements.txt
├── sample_resume.txt
├── sample_job_description.txt
├── templates/index.html   # Webpage UI
├── static/style.css       # Styling and responsiveness
├── static/app.js          # Upload, results, download, interaction
└── tests/test_analyzer.py # Unit tests
```

## How it works (viva explanation)
- **Frontend:** HTML, CSS and JavaScript display the form and dashboard.
- **Backend:** Flask receives PDF/DOCX/TXT uploaded files in memory. The contents are not saved to disk or to a database.
- **Text extraction:** `pypdf` extracts PDF text, `python-docx` reads DOCX, and built-in decoding handles TXT.
- **Skill matching:** Python regular expressions detect whole skill terms in both resume and job description, including a few known aliases.
- **Coverage:** `number of job skills also in resume / number of detected job skills × 100`.
- **Graph:** Matplotlib draws matched vs missing skills for each category and returns an in-memory PNG to the UI.
- **Suggestions:** Missing detected skills become prioritized learning/review suggestions. The app never encourages adding false skills.
- **Report:** The frontend exports results to a local TXT file.

## Limitations / improvements
- **Not an official ATS score.** The score measures only recognized keyword coverage. It doesn't assess experience quality, education equivalence, suitability or hiring decisions.
- Recognized skills come from the editable `SKILL_GROUPS` dictionary in `analyzer.py`. Unlisted skills won't be matched.
- Word matches can be imperfect and do not prove proficiency, recency or experience. Negated statements can still match keywords.
- Scanned/image-only PDFs need OCR, which is not included; use a selectable-text PDF, DOCX or TXT.
- Uploaded files are processed in-memory and discarded after a request. This is intended for **local** use; don't expose the debug server publicly.
- Future scope: contextual NLP, skill extraction beyond a predefined dictionary, experience evidence extraction, multiple job comparisons, better scoring and advanced PDF support.

## Run unit tests
```
python -m unittest discover -s tests -v
```
