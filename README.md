# My 2026 School Calendar

An interactive, mobile-ready Python/Streamlit planner built around a 2026 calendar. Python handles the application and SQLite data; Streamlit delivers the responsive browser interface.

## Current features

- Month calendar and compact 2026 overview
- Monday–Sunday week rows
- Assignment, exam, reading, project, quiz, and other event types
- Course/type filters, priority, due time, notes, and completion status
- SQLite persistence for assignments and uploaded syllabi
- Responsive phone agenda plus desktop month grid
- Search, filtering, sample data, and `.ics` calendar export
- PDF, DOCX, and TXT syllabus inbox

## Run it

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL, normally `http://localhost:8501`.

To test it on a phone connected to the same Wi-Fi, run `streamlit run app.py --server.address 0.0.0.0`, then open `http://YOUR-COMPUTER-IP:8501` on the phone. For permanent access, deploy this folder from GitHub to a Python host.

## Test it

```bash
pytest -q
```

## Next phase

When syllabi are available, add a parser that extracts course names, assignment titles, dates, times, grading categories, and recurring class meetings. Extracted items should be shown in a review screen before they are added to the calendar.
