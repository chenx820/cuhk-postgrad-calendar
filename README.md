# CUHK Postgrad Calendar

香港中文大学（沙田）研究生校历的非官方 `.ics` 日历包，可导入 Apple 日历及其他支持 iCalendar 的应用。

目前提供 **2026–27 学年**，覆盖 2026 年 8 月至 2027 年 8 月。日期来自研究生院通用校历，**尚未按具体项目匹配**；请先核对学院项目表，项目安排有差异时以项目通知为准。

## 选择日历

| 文件 | 内容 | 事件数 |
| --- | --- | ---: |
| [公共日期](calendars/2026-27/01-common.ics) | 选课、农历新年校假期、公众假期及大学大会 | 20 |
| [两学期制](calendars/2026-27/02-select-one-term-system/2-term.ics) | 学期起止、加退选期，含暑期 | 9 |
| [三学期制 A](calendars/2026-27/02-select-one-term-system/3-term-A.ics) | 学期起止、加退选期，含暑期 | 12 |
| [三学期制 B](calendars/2026-27/02-select-one-term-system/3-term-B.ics) | 学期起止、加退选期，含暑期 | 12 |
| [四学期制](calendars/2026-27/02-select-one-term-system/4-term.ics) | 学期起止及加退选期 | 12 |
| [博士／研究式研究生（可选）](calendars/2026-27/03-optional-research-doctoral.ics) | 最终论文提交截止及学位颁授日期 | 7 |

**四种学期制度只选适用的一份。** 尚未确认项目时，可先导入公共日期。授课型硕士通常无需导入论文与学位文件；研究式学生仍须核对内部提交期限和毕业要求。

## 导入 Apple 日历

1. 点击仓库页面的 **Code → Download ZIP** 并解压，或下载所需 `.ics` 文件。
2. Mac 打开「日历」，选择「文件 → 新建日历 → iCloud」，创建专用的 CUHK 日历。
3. 选择「文件 → 导入」，导入公共日期及一份适用的学期文件；按需要加入研究式研究生文件。
4. Mac 和 iPhone 使用同一 Apple 账户并开启 iCloud 日历同步，即可在 iPhone 查看。

导入属于一次性复制，**不会随学校修订自动更新**。重复导入可能产生重复事件；建议将个人课表放在其他日历中，方便单独替换本包。若已启用香港节假日日历，公众假期也可能重复显示。

如需订阅，可使用 GitHub 对应 `.ics` 文件的 Raw HTTPS 地址添加订阅日历。订阅只会读取本仓库文件的更新，仍需维护者手动核对学校修订并更新文件。

## 具体课程示例

`courses/2026-27/term-1/` 提供按 CUSIS 课表生成的课程示例，用来演示如何添加自己的课程，并不是完整或持续维护的官方课程目录。课程以 CUSIS 列出的完整 **Meeting Dates** 为准，不使用首次和最后一次上课日期推算，因此停课周不会被错误加入。

目前包括：

- [AIST 5040](courses/2026-27/term-1/AIST5040.ics)：13 次 lecture。
- [CENG 5280](courses/2026-27/term-1/CENG5280.ics)：13 次 lecture 和 13 次 tutorial。
- [全部课程](courses/2026-27/term-1/all-courses.ics)：以上课程合并，共 39 次课堂。导入此文件后无需再导入单科文件。

课程数据保存在 [courses.json](courses/2026-27/term-1/courses.json)。每个课堂组件分别记录 `class_number`、`section`、`meeting_dates`、起止时间和教室。要制作自己的课表，可复制这个 JSON 结构并替换其中的数据，然后运行：

```sh
python3 courses/2026-27/term-1/make_courses.py
```

生成的课程事件使用香港时区并占用日历忙碌时间。本仓库不设置提醒；可以在 Apple 日历导入后自行添加。

## 数据与维护

- 校历文件为全天事件；具体课程文件包含上课时间和教室。本仓库不包含个人考试时间或提醒。学期开始和结束各为单日标记；日期范围包含首尾。
- [dates.json](calendars/2026-27/dates.json) 保存结构化日期，[manifest.json](calendars/2026-27/manifest.json) 列出生成文件与事件数。
- 修改日期后，在仓库根目录运行以下命令（仅需 Python 3 标准库）：

```sh
python3 calendars/2026-27/make_calendars.py
```

生成器使用 UTF-8、CRLF、稳定事件 UID 及 iCalendar 折行规则；全天事件的 `DTEND` 写为最后一天的下一天。修改订阅源中已有事件时，需保留 UID，并相应维护 `SEQUENCE` 和更新时间。当前生成器面向 2026–27 学年，新学年应另建目录并更新生成器中的学年标识。

## 官方来源

- [CUHK 研究生院 Academic Calendar（含各学院项目表）](https://www.gs.cuhk.edu.hk/academics/calendar)
- [University Almanac 2026–27 官方 PDF](https://www.gs.cuhk.edu.hk/download/UniversityAlmanac202627.pdf.pdf)：版本日期 2026-05-26，本包核对日期 2026-09-08。
- [Apple：在 Mac 上导入或导出日历](https://support.apple.com/zh-cn/guide/calendar/-icl1023/mac)
- [Apple：在 iCloud 中添加日历订阅](https://support.apple.com/zh-cn/102301)
- [RFC 5545：iCalendar](https://www.rfc-editor.org/rfc/rfc5545.html)

官方 PDF 第三页将三学期制 A 的第二学期结束日 2027-04-10 误标为星期一；第一页日期表标为星期六，两处日期一致。本包采用 2027-04-10（星期六）。

本项目并非 CUHK 官方发布，也未获学校认可或背书。学校发布的最新校历及项目通知优先。
