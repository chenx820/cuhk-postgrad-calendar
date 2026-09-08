"""Edit dates.json, then run: python3 make_calendars.py"""
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid5

ROOT = Path(__file__).resolve().parent
D = json.loads((ROOT / "dates.json").read_text(encoding="utf-8"))
SOURCE = D["source"]
NAMESPACE = UUID("114dcfc6-d085-4732-ad04-7b63066b7f9d")
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def escape(value):
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace(";", "\\;").replace(",", "\\,")

def fold(line):
    # RFC 5545: max 75 octets per physical line; never split a UTF-8 character.
    lines, current = [], ""
    for char in line:
        if len((current + char).encode("utf-8")) > 75:
            lines.append(current)
            current = " "
        current += char
    return "\r\n".join(lines + [current])

def event(key, title, start, end, note, category):
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    assert first <= last
    description = (note + "\n日期范围：" + start + " 至 " + end + "（含首尾）。"
        + "\n非官方整理；官方校历版本：" + D["source_updated"]
        + "；核对日期：" + D["checked_on"] + "。\n来源：" + SOURCE)
    return {"key": key, "summary": "CUHK｜" + title, "start": first,
        "end": last + timedelta(days=1), "description": description, "category": category}

manifest = []
def write_calendar(relative_path, name, events):
    events = sorted(events, key=lambda e: (e["start"], e["summary"]))
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Personal Calendar//CUHK PG 2026-27//ZH",
        "CALSCALE:GREGORIAN", "X-WR-CALNAME:" + escape(name), "X-WR-TIMEZONE:Asia/Hong_Kong",
        "X-WR-CALDESC:" + escape("非官方整理；具体项目日期以 CUHK 研究生院及项目通知为准。")]
    for e in events:
        uid = str(uuid5(NAMESPACE, "cuhk-pg-2026-27/" + e["key"]))
        lines.extend(["BEGIN:VEVENT", "UID:" + uid, "DTSTAMP:" + STAMP,
            "DTSTART;VALUE=DATE:" + e["start"].strftime("%Y%m%d"),
            "DTEND;VALUE=DATE:" + e["end"].strftime("%Y%m%d"),
            "SUMMARY:" + escape(e["summary"]), "DESCRIPTION:" + escape(e["description"]),
            "CATEGORIES:" + escape(e["category"]), "URL:" + SOURCE,
            "TRANSP:TRANSPARENT", "SEQUENCE:0", "END:VEVENT"])
    lines.append("END:VCALENDAR")
    target = ROOT / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(("\r\n".join(fold(line) for line in lines) + "\r\n").encode("utf-8"))
    manifest.append({"file": relative_path, "events": len(events), "calendar": name})

common = [event(key, title, first, last, note, "校历")
    for key, title, first, last, note in D["common"]]
common.extend(event("holiday/" + day, title, day, day,
    "研究生官方校历列明的公众假期；大学假期不安排课堂。", "公众假期")
    for day, title in D["holidays"])
write_calendar("01-common.ics", "CUHK 研究生 2026–27｜公共日期", common)

for system, item in D["term_systems"].items():
    events = []
    for number, (term, first, last, add_first, add_last, grade) in enumerate(item["terms"], 1):
        base = system + "/" + str(number)
        note = ("适用：研究生通用" + item["label"] + "。学期：" + first + " 至 " + last
            + "。部分项目另有日期，需先核对具体项目。个人课程及考试安排以项目通知为准。")
        if term == "暑期学期":
            note += "暑期是否修课由项目及个人选课决定。"
        events.extend([
            event(base + "/start", term + "开始（" + item["label"] + "）", first, first, note, "学期"),
            event(base + "/end", term + "结束（" + item["label"] + "）", last, last, note, "学期"),
            event(base + "/add-drop", term + "加退选（" + item["label"] + "）", add_first, add_last,
                note + "加退选包含最后一天；具体截止时刻以 CUSIS 或项目通知为准。", "选课"),
        ])
    write_calendar("02-select-one-term-system/" + system + ".ics",
        "CUHK 研究生 2026–27｜" + item["label"], events)

research = []
for deadline, conferment in D["research_cycles"]:
    note = ("仅适用于博士及研究式研究生。最终论文/作品集须送达研究生院；对应颁授学位日期："
        + conferment + "。还须完成毕业要求并获教务会批准；学部可能有更早的内部截止日期。")
    research.append(event("thesis/" + deadline, "最终论文提交截止（博士／研究式）", deadline, deadline, note, "论文"))
    if conferment <= "2027-08-31":
        research.append(event("degree/" + conferment, "颁授学位日期（博士／研究式）", conferment, conferment,
            note + "此为学位颁授日期，具体典礼安排另行通知。", "学位"))
write_calendar("03-optional-research-doctoral.ics", "CUHK 2026–27｜论文与学位（可选）", research)
(ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for entry in manifest:
    print(entry["file"], entry["events"], "events")
