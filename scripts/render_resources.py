"""Regenerate the human-readable source index from sources.json."""
import json
import os
import re
from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[1]
    curriculum = json.loads((root / "curriculum.json").read_text(encoding="utf-8"))
    sources = json.loads((root / "docs/sources.json").read_text(encoding="utf-8"))
    reader_numbers = {module["id"]: module["reader_number"] for module in curriculum["modules"]}
    def reader_text(value):
        return re.sub(r"M0[1-9]", lambda m: "第" + str(reader_numbers[m.group(0)]) + "章", value)
    destination = root / "学习指南/资料库.md"
    lines = ["# 需要更多资料时再来这里", "", "[回到课程首页](../README.md)", "",
             "第一次学习以章节开头指定的资料为准。这里按九章整理50项官方论文、课程与文档，用于继续阅读和查漏。阅读时间仅为估计，与章节总课时有重叠。",
             "", "每个章节正文说明具体读哪一部分；不用先把整份资料库读完。来源核验日期：2026-10-11。", ""]
    for module in curriculum["modules"]:
        relative = os.path.relpath(root / module["path"], destination.parent).replace("\\", "/")
        lines.extend(["## 第" + str(module["reader_number"]) + "章：" + module["title"], "",
                      "[回到这一章](" + relative + ")，按正文给出的顺序与范围阅读。", "",
                      "| 资料 | 用途 | 阅读层次 | 约小时 |",
                      "|---|---|---|---:|"])
        for source in sources:
            if module["id"] in source["modules"]:
                lines.append("| [" + source["title"].replace("|", "/") + "](" + source["url"] + ") | " +
                             reader_text(source["why"]).replace("|", "/") + " | " + ("随章节阅读" if source["required"] else "深入时选读") +
                             " | " + str(source["estimated_hours"]) + " |")
        lines.append("")
    lines.extend(["<details>", "<summary>需要核对来源时：页面核验记录</summary>", "",
                  "页面与摘要核验、全文阅读、实际运行是不同层级。以下说明保留访问限制，不宣称已经复现论文性能。", "",
                  "| 资料 | 实际核验范围 |", "|---|---|"])
    for source in sources:
        lines.append("| " + source["title"].replace("|", "/") + " | " + source["verified_note"].replace("|", "/").replace("\n", " ") + " |")
    lines.extend(["", "原始来源记录：[sources.json](../docs/sources.json)。", "", "</details>"])
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("Rendered source index:", len(sources))

if __name__ == "__main__":
    main()
