"""Regenerate the human-readable source index from sources.json."""
import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[1]
    curriculum = json.loads((root / "curriculum.json").read_text(encoding="utf-8"))
    sources = json.loads((root / "docs/sources.json").read_text(encoding="utf-8"))
    lines = ["# 官方资料与必读索引", "",
             "按模块使用，先完成必读指定章节，再决定是否选读。以下时间是阅读估计，与总课时有重叠，不逐项累加。核验说明区分页面/摘要、全文与运行；未做真实模型实验。",
             "", "原始记录：[sources.json](sources.json)。来源核验日期：2026-10-11。", ""]
    for module in curriculum["modules"]:
        lines.extend(["## " + module["id"] + " " + module["title"], "",
                      "[进入模块](" + module["path"].replace("docs/", "") + ")，按模块里的顺序与章节范围阅读。", "",
                      "| 编号 | 必读/选读 | 官方资料 | 约小时 | 为什么读 |",
                      "|---|---|---|---:|---|"])
        for source in sources:
            if module["id"] in source["modules"]:
                lines.append("| " + source["id"] + " | " + ("必读" if source["required"] else "选读") +
                             " | [" + source["title"].replace("|", "/") + "](" + source["url"] + ") | " +
                             str(source["estimated_hours"]) + " | " + source["why"].replace("|", "/") + " |")
        lines.append("")
    lines.extend(["## 核验边界", "", "| 编号 | 核验说明 |", "|---|---|"])
    for source in sources:
        lines.append("| " + source["id"] + " | " + source["verified_note"].replace("|", "/").replace("\n", " ") + " |")
    (root / "docs/RESOURCES.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("Rendered source index:", len(sources))

if __name__ == "__main__":
    main()
