from __future__ import annotations

import calendar
import sqlite3
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

MONTH_NAMES = {i: calendar.month_name[i] for i in range(1, 13)}

@dataclass
class Assignment:
    id: str; title: str; course: str; due_date: str; due_time: str | None
    category: str; priority: str; notes: str = ""; completed: bool = False

SCHEMA = """
CREATE TABLE IF NOT EXISTS assignments (
 id TEXT PRIMARY KEY, title TEXT NOT NULL, course TEXT NOT NULL, due_date TEXT NOT NULL,
 due_time TEXT, category TEXT NOT NULL, priority TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '',
 completed INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS syllabi (
 id TEXT PRIMARY KEY, filename TEXT NOT NULL, content BLOB NOT NULL,
 uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, status TEXT NOT NULL DEFAULT 'Waiting for parser');
"""

def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path); db.row_factory = sqlite3.Row; db.executescript(SCHEMA)
    return db

def month_weeks(year: int, month: int) -> list[list[date]]:
    return calendar.Calendar(firstweekday=calendar.MONDAY).monthdatescalendar(year, month)

def create_assignment(**v) -> Assignment:
    due, due_time = v["due_date"], v.get("due_time")
    return Assignment(str(uuid4()), v["title"].strip(), v["course"].strip(),
        due.isoformat() if isinstance(due, date) else due,
        due_time.strftime("%H:%M") if hasattr(due_time, "strftime") else due_time,
        v["category"], v["priority"], v.get("notes", "").strip())

def list_assignments(path: Path) -> list[Assignment]:
    with connect(path) as db:
        rows = db.execute("SELECT * FROM assignments ORDER BY due_date, COALESCE(due_time,'23:59'), title").fetchall()
    return [Assignment(**{k: bool(r[k]) if k == "completed" else r[k] for k in Assignment.__dataclass_fields__}) for r in rows]

def save_assignment(path: Path, x: Assignment) -> None:
    with connect(path) as db:
        db.execute("INSERT OR REPLACE INTO assignments (id,title,course,due_date,due_time,category,priority,notes,completed) VALUES (?,?,?,?,?,?,?,?,?)",
            (x.id,x.title,x.course,x.due_date,x.due_time,x.category,x.priority,x.notes,int(x.completed)))

def update_assignment(path: Path, item_id: str, **values) -> None:
    allowed={"title","course","due_date","due_time","category","priority","notes","completed"}
    v={k:x for k,x in values.items() if k in allowed}
    if not v: return
    if isinstance(v.get("due_date"),date): v["due_date"]=v["due_date"].isoformat()
    if hasattr(v.get("due_time"),"strftime"): v["due_time"]=v["due_time"].strftime("%H:%M")
    if "completed" in v: v["completed"]=int(v["completed"])
    with connect(path) as db: db.execute(f"UPDATE assignments SET {', '.join(f'{k}=?' for k in v)} WHERE id=?",[*v.values(),item_id])

def delete_assignment(path: Path, item_id: str) -> None:
    with connect(path) as db: db.execute("DELETE FROM assignments WHERE id=?",(item_id,))

def save_syllabus(path: Path, filename: str, content: bytes) -> None:
    with connect(path) as db: db.execute("INSERT INTO syllabi (id,filename,content) VALUES (?,?,?)",(str(uuid4()),filename,content))

def list_syllabi(path: Path) -> list[dict]:
    with connect(path) as db: return [dict(r) for r in db.execute("SELECT id,filename,uploaded_at,status FROM syllabi ORDER BY uploaded_at DESC")]

def seed_demo(path: Path) -> None:
    if list_assignments(path): return
    samples=[("Read chapters 1–3","Media Studies",date(2026,9,22),None,"Reading","Medium","Take notes on visual framing."),("Discussion post","Media Studies",date(2026,9,26),"18:00","Assignment","Medium","Respond to two classmates."),("Quiz 1","Statistics",date(2026,10,5),"09:30","Quiz","High","Distributions and z-scores."),("Research proposal","English 210",date(2026,10,18),"23:59","Project","High","2–3 pages plus sources."),("Midterm exam","Statistics",date(2026,11,12),"10:00","Exam","High","Bring calculator and student ID.")]
    for title,course,due,t,cat,priority,notes in samples: save_assignment(path,create_assignment(title=title,course=course,due_date=due,due_time=t,category=cat,priority=priority,notes=notes))

def to_ics(items: list[Assignment]) -> bytes:
    def esc(v: str): return v.replace("\\","\\\\").replace(";","\\;").replace(",","\\,").replace("\n","\\n")
    out=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//StudyFlow//EN","CALSCALE:GREGORIAN"]
    for x in items:
        out += ["BEGIN:VEVENT",f"UID:{x.id}@studyflow",f"SUMMARY:{esc(x.course+': '+x.title)}"]
        if x.due_time:
            stamp=x.due_date.replace("-","")+"T"+x.due_time.replace(":","")+"00"; out += [f"DTSTART:{stamp}",f"DTEND:{stamp}"]
        else:
            out += [f"DTSTART;VALUE=DATE:{x.due_date.replace('-','')}",f"DTEND;VALUE=DATE:{(date.fromisoformat(x.due_date)+timedelta(days=1)).strftime('%Y%m%d')}"]
        out += [f"DESCRIPTION:{esc(x.notes)}","END:VEVENT"]
    return ("\r\n".join(out+["END:VCALENDAR",""])).encode()
