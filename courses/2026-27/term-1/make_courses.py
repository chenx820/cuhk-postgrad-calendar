"""Generate exact-date course calendars from courses.json using Python 3."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import UUID, uuid5


ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "courses.json").read_text(encoding="utf-8"))
NAMESPACE = UUID("b18bdcac-01ec-428d-8c35-a17193d879c8")
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def escape(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )


def fold(line: str) -> str:
    """Fold an iCalendar line without splitting a UTF-8 character."""
    result: list[str] = []
    current = ""
    for char in line:
        if len((current + char).encode("utf-8")) > 75:
            result.append(current)
            current = " "
        current += char
    return "\r\n".join(result + [current])


def compact_date_time(day: str, clock: str) -> str:
    parsed = datetime.fromisoformat(f"{day}T{clock}")
    return parsed.strftime("%Y%m%dT%H%M%S")


def course_events(course: dict) -> list[dict]:
    events = []
    for component in course["components"]:
        meeting_dates = component["meeting_dates"]
        if not meeting_dates:
            raise ValueError(f"{course['code']} {component['section']} has no meeting_dates")
        if meeting_dates != sorted(set(meeting_dates)):
            raise ValueError(
                f"{course['code']} {component['section']} meeting_dates must be unique and sorted"
            )
        for day in meeting_dates:
            date.fromisoformat(day)
            start = datetime.fromisoformat(f"{day}T{component['start_time']}")
            end = datetime.fromisoformat(f"{day}T{component['end_time']}")
            if start >= end:
                raise ValueError(f"Invalid time range for {course['code']} on {day}")
            events.append(
                {
                    "uid_key": "/".join(
                        [
                            DATA["academic_year"],
                            DATA["term"],
                            course["code"],
                            component["class_number"],
                            day,
                        ]
                    ),
                    "summary": f"{course['code']} {component['section']}｜{course['title']}",
                    "day": day,
                    "start_time": component["start_time"],
                    "end_time": component["end_time"],
                    "location": component["room"],
                    "description": (
                        "Example course calendar generated from exact CUSIS Meeting Dates.\n"
                        f"Course: {course['code']} {course['title']}\n"
                        f"Class: {component['class_number']}\n"
                        f"Section: {component['section']}\n"
                        f"Meeting Date: {day}\n"
                        "Source: CUSIS meeting information supplied by the student."
                    ),
                    "categories": f"CUHK,{course['code']},{component['section']}",
                }
            )
    return events


def write_calendar(path: Path, calendar_name: str, events: list[dict]) -> None:
    timezone_name = DATA["timezone"]
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Personal Calendar//CUHK Courses//EN",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:{escape(calendar_name)}",
        f"X-WR-TIMEZONE:{timezone_name}",
        f"X-WR-CALDESC:{escape(DATA['purpose'])}",
        "BEGIN:VTIMEZONE",
        f"TZID:{timezone_name}",
        "BEGIN:STANDARD",
        "DTSTART:19700101T000000",
        "TZOFFSETFROM:+0800",
        "TZOFFSETTO:+0800",
        "TZNAME:HKT",
        "END:STANDARD",
        "END:VTIMEZONE",
    ]
    for event in sorted(events, key=lambda item: (item["day"], item["start_time"], item["summary"])):
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uuid5(NAMESPACE, event['uid_key'])}",
                f"DTSTAMP:{STAMP}",
                f"DTSTART;TZID={timezone_name}:{compact_date_time(event['day'], event['start_time'])}",
                f"DTEND;TZID={timezone_name}:{compact_date_time(event['day'], event['end_time'])}",
                f"SUMMARY:{escape(event['summary'])}",
                f"LOCATION:{escape(event['location'])}",
                f"DESCRIPTION:{escape(event['description'])}",
                f"CATEGORIES:{escape(event['categories'])}",
                "STATUS:CONFIRMED",
                "TRANSP:OPAQUE",
                "SEQUENCE:0",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    path.write_bytes(("\r\n".join(fold(line) for line in lines) + "\r\n").encode("utf-8"))


manifest = []
all_events = []
for course in DATA["courses"]:
    events = course_events(course)
    all_events.extend(events)
    filename = course["code"].replace(" ", "") + ".ics"
    write_calendar(ROOT / filename, f"CUHK Example｜{course['code']}｜{DATA['term']}", events)
    manifest.append({"file": filename, "meetings": len(events), "course": course["code"]})

write_calendar(
    ROOT / "all-courses.ics",
    f"CUHK Example Courses｜{DATA['term']} {DATA['academic_year']}",
    all_events,
)
manifest.append({"file": "all-courses.ics", "meetings": len(all_events), "course": "ALL"})
(ROOT / "manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
for item in manifest:
    print(item["file"], item["meetings"], "meetings")
