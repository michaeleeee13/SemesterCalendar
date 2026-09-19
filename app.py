from __future__ import annotations
import html
from datetime import date, datetime, time
from pathlib import Path
import streamlit as st
from calendar_engine import MONTH_NAMES, Assignment, create_assignment, delete_assignment, list_assignments, list_syllabi, month_weeks, save_assignment, save_syllabus, seed_demo, to_ics, update_assignment

YEAR=2026; ROOT=Path(__file__).parent; DB_FILE=ROOT/"data"/"school_calendar.db"
COLORS={"Assignment":"#5b7cfa","Reminder":"#7b61ff","Event":"#2aa6a6","Exam":"#e25b65","Quiz":"#26a77a","Reading":"#8d65d6","Project":"#e49a3a","Other":"#6f7a89"}
st.set_page_config(page_title="Semester Calendar",page_icon="📚",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>
:root{--ink:#172033;--muted:#6d7585;--line:#e8eaf0}.stApp{background:linear-gradient(150deg,#f8f9fc,#fff 42%,#f7f8fc);color:var(--ink)}
.block-container{max-width:1480px;padding-top:1.25rem;padding-bottom:5rem}[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);padding:13px 15px;border-radius:16px;box-shadow:0 8px 25px #1f2a440a}
.hero{padding:9px 0 18px}.eyebrow{letter-spacing:.13em;text-transform:uppercase;font-size:.72rem;font-weight:800;color:#5b7cfa}.hero h1{font-size:clamp(2rem,5vw,3.8rem);line-height:1;margin:.3rem 0 .65rem;letter-spacing:-.045em}.hero p{color:var(--muted);font-size:1.03rem;margin:0}
.create-bar{display:flex;align-items:center;gap:1rem;margin:0 0 1rem}.create-toggle{background:linear-gradient(135deg,#5b7cfa,#7b61ff);color:#fff;border:none;border-radius:14px;padding:.8rem 1.2rem;font-weight:800;box-shadow:0 12px 26px #5b7cfa4d}.create-panel{background:#fff;border:1px solid #e8eaf0;border-radius:18px;padding:1rem 1rem 0.5rem;box-shadow:0 14px 30px #1f2a440a;margin:.5rem 0 1.1rem}
.week-head{font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;text-align:center;color:var(--muted);font-weight:800}.day{min-height:145px;border:1px solid var(--line);border-radius:14px;padding:9px;background:#fff;margin-bottom:9px;box-shadow:0 4px 12px #1f2a4406}.day.out{background:#f8f9fb;color:#adb2bc}.day.today{border:2px solid #5b7cfa}.num{font-weight:800;font-size:.82rem;margin-bottom:7px}.chip{font-size:.72rem;line-height:1.25;color:#fff;border-radius:7px;padding:5px 6px;margin:4px 0;overflow:hidden}.chip.done{opacity:.45;text-decoration:line-through}
.agenda{background:#fff;border:1px solid var(--line);border-left:5px solid var(--accent);border-radius:14px;padding:13px 14px;margin:8px 0;display:flex;gap:12px}.agenda-date{min-width:52px;text-align:center;color:var(--muted);font-size:.72rem;text-transform:uppercase}.agenda-date b{display:block;color:var(--ink);font-size:1.35rem}.agenda-body{flex:1}.agenda-title{font-weight:800}.agenda-meta{color:var(--muted);font-size:.82rem;margin-top:3px}.empty{padding:35px;border:1px dashed #cfd4df;border-radius:16px;text-align:center;color:var(--muted);background:#fff}
.agenda{background:#fff;border:1px solid var(--line);border-left:5px solid var(--accent);border-radius:14px;padding:13px 14px;margin:8px 0;display:flex;gap:12px}.agenda-date{min-width:52px;text-align:center;color:var(--muted);font-size:.72rem;text-transform:uppercase}.agenda-date b{display:block;color:var(--ink);font-size:1.35rem}.agenda-body{flex:1}.agenda-title{font-weight:800}.agenda-meta{color:var(--muted);font-size:.82rem;margin-top:3px}.progress-card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px 18px;margin:10px 0 14px}.progress-header{display:flex;justify-content:space-between;gap:1rem;align-items:baseline}.progress-title{font-size:1.1rem;font-weight:800}.progress-value{color:var(--muted);font-size:.85rem}.remaining{border-top:1px solid var(--line);margin-top:12px;padding-top:9px}.remaining-row{display:flex;justify-content:space-between;gap:1rem;padding:7px 0;color:var(--ink);font-size:.9rem}.remaining-points{color:var(--muted);white-space:nowrap}.empty{padding:35px;border:1px dashed #cfd4df;border-radius:16px;text-align:center;color:var(--muted);background:#fff}
@media(max-width:720px){.block-container{padding:.8rem .75rem 4rem}.hero h1{font-size:2.25rem}.day{min-height:80px;padding:4px}.chip{font-size:.6rem;padding:3px}.agenda{padding:11px}.stTabs [data-baseweb="tab"]{padding-left:10px;padding-right:10px}}
</style>""",unsafe_allow_html=True)

seed_demo(DB_FILE); items=list_assignments(DB_FILE); today=date.today()
if "show_create" not in st.session_state: st.session_state.show_create=False
if "create_date" not in st.session_state: st.session_state.create_date=date(YEAR,1,15)
if "calendar_month" not in st.session_state: st.session_state.calendar_month=today.month
st.markdown('<div class="hero"><div class="eyebrow">Your semester at a glance</div><h1>Semester Calendar <span style="color:#5b7cfa">2026</span></h1><p>One clear place for every deadline, exam, reading, and project.</p></div>',unsafe_allow_html=True)
create_col, helper_col=st.columns([1.2,5])
with create_col:
    if st.button("＋ Create", type="primary", use_container_width=True):
        st.session_state.show_create = not st.session_state.show_create
with helper_col:
    st.caption("Create an assignment, reminder, event, exam, or quiz in seconds.")
if st.session_state.show_create:
    st.markdown('<div class="create-panel">',unsafe_allow_html=True)
    with st.form("quick_create", clear_on_submit=True):
        kind=st.selectbox("Type",["Assignment","Reminder","Event","Exam","Quiz"],index=0,label_visibility="visible")
        title=st.text_input("Title",placeholder="Final review session")
        course=st.text_input("Course",placeholder="Statistics")
        col_a,col_b=st.columns(2)
        with col_a:
            due=st.date_input("Date",st.session_state.create_date,min_value=date(YEAR,1,1),max_value=date(YEAR,12,31))
            include_time=st.checkbox("Add a time",value=kind in {"Reminder","Event","Exam","Quiz"})
        with col_b:
            due_time=st.time_input("Time",time(9,0),disabled=not include_time)
            priority=st.selectbox("Priority",["High","Medium","Low"],index=1)
        points=st.number_input("Points",min_value=0,step=1,value=10,help="How many points this item contributes to the class.")
        location=st.text_input("Location",placeholder="Library, room 204, Zoom")
        description=st.text_area("Description",placeholder="Add any notes, prep steps, or key details.")
        submit=st.form_submit_button("Save item",type="primary",use_container_width=True)
        if submit:
            if not title.strip():
                st.error("Title is required.")
            else:
                course_name=(course.strip() or kind)
                note_parts=[]
                if description.strip(): note_parts.append(f"Description: {description.strip()}")
                if location.strip(): note_parts.append(f"Location: {location.strip()}")
                save_assignment(DB_FILE,create_assignment(title=title,course=course_name,due_date=due,due_time=due_time if include_time else None,category=kind,priority=priority,notes="\n".join(note_parts),points=points))
                st.success(f"{kind} saved.")
                st.session_state.show_create=False
                st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)
with st.sidebar:
    st.header("View settings")
    query=st.text_input("Search",placeholder="Title, course, or notes")
    all_courses=sorted({x.course for x in items}); courses=st.multiselect("Courses",all_courses,default=all_courses)
    categories=st.multiselect("Types",list(COLORS),default=list(COLORS)); show_done=st.toggle("Show completed",True)
    st.download_button("Export to Apple/Google Calendar",to_ics(items),"studyflow-2026.ics","text/calendar",use_container_width=True)
q=query.lower().strip(); filtered=[x for x in items if (not q or q in f"{x.title} {x.course} {x.notes}".lower()) and x.course in courses and x.category in categories and (show_done or not x.completed)]
open_items=[x for x in items if not x.completed]; upcoming=[x for x in open_items if x.due_date>=today.isoformat()]
metrics=st.columns(3); metrics[0].metric("Open work",len(open_items)); metrics[1].metric("Completed",len(items)-len(open_items)); metrics[2].metric("Next deadline",datetime.strptime(upcoming[0].due_date,"%Y-%m-%d").strftime("%b %d") if upcoming else "All clear")
calendar_tab,progress_tab,agenda_tab,manage_tab,syllabi_tab=st.tabs(["Calendar","Progress","Agenda","Assignments","Syllabi"])
month=st.session_state.calendar_month

def chip(x:Assignment)->str:
    return f'<div class="chip {"done" if x.completed else ""}" style="background:{COLORS.get(x.category,COLORS["Other"])}"><b>{html.escape(x.title)}</b><br>{html.escape(x.due_time or "All day")} · {html.escape(x.course)}</div>'

with calendar_tab:
    previous_col, title_col, next_col=st.columns([0.15,1,0.15])
    with previous_col:
        if st.button("←",key="previous-month",help="View previous month",use_container_width=True):
            st.session_state.calendar_month=12 if month == 1 else month-1
            st.rerun()
    with title_col:
        st.subheader(f"{MONTH_NAMES[month]} {YEAR}")
    with next_col:
        if st.button("→",key="next-month",help="View next month",use_container_width=True):
            st.session_state.calendar_month=1 if month == 12 else month+1
            st.rerun()
    st.caption("On phones, use the Agenda tab for the clearest view.")
    heads=st.columns(7)
    for c,name in zip(heads,["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]): c.markdown(f'<div class="week-head">{name}</div>',unsafe_allow_html=True)
    by_day={}
    for x in filtered: by_day.setdefault(x.due_date,[]).append(x)
    for week in month_weeks(YEAR,month):
        cols=st.columns(7)
        for c,day in zip(cols,week):
            classes="day"+(" out" if day.month!=month else "")+(" today" if day==today else "")
            with c:
                st.markdown(f'<div class="{classes}"><div class="num">{day.day}</div>{"".join(chip(x) for x in by_day.get(day.isoformat(),[]))}</div>',unsafe_allow_html=True)
                if st.button("＋ Add",key=f"add-{day.isoformat()}",use_container_width=True,help=f"Add an item on {day.strftime('%B %d, %Y')}"):
                    st.session_state.create_date=day
                    st.session_state.show_create=True
                    st.rerun()
with progress_tab:
    st.subheader("Class progress")
    st.caption("Completed point values count toward each class total. Add points to new items to keep this view accurate.")
    courses_for_progress=sorted({x.course for x in items})
    if not courses_for_progress:
        st.markdown('<div class="empty">No assignments yet. Create one to start tracking progress.</div>',unsafe_allow_html=True)
    for course_name in courses_for_progress:
        course_items=[x for x in items if x.course == course_name]
        total_points=sum(x.points for x in course_items)
        completed_points=sum(x.points for x in course_items if x.completed)
        remaining=[x for x in course_items if not x.completed]
        ratio=completed_points/total_points if total_points else 0
        st.markdown('<div class="progress-card">',unsafe_allow_html=True)
        header_left,header_right=st.columns([2,1])
        with header_left: st.markdown(f'<div class="progress-header"><div class="progress-title">{html.escape(course_name)}</div></div>',unsafe_allow_html=True)
        with header_right: st.markdown(f'<div class="progress-value" style="text-align:right">{completed_points:g} / {total_points:g} points · {ratio:.0%}</div>',unsafe_allow_html=True)
        st.progress(ratio)
        if remaining:
            st.markdown('<div class="remaining">',unsafe_allow_html=True)
            for item in sorted(remaining,key=lambda x:(x.due_date,x.title)):
                st.markdown(f'<div class="remaining-row"><span>{html.escape(item.title)}</span><span class="remaining-points">{item.points:g} points · {item.due_date}</span></div>',unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)
        else:
            st.caption("Everything is complete.")
        st.markdown('</div>',unsafe_allow_html=True)
with agenda_tab:
    st.subheader("Upcoming agenda"); agenda=[x for x in filtered if x.due_date>=today.isoformat()]
    if not agenda: st.markdown('<div class="empty">No upcoming work matches your filters.</div>',unsafe_allow_html=True)
    for x in agenda:
        d=date.fromisoformat(x.due_date)
        st.markdown(f'<div class="agenda" style="--accent:{COLORS.get(x.category,COLORS["Other"])}"><div class="agenda-date">{d.strftime("%b")}<b>{d.day}</b>{d.strftime("%a")}</div><div class="agenda-body"><div class="agenda-title">{html.escape(x.title)}</div><div class="agenda-meta">{html.escape(x.course)} · {x.category} · {html.escape(x.due_time or "All day")} · {x.priority} priority</div></div></div>',unsafe_allow_html=True)
with manage_tab:
    form_col,list_col=st.columns([1,1.45],gap="large")
    with form_col:
        st.subheader("Add assignment")
        with st.form("new",clear_on_submit=True):
            title=st.text_input("Title",placeholder="Research paper outline"); course=st.text_input("Course",placeholder="English 210")
            due=st.date_input("Due date",date(YEAR,1,15),min_value=date(YEAR,1,1),max_value=date(YEAR,12,31)); timed=st.checkbox("Include due time"); due_time=st.time_input("Due time",time(23,59),disabled=not timed)
            category=st.selectbox("Type",list(COLORS)); priority=st.selectbox("Priority",["High","Medium","Low"],index=1); points=st.number_input("Points",min_value=0,step=1,value=10); notes=st.text_area("Notes",placeholder="Reading pages, submission link, reminders…")
            if st.form_submit_button("Add to calendar",type="primary",use_container_width=True):
                if title.strip() and course.strip(): save_assignment(DB_FILE,create_assignment(title=title,course=course,due_date=due,due_time=due_time if timed else None,category=category,priority=priority,notes=notes,points=points)); st.rerun()
                else: st.error("Title and course are required.")
    with list_col:
        st.subheader("Manage work")
        for x in filtered:
            with st.expander(f"{'✓ ' if x.completed else ''}{x.due_date} — {x.title}"):
                st.caption(f"{x.course} · {x.category} · {x.priority} priority")
                if x.notes: st.write(x.notes)
                a,b=st.columns(2)
                if a.button("Reopen" if x.completed else "Complete",key=f"done-{x.id}",use_container_width=True): update_assignment(DB_FILE,x.id,completed=not x.completed); st.rerun()
                if b.button("Delete",key=f"delete-{x.id}",use_container_width=True): delete_assignment(DB_FILE,x.id); st.rerun()
with syllabi_tab:
    st.subheader("Syllabus inbox"); st.write("Store syllabi here. Automatic extraction and a review screen will be connected when you add the real documents.")
    uploads=st.file_uploader("Upload PDF, DOCX, or TXT",type=["pdf","docx","txt"],accept_multiple_files=True)
    if st.button("Save uploaded syllabi",type="primary",disabled=not uploads):
        for upload in uploads: save_syllabus(DB_FILE,upload.name,upload.getvalue())
        st.success(f"Saved {len(uploads)} file(s)."); st.rerun()
    saved=list_syllabi(DB_FILE)
    if saved: st.dataframe([{"File":x["filename"],"Uploaded":x["uploaded_at"],"Status":x["status"]} for x in saved],hide_index=True,use_container_width=True)
    else: st.info("No syllabi uploaded yet.")
